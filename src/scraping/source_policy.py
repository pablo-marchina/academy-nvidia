"""Source classification and allowlist helpers for public startup research."""

from urllib.parse import urlparse

from src.extraction.schemas import SourceType

_KNOWN_OFFICIAL_HINTS = ("about", "company", "careers", "blog")


def classify_source(url: str) -> SourceType:
    """Classify a public source using simple URL-based heuristics."""

    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    if "linkedin.com" in host:
        return SourceType.FOUNDER_PROFILE
    if any(news_host in host for news_host in ("exame.com", "valor.globo.com", "neofeed.com.br")):
        return SourceType.NEWS
    if "jobs" in host or "careers" in path:
        return SourceType.JOB_POST
    if "blog" in host or "blog" in path:
        return SourceType.BLOG
    if any(hint in path for hint in _KNOWN_OFFICIAL_HINTS) or host:
        return SourceType.OFFICIAL_SITE
    return SourceType.DIRECTORY


def is_allowed_source(url: str) -> bool:
    """Return whether the URL is eligible for polite public-web collection."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    blocked_terms = ("login", "signin", "paywall")
    return not any(term in parsed.path.lower() for term in blocked_terms)
