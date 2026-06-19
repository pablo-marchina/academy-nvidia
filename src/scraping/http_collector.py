"""Real HTTP collector governed by Source Registry and Decision Calibration.

Only consumes production_enabled=true sources. Respects compliance rules,
robots.txt, rate limits, and calibrated decisions for timeout/retry/backoff.

No mock, no fake, no stub in the productive path.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from datetime import UTC, datetime
from statistics import median
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from src.quality.decision_calibration_registry import (
    get_project_decision_inventory,
    validate_decision_for_production,
)
from src.scraping.fetcher import fetch_page
from src.scraping.parser import extract_clean_text
from src.scraping.rate_limit_policy import get_rate_limit_policy
from src.scraping.source_registry import SourceRecord, list_production_enabled_sources

logger = logging.getLogger(__name__)

_HTTP_COLLECTOR_USER_AGENT = (
    "Mozilla/5.0 (compatible; NVIDIAStartupAIRadar-HttpCollector/0.1; "
    "+https://github.com/nvidia/startup-ai-radar)"
)

# ── Calibration Decision IDs ─────────────────────────────────────────────

DECISION_HTTP_TIMEOUT = "collection.http_timeout_seconds"
DECISION_HTTP_MAX_RETRIES = "collection.http_max_retries"
DECISION_HTTP_BACKOFF_BASE = "collection.http_backoff_base_seconds"

_CALIBRATION_DECISIONS: list[tuple[str, str]] = [
    (DECISION_HTTP_TIMEOUT, "timeout_seconds"),
    (DECISION_HTTP_MAX_RETRIES, "max_retries"),
    (DECISION_HTTP_BACKOFF_BASE, "backoff_base_seconds"),
]

# ── Pydantic Models ──────────────────────────────────────────────────────


class ComplianceResult(BaseModel):
    passed: bool
    blockers: list[str] = Field(default_factory=list)
    robots_allowed: bool = True
    robots_checked: bool = False


class SourceFetchResult(BaseModel):
    source_id: str
    source_url: str
    status: str = "pending"
    http_status_code: int | None = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    content_hash: str | None = None
    raw_html: str = ""
    raw_text: str = ""
    extracted_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message_sanitized: str | None = None
    compliance_status: str | None = None
    robots_allowed: bool = True
    latency_ms: int = 0
    content_bytes: int = 0
    extraction_status: str = "not_configured"


class CollectionMetrics(BaseModel):
    attempted_sources_count: int = 0
    fetched_sources_count: int = 0
    blocked_sources_count: int = 0
    failed_sources_count: int = 0
    robots_blocked_count: int = 0
    compliance_blocked_count: int = 0
    duplicate_count: int = 0
    total_latency_ms: int = 0
    median_latency_ms: float = 0.0
    total_content_bytes: int = 0
    extraction_success_rate: float = 0.0
    fetch_success_rate: float = 0.0


class CollectionRequest(BaseModel):
    run_id: str
    source_records: list[SourceRecord]
    calibrated_limits: dict[str, Any] = Field(default_factory=dict)
    user_agent: str | None = None
    dry_run: bool = False

    model_config = {"arbitrary_types_allowed": True}


class CollectionResult(BaseModel):
    run_id: str
    request: CollectionRequest
    sources: list[SourceFetchResult] = Field(default_factory=list)
    metrics: CollectionMetrics = Field(default_factory=CollectionMetrics)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None


# ── Robots Checker ───────────────────────────────────────────────────────


class RobotsChecker:
    """Simple robots.txt parser supporting User-agent, Disallow, Allow, Crawl-delay.

    Longest-matching-path wins (most specific rule). Allow overrides
    Disallow at equal path length. Supports ``*`` wildcard in path.
    """

    _Rule = tuple[re.Pattern[str], int, bool]  # (regex, raw_path_len, is_allow)

    def __init__(self, robots_txt: str = "", user_agent: str = "*") -> None:
        self._rules: list[RobotsChecker._Rule] = []
        self._crawl_delay: float = 0.0
        self._parsed: bool = False
        if robots_txt:
            self._parse(robots_txt, user_agent)

    def _parse(self, robots_txt: str, user_agent: str) -> None:
        self._parsed = True
        current_agents: list[str] = []
        for line in robots_txt.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lower = line.lower()
            if lower.startswith("user-agent:"):
                agent = line.split(":", 1)[1].strip()
                current_agents = [agent]
            elif lower.startswith("disallow:"):
                path = self._extract_path(line)
                if self._matches_agent(current_agents, user_agent):
                    self._rules.append((self._path_to_regex(path), len(path), False))
            elif lower.startswith("allow:"):
                path = self._extract_path(line)
                if self._matches_agent(current_agents, user_agent):
                    self._rules.append((self._path_to_regex(path), len(path), True))
            elif lower.startswith("crawl-delay:"):
                if self._matches_agent(current_agents, user_agent):
                    try:
                        self._crawl_delay = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        pass

    @staticmethod
    def _extract_path(line: str) -> str:
        parts = line.split(":", 1)
        return parts[1].strip() if len(parts) > 1 else ""

    @staticmethod
    def _path_to_regex(path: str) -> re.Pattern[str]:
        escaped = re.escape(path)
        wildcard_replaced = escaped.replace(r"\*", ".*")
        return re.compile(f"^{wildcard_replaced}")

    @staticmethod
    def _matches_agent(current_agents: list[str], target: str) -> bool:
        return any(a == "*" or a.lower() == target.lower() for a in current_agents)

    def is_allowed(self, url: str) -> bool:
        path = urlparse(url).path or "/"
        if not self._parsed:
            return True
        best_len = -1
        best_is_allow = True
        for pattern, raw_len, is_allow in self._rules:
            if pattern.search(path):
                if raw_len > best_len:
                    best_len = raw_len
                    best_is_allow = is_allow
                elif raw_len == best_len and is_allow and not best_is_allow:
                    best_is_allow = True
        return best_is_allow

    @property
    def crawl_delay(self) -> float:
        return self._crawl_delay

    @property
    def parsed(self) -> bool:
        return self._parsed


# ── Content Hashing ──────────────────────────────────────────────────────


def _compute_content_hash(raw: str | bytes) -> str:
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# ── Calibration Lookup ───────────────────────────────────────────────────


def _lookup_calibrated_value(
    decision_id: str,
    inventory: list,
) -> tuple[Any, bool, str]:
    """Look up a decision from Decision Calibration Registry.

    Returns (value, is_blocked, block_reason).
    """
    for rec in inventory:
        if rec.decision_id == decision_id:
            result = validate_decision_for_production(rec)
            if not result.passed:
                return None, True, f"{decision_id}: {'; '.join(result.reasons)}"
            return rec.current_value, False, ""
    return None, True, f"{decision_id}: not registered in Decision Calibration Registry"


def _resolve_calibrated_limits(
    request: CollectionRequest,
) -> tuple[dict[str, Any], list[str]]:
    """Resolve timeout/retry/backoff from request.calibrated_limits or registry.

    Returns (limits_dict, blockers_list).
    """
    limits: dict[str, Any] = {}
    blockers: list[str] = []
    inventory = get_project_decision_inventory()

    for decision_id, key in _CALIBRATION_DECISIONS:
        if key in request.calibrated_limits:
            limits[key] = request.calibrated_limits[key]
        else:
            value, blocked, reason = _lookup_calibrated_value(decision_id, inventory)
            if blocked:
                blockers.append(reason)
            else:
                limits[key] = value

    return limits, blockers


# ── Source Compliance ────────────────────────────────────────────────────


def _validate_source(source: SourceRecord) -> ComplianceResult:
    """Run compliance checks against a source record.

    Mirrors SourceRegistry's _apply_production_blockers but as a
    collector-level gate.
    """
    blockers: list[str] = []

    if not source.production_enabled:
        blockers.append("source_not_production_enabled")
    if source.requires_login:
        blockers.append("source_requires_login")
    if source.paywall_risk == "mandatory":
        blockers.append("source_paywall_mandatory")
    if source.calibrated_priority_score is None:
        blockers.append("source_priority_uncalibrated")
    if not source.robots_required:
        blockers.append("source_robots_not_defined")
    policy = get_rate_limit_policy(source.rate_limit_policy_id)
    if policy is None:
        blockers.append("rate_limit_policy_not_found")

    passed = len(blockers) == 0
    return ComplianceResult(passed=passed, blockers=blockers, robots_allowed=source.robots_required)


# ── HTTP Source Collector ────────────────────────────────────────────────


class HttpSourceCollector:
    """Real HTTP collector governed by Source Registry and Decision Calibration.

    Only collects from production_enabled sources. Each source is validated
    for compliance, robots.txt, rate limits, and calibrated timeout/retry/backoff.
    """

    def __init__(self, user_agent: str | None = None) -> None:
        self._user_agent = user_agent or _HTTP_COLLECTOR_USER_AGENT
        self._seen_hashes: set[str] = set()

    def collect(self, request: CollectionRequest) -> CollectionResult:
        started_at = datetime.now(UTC)
        self._seen_hashes.clear()

        result = CollectionResult(run_id=request.run_id, request=request, started_at=started_at)

        limits, blockers = _resolve_calibrated_limits(request)

        if blockers and not request.dry_run:
            for source in request.source_records:
                result.sources.append(
                    SourceFetchResult(
                        source_id=source.source_id,
                        source_url=source.base_url,
                        status="blocked",
                        compliance_status="calibration_blocked",
                        error_code="calibration_blocked",
                        error_message_sanitized="; ".join(blockers),
                    )
                )
            result.metrics = self._compute_metrics(result.sources)
            result.finished_at = datetime.now(UTC)
            return result

        timeout_s = float(limits.get("timeout_seconds", 15))
        max_retries = int(limits.get("max_retries", 3))
        backoff_base = float(limits.get("backoff_base_seconds", 2.0))

        policy_limiters: dict[str, float] = {}

        for source in request.source_records:
            sfr = self._collect_one(
                source=source,
                timeout_s=timeout_s,
                max_retries=max_retries,
                backoff_base=backoff_base,
                dry_run=request.dry_run,
                policy_limiters=policy_limiters,
            )
            result.sources.append(sfr)

        result.metrics = self._compute_metrics(result.sources)
        result.finished_at = datetime.now(UTC)
        return result

    def _collect_one(
        self,
        source: SourceRecord,
        timeout_s: float,
        max_retries: int,
        backoff_base: float,
        dry_run: bool,
        policy_limiters: dict[str, float],
    ) -> SourceFetchResult:
        url = (source.base_url or "").strip()
        if not url:
            return SourceFetchResult(
                source_id=source.source_id,
                source_url="",
                status="skipped",
                error_code="no_base_url",
                error_message_sanitized="Source has no base_url configured",
            )

        # 1. Compliance
        compliance = _validate_source(source)
        if not compliance.passed:
            return SourceFetchResult(
                source_id=source.source_id,
                source_url=url,
                status="blocked",
                compliance_status="compliance_blocked",
                error_code="compliance_blocked",
                error_message_sanitized="; ".join(compliance.blockers),
                robots_allowed=compliance.robots_allowed,
            )

        # 2. Robots check
        robots_checker = self._fetch_robots_txt(url, timeout_s)
        if robots_checker.parsed and not robots_checker.is_allowed(url):
            return SourceFetchResult(
                source_id=source.source_id,
                source_url=url,
                status="blocked",
                compliance_status="robots_blocked",
                error_code="robots_disallowed",
                error_message_sanitized="Disallowed by robots.txt",
                robots_allowed=False,
            )

        # 3. Dry run
        if dry_run:
            return SourceFetchResult(
                source_id=source.source_id,
                source_url=url,
                status="dry_run",
                compliance_status="dry_run",
                robots_allowed=robots_checker.is_allowed(url),
            )

        # 4. Fetch with rate limiting and retry
        policy = get_rate_limit_policy(source.rate_limit_policy_id)
        if policy is None:
            return SourceFetchResult(
                source_id=source.source_id,
                source_url=url,
                status="blocked",
                error_code="rate_limit_policy_not_found",
                error_message_sanitized=(
                    f"Rate limit policy '{source.rate_limit_policy_id}' not found"
                ),
            )

        last_error_msg: str | None = None
        last_http_status: int | None = None
        last_latency: int = 0
        fetched_at = datetime.now(UTC)

        for attempt in range(1, max_retries + 1):
            rps = policy.requests_per_second
            self._rate_limit_wait(source.rate_limit_policy_id, rps, policy_limiters)

            start = time.time()
            fr = fetch_page(url, timeout=int(timeout_s))
            elapsed_ms = int((time.time() - start) * 1000)
            last_latency = elapsed_ms
            fetched_at = fr.fetched_at

            if fr.status is not None and fr.status < 400:
                content_hash = _compute_content_hash(fr.raw_html)
                is_duplicate = content_hash in self._seen_hashes
                self._seen_hashes.add(content_hash)

                extracted: str | None = None
                extraction_status = "not_configured"
                try:
                    extracted_val = extract_clean_text(fr.raw_html)
                    if extracted_val.strip():
                        extracted = extracted_val
                        extraction_status = "success"
                    else:
                        extraction_status = "empty"
                except Exception:
                    extraction_status = "failed"

                if is_duplicate:
                    extraction_status = "duplicate_skipped"

                return SourceFetchResult(
                    source_id=source.source_id,
                    source_url=url,
                    status="duplicate" if is_duplicate else "fetched",
                    http_status_code=fr.status,
                    fetched_at=fetched_at,
                    content_hash=content_hash,
                    raw_html="" if is_duplicate else fr.raw_html,
                    raw_text="" if is_duplicate else fr.raw_html,
                    extracted_text=extracted,
                    metadata={
                        "source_category": source.source_category,
                        "source_name": source.source_name,
                        "source_id": source.source_id,
                    },
                    compliance_status="compliant",
                    robots_allowed=robots_checker.is_allowed(url),
                    latency_ms=elapsed_ms,
                    content_bytes=len(fr.raw_html.encode("utf-8")) if not is_duplicate else 0,
                    extraction_status=extraction_status,
                )

            last_http_status = fr.status

            if fr.status is not None and 400 <= fr.status < 500:
                last_error_msg = f"HTTP {fr.status}"
                break

            if fr.status is not None and fr.status >= 500:
                last_error_msg = f"HTTP {fr.status} (attempt {attempt})"
                if attempt < max_retries:
                    time.sleep(backoff_base * (2 ** (attempt - 1)))
                continue

            if fr.error:
                last_error_msg = f"{fr.error} (attempt {attempt})"
                if attempt < max_retries:
                    time.sleep(backoff_base * (2 ** (attempt - 1)))
                continue

        return SourceFetchResult(
            source_id=source.source_id,
            source_url=url,
            status="failed",
            http_status_code=last_http_status,
            fetched_at=fetched_at,
            error_code="fetch_failed",
            error_message_sanitized=(
                f"Fetch failed after {max_retries} attempt(s): {last_error_msg}"
            ),
            compliance_status="compliant",
            robots_allowed=robots_checker.is_allowed(url),
            latency_ms=last_latency,
            content_bytes=0,
        )

    def _fetch_robots_txt(self, base_url: str, timeout: float) -> RobotsChecker:
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            return RobotsChecker()
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        try:
            fr = fetch_page(robots_url, timeout=int(timeout))
            if fr.status == 200 and fr.raw_html:
                return RobotsChecker(fr.raw_html, self._user_agent)
        except Exception as exc:
            logger.warning("Failed to fetch robots.txt from %s: %s", robots_url, exc)
        return RobotsChecker()

    @staticmethod
    def _rate_limit_wait(
        policy_id: str,
        requests_per_second: float,
        policy_limiters: dict[str, float],
    ) -> None:
        interval = 1.0 / max(requests_per_second, 0.5)
        last = policy_limiters.get(policy_id, 0.0)
        now = time.time()
        elapsed = now - last
        if elapsed < interval:
            time.sleep(interval - elapsed)
        policy_limiters[policy_id] = time.time()

    @staticmethod
    def _compute_metrics(sources: list[SourceFetchResult]) -> CollectionMetrics:
        total = len(sources)
        if total == 0:
            return CollectionMetrics()

        fetched = [s for s in sources if s.status == "fetched"]
        blocked = [s for s in sources if s.status == "blocked"]
        failed = [s for s in sources if s.status == "failed"]
        duplicates = [s for s in sources if s.status == "duplicate"]
        robots_blocked = [s for s in sources if s.error_code == "robots_disallowed"]
        compliance_blocked = [s for s in sources if s.error_code == "compliance_blocked"]

        latencies = [s.latency_ms for s in fetched]
        total_latency = sum(latencies)
        median_latency = median(latencies) if latencies else 0.0

        total_content = sum(s.content_bytes for s in fetched)
        extraction_success = sum(1 for s in fetched if s.extraction_status == "success")
        extraction_rate = extraction_success / len(fetched) if fetched else 0.0
        fetch_rate = len(fetched) / total if total else 0.0

        return CollectionMetrics(
            attempted_sources_count=total,
            fetched_sources_count=len(fetched),
            blocked_sources_count=len(blocked),
            failed_sources_count=len(failed),
            robots_blocked_count=len(robots_blocked),
            compliance_blocked_count=len(compliance_blocked),
            duplicate_count=len(duplicates),
            total_latency_ms=total_latency,
            median_latency_ms=median_latency,
            total_content_bytes=total_content,
            extraction_success_rate=extraction_rate,
            fetch_success_rate=fetch_rate,
        )


# ── Factory / Helpers ────────────────────────────────────────────────────


def build_http_collector(user_agent: str | None = None) -> HttpSourceCollector:
    logger.info("HttpSourceCollector created (governed by Source Registry + Decision Calibration)")
    return HttpSourceCollector(user_agent=user_agent)


def list_governed_sources() -> list[SourceRecord]:
    return list_production_enabled_sources()
