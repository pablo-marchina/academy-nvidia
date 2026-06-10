from datetime import UTC, datetime

from src.classification.ai_native_classifier import ClassificationResult
from src.diagnosis.schemas import (
    EvidenceTag,
    GapDiagnosisResult,
    GapWithEvidence,
    NvidiaTechnologyCandidate,
)
from src.extraction.schemas import (
    AINativeLevel,
    ConfidenceLevel,
    StartupProfile,
    TechnicalGap,
)
from src.recommendation.recommendation_engine import (
    _compute_overall_confidence,
    _compute_overall_priority,
    _determine_action,
    _determine_priority,
    _suggest_experiment,
    build_per_gap_recommendation,
    build_recommendations,
)
from src.recommendation.schemas import (
    RecommendedNextAction,
    SuggestedTechnicalExperiment,
)
from src.validation.evidence_validator import EvidenceKind, ValidatedEvidence


def _make_profile() -> StartupProfile:
    return StartupProfile(
        startup_name="TestAI",
        website="https://testai.com",
        sector="SaaS",
        description="A test startup.",
        product_summary="AI platform.",
        ai_signals=["AI copilot"],
        sources=[],
        confidence_score=0.8,
    )


def _make_classification() -> ClassificationResult:
    return ClassificationResult(
        startup_name="TestAI",
        classification=AINativeLevel.AI_NATIVE,
        confidence=ConfidenceLevel.HIGH,
        reasoning="Test classification.",
    )


def _make_gap(
    gap: TechnicalGap = TechnicalGap.HIGH_INFERENCE_COST,
    detected: bool = True,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    tag: EvidenceTag = EvidenceTag.FACT,
) -> GapWithEvidence:
    return GapWithEvidence(
        gap=gap,
        detected=detected,
        confidence=confidence,
        evidence_tag=tag,
        reasoning="Test reasoning.",
        evidence_used=[
            ValidatedEvidence(
                claim="Test claim",
                source_url="https://test.com",
                source_type="official_site",
                quote_or_evidence="Test quote",
                confidence=ConfidenceLevel.HIGH,
                collected_at=datetime.now(UTC),
                evidence_kind=EvidenceKind.FACT,
            )
        ],
    )


def _make_diagnosis(
    gaps: list[GapWithEvidence] | None = None,
) -> GapDiagnosisResult:
    if gaps is None:
        gaps = [_make_gap()]
    return GapDiagnosisResult(
        startup_name="TestAI",
        diagnosed_gaps=gaps,
        nvidia_technology_candidates=[
            NvidiaTechnologyCandidate(
                technology_name="TensorRT-LLM",
                addresses_gap=TechnicalGap.HIGH_INFERENCE_COST,
                justification="Direct match.",
            ),
        ],
        confidence=ConfidenceLevel.HIGH,
        reasoning="Test diagnosis.",
        missing_evidence=["More data needed."],
    )


def _make_validated_evidence() -> list[ValidatedEvidence]:
    return [
        ValidatedEvidence(
            claim="Evidence claim.",
            source_url="https://test.com",
            source_type="official_site",
            quote_or_evidence="Quote.",
            confidence=ConfidenceLevel.HIGH,
            collected_at=datetime.now(UTC),
            evidence_kind=EvidenceKind.FACT,
        ),
    ]


class TestDetermineAction:
    def test_not_recommended_motion_returns_not_recommended(self) -> None:
        gap = _make_gap()
        action = _determine_action(gap, "not_recommended")
        assert action == RecommendedNextAction.NOT_RECOMMENDED

    def test_not_detected_returns_monitor(self) -> None:
        gap = _make_gap(detected=False)
        action = _determine_action(gap, "immediate_outreach")
        assert action == RecommendedNextAction.MONITOR

    def test_low_confidence_returns_validate_manually(self) -> None:
        gap = _make_gap(confidence=ConfidenceLevel.LOW)
        action = _determine_action(gap, "immediate_outreach")
        assert action == RecommendedNextAction.VALIDATE_MANUALLY

    def test_lack_evidence_motion_returns_validate_manually(self) -> None:
        gap = _make_gap()
        action = _determine_action(gap, "lack_evidence_more_research")
        assert action == RecommendedNextAction.VALIDATE_MANUALLY

    def test_high_confidence_immediate_outreach_returns_approach_now(self) -> None:
        gap = _make_gap()
        action = _determine_action(gap, "immediate_outreach")
        assert action == RecommendedNextAction.APPROACH_NOW

    def test_medium_confidence_approach_now(self) -> None:
        gap = _make_gap(confidence=ConfidenceLevel.MEDIUM)
        action = _determine_action(gap, "immediate_outreach")
        assert action == RecommendedNextAction.VALIDATE_MANUALLY

    def test_medium_confidence_monitor_motion_returns_monitor(self) -> None:
        gap = _make_gap(confidence=ConfidenceLevel.MEDIUM)
        action = _determine_action(gap, "monitor_and_nurture")
        assert action == RecommendedNextAction.MONITOR


