from __future__ import annotations

from src.sourcing import (
    SourceAttempt,
    SourceCategory,
    compute_source_coverage,
    default_source_registry,
    discover_seed_sources,
    policy_for_category,
    score_source,
)


def test_default_source_registry_covers_required_categories() -> None:
    categories = {source.category for source in default_source_registry()}

    assert {
        SourceCategory.OFFICIAL_SITE,
        SourceCategory.OFFICIAL_BLOG,
        SourceCategory.CAREERS,
        SourceCategory.PRODUCT_DOCS,
        SourceCategory.LINKEDIN_PUBLIC,
        SourceCategory.GITHUB_PUBLIC,
        SourceCategory.TRUSTED_NEWS,
        SourceCategory.ACCELERATOR,
        SourceCategory.STARTUP_DIRECTORY,
        SourceCategory.INVESTOR_PORTFOLIO,
        SourceCategory.NVIDIA_OFFICIAL,
        SourceCategory.NVIDIA_DOCS,
        SourceCategory.CASE_MATERIAL,
    }.issubset(categories)


def test_compute_source_coverage_exposes_gaps_and_blocked_sources() -> None:
    attempts = [
        SourceAttempt(
            source_id="official",
            category=SourceCategory.OFFICIAL_SITE,
            url="https://startup.example.com",
            status="success",
            evidence_items=8,
            valid_claims=4,
        ),
        SourceAttempt(
            source_id="news",
            category=SourceCategory.TRUSTED_NEWS,
            url="https://news.example.com/startup",
            status="blocked",
            blocked_reason="robots_disallow",
        ),
    ]

    report = compute_source_coverage(
        startup_id="startup-1",
        attempts=attempts,
        expected_categories={
            SourceCategory.OFFICIAL_SITE,
            SourceCategory.TRUSTED_NEWS,
            SourceCategory.PRODUCT_DOCS,
        },
        cross_source_confirmed_claims=2,
        total_claims=4,
        robots_allowed_by_source={"official": True, "news": False},
        tos_allowed_by_source={"official": True, "news": True},
    )

    assert report.sources_attempted == 2
    assert report.sources_successful == 1
    assert report.blocked_sources == 1
    assert report.valid_evidence_items == 8
    assert report.coverage_by_category["official_site"] == 1.0
    assert report.coverage_by_category["product_docs"] == 0.0
    assert report.source_coverage_score == 0.3333
    assert report.cross_source_confirmation_rate == 0.5
    assert report.robots_compliance_status == "needs_review"
    assert "product_docs" in report.remaining_gaps


def test_source_scoring_is_quantitative_and_exposes_weights() -> None:
    source = default_source_registry()[0]
    attempt = SourceAttempt(
        source_id=source.source_id,
        category=source.category,
        url="https://startup.example.com",
        status="success",
        evidence_items=5,
        valid_claims=2,
    )

    score = score_source(source, attempt, freshness_days=30, robots_allowed=True, tos_allowed=True)

    assert score.overall_score > 0.0
    assert score.confidence > score.uncertainty
    assert set(score.weights) == {"authority", "freshness", "evidence_yield", "compliance"}


def test_discovery_seeds_are_marked_by_method_and_policy_is_public_only() -> None:
    candidates = discover_seed_sources("Radar AI", "https://radar.example.com")
    github = [candidate for candidate in candidates if candidate.category == SourceCategory.GITHUB_PUBLIC][0]
    policy = policy_for_category(SourceCategory.LINKEDIN_PUBLIC)

    assert github.discovery_method == "public_profile_guess_requires_validation"
    assert str(candidates[0].url) == "https://radar.example.com/"
    assert policy.public_only is True
    assert policy.allow_authenticated_scraping is False
