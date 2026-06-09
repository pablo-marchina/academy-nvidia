"""HTTP fetching scaffold for future scraping workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class FetchResult:
    url: str
    status: int | None
    raw_html: str
    fetched_at: datetime


def fetch_page(url: str) -> FetchResult:
    """Return a placeholder fetch result until real network fetching is enabled."""

    return FetchResult(
        url=url,
        status=None,
        raw_html="",
        fetched_at=datetime.now(timezone.utc),
    )
