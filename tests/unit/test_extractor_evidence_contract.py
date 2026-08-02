from __future__ import annotations

from datetime import UTC, datetime

from src.agents.extractor_agent import _build_evidence_item, _normalize_signal_text
from src.extraction.schemas import ConfidenceLevel, Evidence, SourceType, StartupProfile


def _profile(canonical: Evidence) -> StartupProfile:
    return StartupProfile(
        startup_name="Pix Force",
        website="https://pixforce.com/",
        country="Brazil",
        sector="Computer Vision",
        description="Industrial computer-vision company.",
        product_summary="AI inspection systems.",
        ai_signals=["computer vision", "artificial intelligence"],
        sources=[canonical],
        confidence_score=0.9,
    )


def test_extracted_evidence_envelope_satisfies_canonical_contract() -> None:
    canonical = Evidence(
        claim="Pix Force develops computer-vision systems for industrial inspection.",
        source_url="https://pixforce.com/",
        source_type=SourceType.OFFICIAL_SITE,
        quote_or_evidence="The official site describes AI systems that interpret images and videos.",
        confidence=ConfidenceLevel.HIGH,
        collected_at=datetime.now(UTC),
    )
    raw_text = "Pix Force develops computer-vision systems for industrial inspection."
    item = _build_evidence_item(
        {
            "text": raw_text,
            "source_url": "https://pixforce.com/",
            "source_id": "official-homepage",
            "collected_at": datetime.now(UTC).isoformat(),
        },
        _profile(canonical),
        SourceType.OFFICIAL_SITE,
    )

    parsed = Evidence.model_validate(item)
    assert parsed.claim == canonical.claim
    assert parsed.quote_or_evidence == canonical.quote_or_evidence
    assert parsed.confidence is ConfidenceLevel.HIGH
    assert item["evidence_id"]
    assert item["text"] == "pix force develops computer vision systems for industrial inspection"
    assert item["raw_text"] == raw_text
    assert item["source_id"] == "official-homepage"


def test_signal_normalization_handles_portuguese_diacritics_and_punctuation() -> None:
    assert (
        _normalize_signal_text("Visão computacional — inspeção visual em tempo real.")
        == "visao computacional inspecao visual em tempo real"
    )


def test_upstream_evidence_identifier_is_preserved() -> None:
    canonical = Evidence(
        claim="Pix Force develops computer vision systems.",
        source_url="https://pixforce.com/",
        source_type=SourceType.OFFICIAL_SITE,
        quote_or_evidence="Computer vision systems for industrial operations.",
        confidence=ConfidenceLevel.HIGH,
        collected_at=datetime.now(UTC),
    )
    item = _build_evidence_item(
        {
            "id": "persisted-evidence-id",
            "text": canonical.claim,
            "source_url": canonical.source_url,
            "source_id": "persisted_startup_evidence",
        },
        _profile(canonical),
        SourceType.OFFICIAL_SITE,
    )

    assert item["evidence_id"] == "persisted-evidence-id"
