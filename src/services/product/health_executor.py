"""Health check executor — runs real dependency checks for readiness service.

Each check maps to a ``health_check_key`` defined on a ``CapabilityDefinition``.
Results are cached with a TTL to avoid hammering dependencies on every request.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.services.product.capability_registry import CapabilityStatus


@dataclass
class HealthCheckResult:
    status: CapabilityStatus
    latency_ms: float = 0.0
    detail: str = ""


_RAG_CATEGORIES = {"rag"}


def _is_rag_capability(category: str) -> bool:
    return category in _RAG_CATEGORIES


_executor: HealthCheckExecutor | None = None


def get_health_executor() -> HealthCheckExecutor:
    global _executor
    if _executor is None:
        _executor = HealthCheckExecutor()
    return _executor


class HealthCheckExecutor:
    """Run health checks for capabilities by ``health_check_key``.

    Each check is cached for ``cache_ttl`` seconds to avoid
    hammering dependencies on every readiness call.
    """

    def __init__(self, cache_ttl: float = 30.0) -> None:
        self._cache_ttl = cache_ttl
        self._cache: dict[str, tuple[HealthCheckResult, float]] = {}

    def check(self, key: str) -> HealthCheckResult:
        now = time.monotonic()
        if key in self._cache:
            result, cached_at = self._cache[key]
            if now - cached_at < self._cache_ttl:
                return result
        result = self._execute(key)
        self._cache[key] = (result, now)
        return result

    def invalidate(self, key: str | None = None) -> None:
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    def _execute(self, key: str) -> HealthCheckResult:
        start = time.monotonic()
        if key == "product_db":
            result = self._check_product_db()
        elif key == "qdrant":
            result = self._check_qdrant()
        elif key == "rag":
            result = self._check_rag_corpus()
        elif key == "llm_judge":
            result = self._check_llm_judge()
        else:
            result = HealthCheckResult(
                status=CapabilityStatus.available,
                detail=f"No health check implemented for '{key}'",
            )
        result.latency_ms = round((time.monotonic() - start) * 1000, 1)
        return result

    def _check_product_db(self) -> HealthCheckResult:
        try:
            from src.database.session import check_product_database

            ok, error = check_product_database()
            if ok:
                return HealthCheckResult(
                    status=CapabilityStatus.available,
                    detail="Database responded to SELECT 1",
                )
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail=f"Database unreachable: {error}",
            )
        except Exception as exc:
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail=f"Database health check error: {exc}",
            )

    def _check_qdrant(self) -> HealthCheckResult:
        url = os.environ.get("QDRANT_URL", "")
        if not url:
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail="QDRANT_URL is not set",
            )
        api_key = os.environ.get("QDRANT_API_KEY") or None
        collection = os.environ.get("QDRANT_COLLECTION", "")
        if not collection:
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail="QDRANT_COLLECTION is not set",
            )
        min_points = int(os.environ.get("QDRANT_MIN_POINTS", "10"))
        try:
            from qdrant_client import QdrantClient

            client = QdrantClient(url=url, api_key=api_key, timeout=5)
            collections = client.get_collections().collections
            existing = {c.name for c in collections}
            if collection not in existing:
                return HealthCheckResult(
                    status=CapabilityStatus.degraded,
                    detail=f"Qdrant reachable but collection '{collection}' not found",
                )
            count = client.count(collection_name=collection).count
            if count == 0:
                return HealthCheckResult(
                    status=CapabilityStatus.degraded,
                    detail=f"Qdrant collection '{collection}' exists but is empty",
                )
            if count < min_points:
                return HealthCheckResult(
                    status=CapabilityStatus.degraded,
                    detail=(
                        f"Qdrant collection '{collection}' has only {count} point(s), "
                        f"below minimum threshold of {min_points}"
                    ),
                )
            return HealthCheckResult(
                status=CapabilityStatus.available,
                detail=f"Qdrant reachable at {url}, collection '{collection}' has {count} point(s)",
            )
        except ImportError:
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail="qdrant-client package not installed",
            )
        except Exception as exc:
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail=f"Qdrant unreachable at {url}: {exc}",
            )

    def _check_rag_corpus(self) -> HealthCheckResult:
        corpus_dir = Path("data/nvidia_corpus")
        if not corpus_dir.exists():
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail="Corpus directory 'data/nvidia_corpus' not found",
            )
        md_files = sorted(corpus_dir.glob("*.md"))
        md_files = [f for f in md_files if f.name != "README.md"]
        if not md_files:
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail="Corpus directory exists but no markdown documents found",
            )
        sources_file = corpus_dir / "sources.yaml"
        if not sources_file.exists():
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail="Corpus files found but sources.yaml is missing",
            )
        freshness_error = _check_sources_freshness(sources_file)
        if freshness_error:
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail=freshness_error,
            )
        return HealthCheckResult(
            status=CapabilityStatus.available,
            detail=f"Corpus found with {len(md_files)} document(s)",
        )

    def _check_llm_judge(self) -> HealthCheckResult:
        enabled = os.environ.get("ANSWER_QUALITY_LLM_JUDGE_ENABLED", "false").lower()
        if enabled != "true":
            return HealthCheckResult(
                status=CapabilityStatus.unavailable,
                detail="ANSWER_QUALITY_LLM_JUDGE_ENABLED is not set to true",
            )
        provider = os.environ.get("ANSWER_QUALITY_LLM_JUDGE_PROVIDER", "")
        legacy_provider = os.environ.get("LLM_PROVIDER", "")
        if not provider and legacy_provider:
            provider = legacy_provider
        if not provider:
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail=(
                    "LLM judge enabled but ANSWER_QUALITY_LLM_JUDGE_PROVIDER "
                    "env var is not set"
                ),
            )
        if provider == "null":
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail=(
                    "ANSWER_QUALITY_LLM_JUDGE_PROVIDER=null uses the offline "
                    "NullLLMJudgeProvider and is not a semantic quality judge"
                ),
            )
        return HealthCheckResult(
            status=CapabilityStatus.degraded,
            detail=(
                f"ANSWER_QUALITY_LLM_JUDGE_PROVIDER={provider} has no active "
                "runtime provider implementation"
            ),
        )


def _check_sources_freshness(sources_file: Path) -> str:
    try:
        import yaml
    except ImportError:
        return "PyYAML is not installed; cannot audit corpus freshness"

    try:
        payload: dict[str, Any] = yaml.safe_load(sources_file.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return f"Failed to read corpus freshness metadata: {exc}"

    now = datetime.now(UTC)
    stale: list[str] = []
    expired: list[str] = []
    for source_id, item in (payload.get("sources") or {}).items():
        if not isinstance(item, dict) or item.get("is_active") is False:
            continue
        valid_until = item.get("valid_until")
        if valid_until:
            try:
                expiry = datetime.fromisoformat(str(valid_until).replace("Z", "+00:00"))
            except ValueError:
                expired.append(str(source_id))
            else:
                if expiry < now:
                    expired.append(str(source_id))
        last_checked = item.get("last_checked_at") or item.get("collected_at")
        stale_after = item.get("stale_after_days")
        if last_checked and stale_after is not None:
            try:
                checked_at = datetime.fromisoformat(str(last_checked).replace("Z", "+00:00"))
                stale_days = int(stale_after)
            except (TypeError, ValueError):
                stale.append(str(source_id))
            else:
                if (now - checked_at).days > stale_days:
                    stale.append(str(source_id))

    if expired:
        return f"Corpus has expired active source(s): {', '.join(sorted(expired))}"
    if stale:
        return f"Corpus has stale active source(s): {', '.join(sorted(stale))}"
    return ""
