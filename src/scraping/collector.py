"""Real source collector that discovers and fetches sources per category.

Driven by SourceRegistry (production_enabled sources only) and
RateLimitPolicyRegistry (per-policy rate limiting + retry/backoff).

Respects robots/terms, rate limits, retry/backoff, logs per source,
deduplication. Uses existing fetcher + parser infrastructure.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from urllib.parse import urlparse

from src.scraping.fetcher import fetch_page
from src.scraping.parser import extract_clean_text
from src.scraping.rate_limit_policy import get_rate_limit_policy
from src.scraping.source_registry import (
    SourceRecord,
    list_production_enabled_sources,
    load_source_registry,
)

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 15


@dataclass
class CollectedSource:
    url: str
    category: str
    rank: int = 0
    fetch_success: bool = False
    extraction_success: bool = False
    is_duplicate: bool = False
    latency_ms: int = 0
    compliance_blocked: bool = False
    error: str | None = None
    collected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CollectionResult:
    startup_name: str
    website_url: str
    sources: list[CollectedSource] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None


class _RateLimiter:
    """Per-policy rate limiter using token-bucket semantics."""

    def __init__(self) -> None:
        self._last_request_time: float = 0.0

    def wait(self, requests_per_second: float) -> None:
        interval = 1.0 / max(requests_per_second, 0.5)
        elapsed = time.time() - self._last_request_time
        if elapsed < interval:
            time.sleep(interval - elapsed)
        self._last_request_time = time.time()


def _enabled_sources_by_category() -> dict[str, list[SourceRecord]]:
    groups: dict[str, list[SourceRecord]] = defaultdict(list)
    for src in list_production_enabled_sources():
        groups[src.source_category].append(src)
    return dict(groups)


class SourceCollector:
    """Polite web collector driven by SourceRegistry.

    Only collects from production_enabled sources.
    Rate limiting, retries and backoff are driven by
    each source's RateLimitPolicy.
    """

    def __init__(
        self,
        *,
        available_capabilities: set[str] | None = None,
    ) -> None:
        load_source_registry(available_capabilities=available_capabilities)
        self._policy_limiters: dict[str, _RateLimiter] = {}
        self._seen_urls: set[str] = set()

    def _limiter(self, policy_id: str) -> _RateLimiter:
        if policy_id not in self._policy_limiters:
            self._policy_limiters[policy_id] = _RateLimiter()
        return self._policy_limiters[policy_id]

    def collect(self, startup_name: str, website_url: str) -> CollectionResult:
        result = CollectionResult(startup_name=startup_name, website_url=website_url)
        domain = urlparse(website_url).netloc.lower()

        by_cat = _enabled_sources_by_category()
        rank = 0

        for cat, sources in by_cat.items():
            try:
                collected = self._collect_category(cat, sources, startup_name, website_url, domain)
                for s in collected:
                    if self._deduplicate(s.url):
                        continue
                    rank += 1
                    s.category = cat
                    s.rank = rank
                    result.sources.append(s)
            except Exception as exc:
                msg = f"collector.{cat}: {exc}"
                logger.warning(msg)
                result.errors.append(msg)

        result.finished_at = datetime.now(UTC)
        return result

    def _deduplicate(self, url: str) -> bool:
        normalized = url.split("#")[0].split("?")[0].rstrip("/")
        if normalized in self._seen_urls:
            return True
        self._seen_urls.add(normalized)
        return False

    def _fetch_with_retry(self, url: str, policy_id: str) -> CollectedSource:
        source = CollectedSource(url=url, category="", latency_ms=0)
        policy = get_rate_limit_policy(policy_id)
        if policy is None:
            policy = get_rate_limit_policy("default_polite")
        assert policy is not None
        max_retries = policy.max_retries

        limiter = self._limiter(policy_id)

        for attempt in range(1, max_retries + 1):
            limiter.wait(policy.requests_per_second)
            start = time.time()
            result = fetch_page(url, timeout=_REQUEST_TIMEOUT)
            elapsed_ms = int((time.time() - start) * 1000)
            source.latency_ms = elapsed_ms
            source.collected_at = datetime.now(UTC)

            if result.status is not None and result.status < 400:
                source.fetch_success = True
                text = extract_clean_text(result.raw_html)
                source.extraction_success = bool(text.strip())
                logger.info("FETCH_OK  %s  %dms  len=%d", url, elapsed_ms, len(text))
                return source

            if result.status is not None and 400 <= result.status < 500:
                source.error = f"HTTP {result.status}"
                logger.warning("FETCH_CLIENT_ERR  %s  HTTP %d", url, result.status)
                return source

            if result.status is not None and result.status >= 500:
                source.error = f"HTTP {result.status} (attempt {attempt})"
                logger.warning("FETCH_SERVER_ERR  %s  HTTP %d (attempt %d)", url, result.status, attempt)
                if attempt < max_retries:
                    time.sleep(2**attempt)
                continue

            if result.error:
                source.error = result.error
                logger.warning("FETCH_ERR  %s  %s (attempt %d)", url, result.error, attempt)
                if attempt < max_retries:
                    time.sleep(2**attempt)
                continue

        return source

    # ── Category dispatch ───────────────────────────────────────────────

    def _collect_category(
        self,
        cat: str,
        sources: list[SourceRecord],
        startup_name: str,
        website_url: str,
        domain: str,
    ) -> list[CollectedSource]:
        dispatch = {
            "official_website": self._collect_official,
            "github_or_code": self._collect_github,
            "technical_docs": self._collect_probe_paths,
            "jobs": self._collect_probe_paths,
            "funding_news": self._collect_news_media,
            "media": self._collect_news_media,
            "ecosystem_directory": self._collect_named_url,
            "nvidia_or_partner_ecosystem": self._collect_named_url,
        }
        method = dispatch.get(cat)
        if method is None:
            logger.warning("No collector strategy for category '%s'", cat)
            return []
        return method(sources, startup_name, website_url, domain)

    def _collect_official(
        self,
        sources: list[SourceRecord],
        startup_name: str,
        website_url: str,
        domain: str,
    ) -> list[CollectedSource]:
        policy_id = sources[0].rate_limit_policy_id if sources else "default_polite"
        result = [self._fetch_with_retry(website_url, policy_id)]
        logger.info(
            "CATEGORY official_website: 1 source (%s) from %s",
            sources[0].source_id if sources else "?",
            website_url,
        )
        return result

    def _collect_github(
        self,
        sources: list[SourceRecord],
        startup_name: str,
        website_url: str,
        domain: str,
    ) -> list[CollectedSource]:
        results: list[CollectedSource] = []
        name = startup_name.lower().replace(" ", "-").replace(".", "-")
        for src in sources:
            search_url = f"{src.base_url}/search/repositories?q={name}+in:name&sort=stars&per_page=3"
            collected = self._fetch_with_retry(search_url, src.rate_limit_policy_id)
            results.append(collected)
            logger.info("CATEGORY github_or_code: source=%s url=%s", src.source_id, search_url)
        return results

    def _collect_probe_paths(
        self,
        sources: list[SourceRecord],
        startup_name: str,
        website_url: str,
        domain: str,
    ) -> list[CollectedSource]:
        results: list[CollectedSource] = []
        for src in sources:
            base = f"https://{domain}"
            for path in src.allowed_paths:
                url = f"{base}{path}"
                if self._deduplicate(url):
                    continue
                collected = self._fetch_with_retry(url, src.rate_limit_policy_id)
                if collected.fetch_success and collected.extraction_success:
                    logger.info(
                        "CATEGORY %s: source=%s url=%s",
                        src.source_category,
                        src.source_id,
                        url,
                    )
                    results.append(collected)
                    break
        return results

    def _collect_news_media(
        self,
        sources: list[SourceRecord],
        startup_name: str,
        website_url: str,
        domain: str,
    ) -> list[CollectedSource]:
        results: list[CollectedSource] = []
        for src in sources:
            found = self._search_named_site(src, startup_name)
            if found is not None:
                results.append(found)
        return results

    def _search_named_site(self, src: SourceRecord, startup_name: str) -> CollectedSource | None:
        name_slug = startup_name.lower().replace(" ", "-").replace(".", "-")
        url = f"{src.base_url.rstrip('/')}/{name_slug}"
        collected = self._fetch_with_retry(url, src.rate_limit_policy_id)
        if collected.fetch_success and collected.extraction_success:
            return collected
        name_compact = startup_name.lower().replace(" ", "")
        url2 = f"{src.base_url.rstrip('/')}/{name_compact}"
        collected2 = self._fetch_with_retry(url2, src.rate_limit_policy_id)
        return collected2 if collected2.fetch_success and collected2.extraction_success else None

    def _collect_named_url(
        self,
        sources: list[SourceRecord],
        startup_name: str,
        website_url: str,
        domain: str,
    ) -> list[CollectedSource]:
        results: list[CollectedSource] = []
        name_slug = startup_name.lower().replace(" ", "-").replace(".", "-")
        for src in sources:
            url = f"{src.base_url.rstrip('/')}/{name_slug}"
            if self._deduplicate(url):
                continue
            collected = self._fetch_with_retry(url, src.rate_limit_policy_id)
            if collected.fetch_success and collected.extraction_success:
                logger.info(
                    "CATEGORY %s: source=%s url=%s",
                    src.source_category,
                    src.source_id,
                    url,
                )
                results.append(collected)
        return results

    def collect_and_validate(
        self,
        startup_name: str,
        website_url: str,
    ) -> CollectionResult:
        return self.collect(startup_name, website_url)


def build_collector(
    *,
    available_capabilities: set[str] | None = None,
) -> SourceCollector:
    logger.info("SourceCollector created (registry-driven)")
    return SourceCollector(available_capabilities=available_capabilities)