class TestDeterminePriority:
    def test_approach_now_high_confidence(self) -> None:
        p = _determine_priority(RecommendedNextAction.APPROACH_NOW, ConfidenceLevel.HIGH)
        from src.extraction.schemas import RecommendationPriority

        assert p == RecommendationPriority.HIGH

    def test_approach_now_medium_confidence(self) -> None:
        from src.extraction.schemas import RecommendationPriority

        p = _determine_priority(RecommendedNextAction.APPROACH_NOW, ConfidenceLevel.MEDIUM)
        assert p == RecommendationPriority.MEDIUM

    def test_validate_manually_returns_medium_or_low(self) -> None:
        from src.extraction.schemas import RecommendationPriority

        p_high = _determine_priority(RecommendedNextAction.VALIDATE_MANUALLY, ConfidenceLevel.HIGH)
        assert p_high == RecommendationPriority.MEDIUM
        p_low = _determine_priority(RecommendedNextAction.VALIDATE_MANUALLY, ConfidenceLevel.LOW)
        assert p_low == RecommendationPriority.LOW

    def test_monitor_returns_low(self) -> None:
        from src.extraction.schemas import RecommendationPriority

        p = _determine_priority(RecommendedNextAction.MONITOR, ConfidenceLevel.HIGH)
        assert p == RecommendationPriority.LOW


class TestComputeOverall:
    def test_overall_priority_with_high(self) -> None:
        from src.extraction.schemas import RecommendationPriority
        from src.recommendation.schemas import PerGapRecommendation

        recs = [
            PerGapRecommendation(
                diagnosed_gap=TechnicalGap.HIGH_INFERENCE_COST,
                detected=True,
                priority=RecommendationPriority.HIGH,
                confidence=ConfidenceLevel.HIGH,
            ),
            PerGapRecommendation(
                diagnosed_gap=TechnicalGap.HIGH_LATENCY,
                detected=True,
                priority=RecommendationPriority.LOW,
                confidence=ConfidenceLevel.MEDIUM,
            ),
        ]
        assert _compute_overall_priority(recs) == RecommendationPriority.HIGH

    def test_overall_confidence_with_mixed(self) -> None:
        from src.recommendation.schemas import PerGapRecommendation

        recs = [
            PerGapRecommendation(
                diagnosed_gap=TechnicalGap.HIGH_INFERENCE_COST,
                detected=True,
                priority="high",
                confidence=ConfidenceLevel.HIGH,
            ),
            PerGapRecommendation(
                diagnosed_gap=TechnicalGap.HIGH_LATENCY,
                detected=True,
                priority="low",
                confidence=ConfidenceLevel.MEDIUM,
            ),
        ]
        assert _compute_overall_confidence(recs) == ConfidenceLevel.MEDIUM

    def test_no_detected_gaps_low_confidence(self) -> None:
        from src.recommendation.schemas import PerGapRecommendation

        recs = [
            PerGapRecommendation(
                diagnosed_gap=TechnicalGap.HIGH_INFERENCE_COST,
                detected=False,
                priority="low",
                confidence=ConfidenceLevel.LOW,
            ),
        ]
        assert _compute_overall_confidence(recs) == ConfidenceLevel.LOW


class TestSuggestExperiment:
    def test_known_gap_returns_experiment(self) -> None:
        experiment = _suggest_experiment(TechnicalGap.HIGH_INFERENCE_COST, "TensorRT-LLM")
        assert experiment is not None
        assert isinstance(experiment, SuggestedTechnicalExperiment)
        assert "TensorRT-LLM" in experiment.nvidia_technology
        assert experiment.target_gap == TechnicalGap.HIGH_INFERENCE_COST

    def test_unknown_gap_returns_none(self) -> None:
        experiment = _suggest_experiment(
            TechnicalGap.SLOW_DATA_PIPELINE,
            "cuDF",
        )
        assert experiment is not None
        assert "cuDF" in experiment.nvidia_technology


