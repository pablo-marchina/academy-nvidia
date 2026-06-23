"""Scraping package with lazy public exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "CollectionMetrics",
    "CollectionRequest",
    "CollectionResult",
    "ComplianceResult",
    "HttpSourceCollector",
    "SourceFetchResult",
    "build_http_collector",
    "list_governed_sources",
]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module 'src.scraping' has no attribute {name!r}")
    value = getattr(import_module("src.scraping.http_collector"), name)
    globals()[name] = value
    return value
