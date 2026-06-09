"""HTML parsing helpers for extracting clean text from fetched pages."""

from __future__ import annotations

from bs4 import BeautifulSoup

try:
    import trafilatura  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional at runtime
    trafilatura = None  # type: ignore[assignment]


def extract_clean_text(raw_html: str) -> str:
    """Extract readable text from HTML using trafilatura when available."""

    if trafilatura is not None:
        extracted = trafilatura.extract(raw_html)
        if extracted:
            return extracted.strip()  # type: ignore[no-any-return]

    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)
