"""HTTP fetching for single public URL collection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

_USER_AGENT = "Mozilla/5.0 (compatible; NVIDIAStartupAIRadar/0.1; +https://github.com/nvidia/startup-ai-radar)"
_DEFAULT_TIMEOUT = 15


@dataclass(slots=True)
class FetchResult:
    url: str
    status: int | None
    raw_html: str
    fetched_at: datetime
    error: str | None


def fetch_page(url: str, timeout: int = _DEFAULT_TIMEOUT) -> FetchResult:
    """Fetch a single public URL and return metadata + raw HTML.

    Never raises an exception — all errors are captured in the
    ``error`` field of the returned ``FetchResult``.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return FetchResult(
            url=url,
            status=None,
            raw_html="",
            fetched_at=datetime.now(timezone.utc),  # noqa: UP017
            error=f"Invalid or unsupported URL: {url}",
        )

    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": _USER_AGENT},
        )
        fetched_at = datetime.now(timezone.utc)  # noqa: UP017

        if resp.status_code >= 400:
            return FetchResult(
                url=url,
                status=resp.status_code,
                raw_html="",
                fetched_at=fetched_at,
                error=f"HTTP {resp.status_code}: {resp.reason}",
            )

        return FetchResult(
            url=url,
            status=resp.status_code,
            raw_html=resp.text,
            fetched_at=fetched_at,
            error=None,
        )

    except requests.exceptions.Timeout as exc:
        return FetchResult(
            url=url,
            status=None,
            raw_html="",
            fetched_at=datetime.now(timezone.utc),  # noqa: UP017
            error=f"Timeout after {timeout}s: {exc}",
        )
    except requests.exceptions.ConnectionError as exc:
        return FetchResult(
            url=url,
            status=None,
            raw_html="",
            fetched_at=datetime.now(timezone.utc),  # noqa: UP017
            error=f"Connection error: {exc}",
        )
    except requests.exceptions.RequestException as exc:
        return FetchResult(
            url=url,
            status=None,
            raw_html="",
            fetched_at=datetime.now(timezone.utc),  # noqa: UP017
            error=f"Request failed: {exc}",
        )
