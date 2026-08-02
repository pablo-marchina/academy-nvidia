from __future__ import annotations

from src.agents.search_planner import build_search_plan
from src.sourcing.adaptive_source_planner import SourceCandidate, expected_information_gain, should_stop_collection


def test_search_plan_exposes_quantitative_source_decisions() -> None:
    plan = build_search_plan("Radar AI", website_url="https://radar.ai")

    assert plan
    first = plan[0]
    assert 0.0 <= first["expected_information_gain"] <= 1.0
    assert 0.0 <= first["marginal_utility"] <= 1.0
    assert "estimated_cost" in first
    assert "compliance_risk" in first
    assert "decision_formula" in first


def test_expected_information_gain_penalizes_compliance_risk() -> None:
    low_risk = SourceCandidate("official", "https://example.com", authority=0.8, compliance_risk=0.0)
    high_risk = SourceCandidate("risky", "https://example.com/login", authority=0.8, compliance_risk=1.0)

    assert expected_information_gain(low_risk) > expected_information_gain(high_risk)


def test_stop_collection_requires_low_marginal_gain_for_source_limit() -> None:
    keep_collecting = should_stop_collection(
        confidence=0.70,
        sources_seen=20,
        max_sources=12,
        marginal_gain=0.20,
        evidence_coverage=0.40,
        source_diversity=1,
    )
    stop = should_stop_collection(
        confidence=0.70,
        sources_seen=20,
        max_sources=12,
        marginal_gain=0.01,
        evidence_coverage=0.40,
        source_diversity=1,
    )

    assert keep_collecting is False
    assert stop is True


def test_search_plan_uses_only_entity_specific_urls() -> None:
    plan = build_search_plan(
        "Nilo Saúde",
        website_url="https://www.nilo.com.br/",
        known_source_urls=["https://www.nilo.com.br/sobre", "https://startups.com.br/nilo-saude"],
        max_sources=5,
    )

    urls = [item["url"] for item in plan]
    assert "https://www.nilo.com.br/" in urls
    assert "https://www.nilo.com.br/sobre" in urls
    assert "https://startups.com.br/nilo-saude" in urls
    assert not any(url.endswith("distrito.me") or url.endswith("cubo.network") for url in urls)
    assert not any("nilo-sade" in url for url in urls)
    assert len(urls) <= 5
