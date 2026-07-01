"""Build adaptive, governed search plans for a given startup name.

The planner intentionally separates real startup-owned sources from
third-party ecosystem/directories. Directory pages must never satisfy an
"official source" gate: they are useful discovery/evidence sources, but they
are not controlled by the startup.
"""

from __future__ import annotations

import os
import re
from typing import Any
from urllib.parse import quote_plus, urlparse


def _normalize_startup_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def _is_allowed_source(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    blocked = ("login", "signin", "paywall")
    return not any(term in parsed.path.lower() for term in blocked)


_NEWS_HOSTS = (
    "exame.com",
    "valor.globo.com",
    "neofeed.com.br",
    "braziljournal.com",
    "startups.com.br",
    "revistapegn.globo.com",
    "mobiletime.com.br",
    "meioemensagem.com.br",
)

_DIRECTORY_HOSTS = (
    "distrito.me",
    "startse.com",
    "latitud.com",
    "cubo.network",
    "acestartups.com.br",
    "bossainvest.com",
    "bossainvest.com.br",
    "inovativa.online",
    "inovativabrasil.com.br",
    "endeavor.org.br",
    "abstartups.com.br",
    "anjosdobrasil.net",
    "darwinstartups.com",
    "liga.ventures",
    "openstartups.net",
    "wow.ac",
)


def _classify_source(url: str, *, source_type_hint: str | None = None, is_probable_owned_domain: bool = False) -> str:
    host = urlparse(url).netloc.lower().replace("www.", "")
    path = urlparse(url).path.lower()
    hint = (source_type_hint or "").casefold()

    if hint in {"news"} or any(n in host for n in _NEWS_HOSTS):
        return "news"
    if "linkedin.com" in host:
        return "founder_profile"
    if "jobs" in host or "careers" in path or "vagas" in path:
        return "job_post"
    if "blog" in host or "blog" in path or "engineering" in path:
        return "blog"
    if hint in {"public_directory", "startup_program", "accelerator", "vc_portfolio", "event_page", "manual_seed"}:
        return "directory"
    if any(d in host for d in _DIRECTORY_HOSTS):
        return "directory"
    if hint == "search_api":
        return "search_api"
    return "official_site" if is_probable_owned_domain and host else "directory"


def build_search_plan(startup_name: str) -> list[dict[str, Any]]:
    from src.discovery.source_registry import list_enabled_sources
    from src.sourcing.adaptive_source_planner import SourceCandidate, source_decision_trace

    plan: list[dict[str, Any]] = []
    seen: set[str] = set()
    source_type_counts: dict[str, int] = {}
    normalized = _normalize_startup_name(startup_name)

    def _source_metrics(url: str, source_type: str) -> dict[str, float]:
        authority_by_type = {
            "official_site": 0.98,
            "news": 0.82,
            "founder_profile": 0.72,
            "job_post": 0.68,
            "blog": 0.66,
            "directory": 0.54,
            "search_api": 0.50,
        }
        prior_count = source_type_counts.get(source_type, 0)
        host = url.lower()
        compliance_risk = 0.10
        if "linkedin.com" in host:
            compliance_risk = 0.25
        freshness = 0.78 if source_type in {"news", "job_post", "blog", "search_api"} else 0.58
        independence = 0.85 if source_type in {"news", "directory"} else 0.35 if source_type == "official_site" else 0.55
        return {
            "authority": authority_by_type.get(source_type, 0.50),
            "freshness": freshness,
            "independence": independence,
            "known_gap_coverage": min(1.0, prior_count / 3.0),
            "expected_category_coverage": 1.0 / float(prior_count + 1),
            "marginal_new_evidence": 1.0 / float(prior_count + 1),
            "estimated_cost": 0.0,
            "latency_ms": 750.0 if source_type == "official_site" else 950.0,
            "compliance_risk": compliance_risk,
        }

    def _add(url: str, reason: str, *, source_type_hint: str | None = None, is_probable_owned_domain: bool = False) -> None:
        if url in seen:
            return
        seen.add(url)
        if not _is_allowed_source(url):
            return
        source_type = _classify_source(url, source_type_hint=source_type_hint, is_probable_owned_domain=is_probable_owned_domain)
        metrics = _source_metrics(url, source_type)
        candidate = SourceCandidate(source_name=reason, source_url=url, **metrics)
        trace = source_decision_trace(candidate)
        plan.append(
            {
                "url": url,
                "source_type": source_type,
                "is_official_source": source_type == "official_site",
                "reason": reason,
                "expected_information_gain": trace["expected_information_gain"],
                "marginal_utility": trace["marginal_utility"],
                "estimated_cost": trace["estimated_cost"],
                "latency_ms": trace["latency_ms"],
                "compliance_risk": trace["compliance_risk"],
                "decision_formula": trace["formula"],
            }
        )
        source_type_counts[source_type] = source_type_counts.get(source_type, 0) + 1

    for source in list_enabled_sources(api_key_available=bool(os.getenv("SERPAPI_API_KEY"))):
        if source.base_url:
            _add(
                source.base_url,
                f"Configured source: {source.name}",
                source_type_hint=getattr(source.source_type, "value", str(source.source_type)),
            )

    # Search APIs are candidate discovery mechanisms, not evidence sources. They
    # are included only when configured; raw search result URLs must be collected
    # and validated before becoming evidence.
    if os.getenv("SERPAPI_API_KEY"):
        _add(
            f"https://serpapi.com/search.json?q={quote_plus(startup_name + ' startup AI Brasil')}",
            "Configured Search API: startup + AI + Brazil",
            source_type_hint="search_api",
        )

    direct_urls = [
        (f"https://br.linkedin.com/company/{normalized}", "LinkedIn company page", False),
        (f"https://{normalized}.com.br", "Probable startup-owned Brazilian domain", True),
        (f"https://www.{normalized}.com.br", "Probable startup-owned Brazilian domain (www)", True),
        (f"https://{normalized}.com", "Probable startup-owned .com domain", True),
        (f"https://www.{normalized}.com", "Probable startup-owned .com domain (www)", True),
    ]
    for url, reason, owned in direct_urls:
        _add(url, reason, is_probable_owned_domain=owned)

    return sorted(plan, key=lambda item: float(item["marginal_utility"]), reverse=True)
