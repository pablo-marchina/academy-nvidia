"""Build search plans for a given startup name.

Combines configured discovery sources with direct-name URLs
to produce a list of target URLs for evidence collection.
"""

from __future__ import annotations

import re


def _normalize_startup_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def _is_allowed_source(url: str) -> bool:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    blocked = ("login", "signin", "paywall")
    return not any(term in parsed.path.lower() for term in blocked)


def _classify_source(url: str) -> str:
    from urllib.parse import urlparse

    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    if "linkedin.com" in host:
        return "founder_profile"
    if any(n in host for n in ("exame.com", "valor.globo.com", "neofeed.com.br")):
        return "news"
    if "jobs" in host or "careers" in path:
        return "job_post"
    if "blog" in host or "blog" in path:
        return "blog"
    return "official_site" if host else "directory"


def build_search_plan(startup_name: str) -> list[dict[str, str]]:
    from src.discovery.source_registry import list_enabled_sources

    plan: list[dict[str, str]] = []
    seen: set[str] = set()

    normalized = _normalize_startup_name(startup_name)

    def _add(url: str, reason: str) -> None:
        if url in seen:
            return
        seen.add(url)
        if _is_allowed_source(url):
            plan.append(
                {
                    "url": url,
                    "source_type": _classify_source(url),
                    "reason": reason,
                }
            )

    for source in list_enabled_sources():
        if source.base_url:
            _add(source.base_url, f"Configured source: {source.name}")

    direct_urls = [
        (
            f"https://www.google.com/search?q={startup_name.replace(' ', '+')}+startup+AI+brasil",
            "Google search for startup + AI + Brazil",
        ),
        (f"https://br.linkedin.com/company/{normalized}", "LinkedIn company page"),
        (f"https://{normalized}.com.br", "Probable Brazilian domain"),
        (f"https://www.{normalized}.com.br", "Probable Brazilian domain (www)"),
        (f"https://{normalized}.com", "Probable .com domain"),
    ]
    for url, reason in direct_urls:
        _add(url, reason)

    return plan