class TestBuildPerGap:
    def test_detected_high_confidence_generates_full_recommendation(self) -> None:
        profile = _make_profile()
        classification = _make_classification()
        gap = _make_gap()

        rec = build_per_gap_recommendation(
            gap=gap,
            tech_names=["TensorRT-LLM"],
            profile=profile,
            classification=classification,
            recommended_motion="immediate_outreach",
        )
        assert rec.detected is True
        assert rec.action == RecommendedNextAction.APPROACH_NOW
        assert len(rec.recommended_nvidia_technologies) == 1
        assert rec.suggested_experiment is not None
        assert rec.priority.value == "high"

    def test_undetected_gap_generates_monitor_action(self) -> None:
        profile = _make_profile()
        classification = _make_classification()
        gap = _make_gap(detected=False)

        rec = build_per_gap_recommendation(
            gap=gap,
            tech_names=[],
            profile=profile,
            classification=classification,
            recommended_motion="immediate_outreach",
        )
        assert rec.detected is False
        assert rec.action == RecommendedNextAction.MONITOR
        assert rec.suggested_experiment is None
        assert rec.recommended_nvidia_technologies == []

    def test_inferred_evidence_adds_missing_evidence_entry(self) -> None:
        profile = _make_profile()
        classification = _make_classification()
        gap = _make_gap(tag=EvidenceTag.INFERRED)

        rec = build_per_gap_recommendation(
            gap=gap,
            tech_names=["TensorRT-LLM"],
            profile=profile,
            classification=classification,
            recommended_motion="immediate_outreach",
        )
        assert len(rec.missing_evidence) == 1
        assert "inference" in rec.missing_evidence[0].lower()


class TestBuildRecommendations:
    def test_full_integration_returns_result(self) -> None:
        profile = _make_profile()
        classification = _make_classification()
        evidence = _make_validated_evidence()
        diagnosis = _make_diagnosis()

        result = build_recommendations(
            startup_name="TestAI",
            profile=profile,
            classification=classification,
            validated_evidence=evidence,
            defensibility=None,
            inception_fit=None,
            production_readiness=None,
            composite=None,
            final_priority_score=0.85,
            recommended_motion="immediate_outreach",
            gap_diagnosis=diagnosis,
        )
        assert result.startup_name == "TestAI"
        assert len(result.recommendations) == 1
        assert result.top_recommendation is not None
        assert result.top_recommendation.action == RecommendedNextAction.APPROACH_NOW

    def test_multiple_gaps_all_approach_now(self) -> None:
        gap1 = _make_gap(TechnicalGap.HIGH_INFERENCE_COST)
        gap2 = _make_gap(TechnicalGap.HIGH_LATENCY, confidence=ConfidenceLevel.HIGH)
        diagnosis = _make_diagnosis([gap1, gap2])

        result = build_recommendations(
            startup_name="TestAI",
            profile=_make_profile(),
            classification=_make_classification(),
            validated_evidence=_make_validated_evidence(),
            defensibility=None,
            inception_fit=None,
            production_readiness=None,
            composite=None,
            final_priority_score=0.85,
            recommended_motion="immediate_outreach",
            gap_diagnosis=diagnosis,
        )
        assert len(result.recommendations) == 2
        approach = [
            r for r in result.recommendations if r.action == RecommendedNextAction.APPROACH_NOW
        ]
        assert len(approach) == 2

    def test_reasoning_contains_startup_name_and_gap_count(self) -> None:
        gap = _make_gap(TechnicalGap.SLOW_DATA_PIPELINE)
        diagnosis = _make_diagnosis([gap])

        result = build_recommendations(
            startup_name="TestAI",
            profile=_make_profile(),
            classification=_make_classification(),
            validated_evidence=_make_validated_evidence(),
            defensibility=None,
            inception_fit=None,
            production_readiness=None,
            composite=None,
            final_priority_score=0.85,
            recommended_motion="high_priority_outreach",
            gap_diagnosis=diagnosis,
        )
        assert "TestAI" in result.reasoning
        assert "Gaps diagnosed: 1" in result.reasoning
