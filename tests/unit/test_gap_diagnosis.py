"""Tests for deterministic gap diagnosis."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import HttpUrl

from src.classification.ai_native_classifier import ClassificationResult
from src.diagnosis.gap_diagnosis import diagnose_gaps
from src.diagnosis.nvidia_mapping import build_technology_candidates
from src.diagnosis.schemas import EvidenceTag, GapDiagnosisResult, GapWithEvidence
from src.extraction.schemas import (
    AINativeLevel,
    ConfidenceLevel,
    SourceType,
    StartupProfile,
)
from src.validation.evidence_validator import EvidenceKind, ValidatedEvidence

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_evidence(
    claim: str,
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH,
    evidence_kind: EvidenceKind = EvidenceKind.FACT,
    quote: str = "The company uses AI for core features.",
) -> ValidatedEvidence:
    return ValidatedEvidence(
        claim=claim,
        source_url=HttpUrl("https://example.com"),
        source_type=SourceType.OFFICIAL_SITE,
        quote_or_evidence=quote,
        confidence=confidence,
        evidence_kind=evidence_kind,
        collected_at=datetime.now(timezone.utc),  # noqa: UP017
    )


def _make_profile(
    sector: str = "Technology",
    ai_signals: list[str] | None = None,
    tech_stack: list[str] | None = None,
    description: str = "A technology company building software.",
    product_summary: str = "Building software solutions.",
    customers: list[str] | None = None,
    funding: list[str] | None = None,
) -> StartupProfile:
    return StartupProfile(
        startup_name="Test Startup",
        website=HttpUrl("https://example.com"),
        sector=sector,
        description=description,
        product_summary=product_summary,
        ai_signals=ai_signals or [],
        tech_stack_signals=tech_stack or [],
        customers=customers or [],
        funding_signals=funding or [],
        sources=[],
        confidence_score=0.5,
    )


def _make_classification(
    level: AINativeLevel = AINativeLevel.AI_ENABLED,
) -> ClassificationResult:
    return ClassificationResult(
        startup_name="Test Startup",
        classification=level,
        confidence=ConfidenceLevel.HIGH,
        reasoning=f"Classified as {level.value}.",
    )


# ---------------------------------------------------------------------------
# Scenario tests
# ---------------------------------------------------------------------------


class TestGapDiagnosis:
    def test_external_api_gap(self) -> None:
        """Startup using 'gpt' and 'openai' should trigger external_api_dependency."""
        profile = _make_profile(
            tech_stack=["Python", "openai", "gpt"],
            ai_signals=["AI signal: llm", "AI signal: gpt"],
            description="We build LLM-powered chatbots using OpenAI GPT-4.",
            product_summary="Chatbot platform using GPT API.",
        )
        evidence = [
            _make_evidence("Uses OpenAI GPT-4 for core features", ConfidenceLevel.HIGH),
        ]
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(),
            evidence,
        )
        gap = _find_gap(result, "external_api_dependency")
        assert gap is not None
        assert gap.detected
        assert gap.evidence_tag == EvidenceTag.FACT

    def test_inference_cost_gap(self) -> None:
        """Startup with high-volume inference without NVIDIA tech."""
        profile = _make_profile(
            tech_stack=["Python", "Flask"],
            ai_signals=["AI signal: inference", "AI signal: high volume"],
            description="High-volume inference serving thousands of requests per second.",
            product_summary="Real-time inference API.",
        )
        evidence = [
            _make_evidence(
                "High-volume inference without GPU acceleration",
                ConfidenceLevel.MEDIUM,
            ),
        ]
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.AI_NATIVE),
            evidence,
        )
        gap = _find_gap(result, "high_inference_cost")
        assert gap is not None
        assert gap.detected

    def test_agent_governance_gap(self) -> None:
        """Startup building AI agents without guardrails."""
        profile = _make_profile(
            tech_stack=["Python", "LangChain"],
            ai_signals=["AI signal: agent", "AI signal: autonomous"],
            description="Multi-agent system for enterprise workflow automation.",
            product_summary="Autonomous AI agents for business processes.",
        )
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.AI_NATIVE),
            [],
        )
        gap = _find_gap(result, "agent_governance_gap")
        assert gap is not None
        assert gap.detected

    def test_voice_gap(self) -> None:
        """Startup in call center with voice/speech should detect voice_need."""
        profile = _make_profile(
            sector="Customer Service",
            ai_signals=["AI signal: voice", "AI signal: speech-to-text"],
            tech_stack=["Python"],
            description="Voicebot for customer service call centers.",
            product_summary="Speech-to-text analytics platform for calls.",
        )
        evidence = [
            _make_evidence("Voicebot platform for call centers", ConfidenceLevel.HIGH),
        ]
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.AI_ENABLED),
            evidence,
        )
        gap = _find_gap(result, "voice_need")
        assert gap is not None
        assert gap.detected
        assert gap.evidence_tag == EvidenceTag.FACT

    def test_healthcare_gap(self) -> None:
        """HealthTech sector should detect healthcare_compliance_need."""
        profile = _make_profile(
            sector="HealthTech",
            ai_signals=["AI signal: medical imaging"],
            tech_stack=["Python", "PyTorch"],
            description="AI-powered medical diagnosis platform.",
            product_summary="Medical imaging analysis for hospitals.",
        )
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.AI_NATIVE),
            [],
        )
        gap = _find_gap(result, "healthcare_compliance_need")
        assert gap is not None
        assert gap.detected

    def test_no_gaps_clean(self) -> None:
        """Generic startup with no AI signals should detect few or no gaps."""
        profile = _make_profile(
            sector="E-commerce",
            tech_stack=["WordPress"],
            ai_signals=[],
            description="Online store selling handmade products.",
            product_summary="E-commerce platform for artisans.",
        )
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.NON_AI),
            [],
        )
        detected = [g for g in result.diagnosed_gaps if g.detected]
        assert len(detected) <= 2

    def test_inferred_gap_weak_evidence(self) -> None:
        """Gap detected by keyword in profile without direct evidence should be inferred."""
        profile = _make_profile(
            tech_stack=["Python"],
            ai_signals=["AI signal: computer vision"],
            description="Using computer vision for quality inspection.",
            product_summary="CV inspection system.",
        )
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.AI_ENABLED),
            [],
        )
        gap = _find_gap(result, "computer_vision_need")
        assert gap is not None
        assert gap.detected
        assert gap.evidence_tag == EvidenceTag.INFERRED

    def test_full_pipeline_with_mapping(self) -> None:
        """End-to-end: diagnose gaps then build technology candidates."""
        profile = _make_profile(
            sector="HealthTech",
            tech_stack=["Python", "openai", "gpt"],
            ai_signals=[
                "AI signal: voice",
                "AI signal: speech-to-text",
                "AI signal: agent",
                "AI signal: autonomous",
            ],
            description="Voice AI agents for healthcare call centers.",
            product_summary="Speech-enabled agents for patient intake.",
        )
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.AI_NATIVE),
            [],
        )
        assert isinstance(result, GapDiagnosisResult)
        assert len(result.diagnosed_gaps) == 15
        detected = [g for g in result.diagnosed_gaps if g.detected]
        assert len(detected) >= 2

        candidates = build_technology_candidates(result.diagnosed_gaps)
        assert len(candidates) >= 1
        for c in candidates:
            assert c.technology_name
            assert c.justification
            assert c.addresses_gap

    def test_missing_evidence_reported(self) -> None:
        """Inferred gaps should produce missing_evidence entries."""
        profile = _make_profile(
            tech_stack=["Python"],
            ai_signals=["AI signal: robotics"],
            description="Robotics startup building autonomous drones.",
            product_summary="Drone navigation system.",
        )
        result = diagnose_gaps(
            "Test Startup",
            profile,
            _make_classification(AINativeLevel.AI_ENABLED),
            [],
        )
        assert len(result.missing_evidence) > 0
        for msg in result.missing_evidence:
            assert "inference" in msg or "inferred" in msg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_gap(result: GapDiagnosisResult, gap_value: str) -> GapWithEvidence | None:
    for g in result.diagnosed_gaps:
        if g.gap.value == gap_value:
            return g
    return None
