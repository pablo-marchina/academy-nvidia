from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.extraction.schemas import (
    ConfidenceLevel,
    Evidence,
    ImplementationComplexity,
    NvidiaRecommendation,
    RecommendationPriority,
    SourceType,
    StartupProfile,
    TechnicalGap,
)


def make_evidence() -> Evidence:
    return Evidence(
        claim="Startup states it offers AI copilots.",
        source_url="https://example.com/blog/ai-copilots",
        source_type=SourceType.BLOG,
        quote_or_evidence="We launched AI copilots for operations teams.",
        confidence=ConfidenceLevel.MEDIUM,
        collected_at=datetime.now(timezone.utc),
    )


def test_startup_profile_creation() -> None:
    profile = StartupProfile(
        startup_name="Example AI",
        website="https://example.com",
        sector="SaaS",
        description="Fictional example for tests.",
        product_summary="An operations platform with AI workflows.",
        ai_signals=["Mentions AI copilots"],
        sources=[make_evidence()],
        confidence_score=0.8,
    )
    assert profile.country == "Brazil"
    assert profile.sources[0].source_type == SourceType.BLOG


def test_evidence_creation() -> None:
    evidence = make_evidence()
    assert evidence.confidence == ConfidenceLevel.MEDIUM


def test_nvidia_recommendation_creation() -> None:
    recommendation = NvidiaRecommendation(
        startup_name="Example AI",
        diagnosed_gap=TechnicalGap.HIGH_INFERENCE_COST,
        recommended_nvidia_technologies=["TensorRT-LLM"],
        technical_justification="Inference cost can be optimized with accelerated serving.",
        business_justification="Lower cost improves gross margin for AI-heavy workloads.",
        priority=RecommendationPriority.HIGH,
        implementation_complexity=ImplementationComplexity.MEDIUM,
        next_action_for_nvidia_team="Validate current inference architecture with the startup.",
        evidence_used=[make_evidence()],
    )
    assert recommendation.priority == RecommendationPriority.HIGH


def test_enum_validation() -> None:
    evidence = Evidence(
        claim="Example claim",
        source_url="https://example.com",
        source_type="official_site",
        quote_or_evidence="Example evidence",
        confidence="high",
        collected_at=datetime.now(timezone.utc),
    )
    assert evidence.source_type == SourceType.OFFICIAL_SITE


def test_invalid_confidence_rejected() -> None:
    with pytest.raises(ValidationError):
        Evidence(
            claim="Example claim",
            source_url="https://example.com",
            source_type="official_site",
            quote_or_evidence="Example evidence",
            confidence="certain",
            collected_at=datetime.now(timezone.utc),
        )
