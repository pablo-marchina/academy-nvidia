"""Health check executor — runs real dependency checks for readiness service.

Each check maps to a ``health_check_key`` defined on a ``CapabilityDefinition``.
Results are cached with a TTL to avoid hammering dependencies on every request.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

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
        url = os.environ.get("QDRANT_URL", "http://localhost:6333")
        api_key = os.environ.get("QDRANT_API_KEY") or None
        collection = os.environ.get("QDRANT_COLLECTION", "nvidia_corpus")
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
        provider = os.environ.get("LLM_PROVIDER", "")
        if not provider:
            return HealthCheckResult(
                status=CapabilityStatus.degraded,
                detail="LLM judge enabled but LLM_PROVIDER env var is not set",
            )
        if provider == "openai":
            if not os.environ.get("OPENAI_API_KEY"):
                return HealthCheckResult(
                    status=CapabilityStatus.degraded,
                    detail=f"LLM_PROVIDER={provider} but OPENAI_API_KEY is not set",
                )
            return HealthCheckResult(
                status=CapabilityStatus.available,
                detail=f"LLM judge configured with provider={provider}",
            )
        return HealthCheckResult(
            status=CapabilityStatus.degraded,
            detail=f"Unknown LLM_PROVIDER={provider}",
        )
