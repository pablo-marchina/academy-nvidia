from __future__ import annotations

from datetime import UTC, datetime

from src.agents.extractor_agent import _build_evidence_item
from src.extraction.schemas import ConfidenceLevel, Evidence, SourceType, StartupProfile


def test_extracted_evidence_envelope_satisfies_canonical_contract() -> None:
    canonical = Evidence(
        claim="Pix Force develops computer-vision systems for industrial inspection.",
        source_url="https://pixforce.com/",
        source_type=SourceType.OFFICIAL_SITE,
        quote_or_evidence="The official site describes AI systems that interpret images and videos.",
        confidence=ConfidenceLevel.HIGH,
        collected_at=datetime.now(UTC),
    )
    profile = StartupProfile(
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

    item = _build_evidence_item(
        {
            "text": "Pix Force develops computer-vision systems for industrial inspection.",
            "source_url": "https://pixforce.com/",
            "source_id": "official-homepage",
            "collected_at": datetime.now(UTC).isoformat(),
        },
        profile,
        SourceType.OFFICIAL_SITE,
    )

    parsed = Evidence.model_validate(item)
    assert parsed.claim == canonical.claim
    assert parsed.quote_or_evidence == canonical.quote_or_evidence
    assert parsed.confidence is ConfidenceLevel.HIGH
    assert item["evidence_id"]
    assert item["text"]
    assert item["source_id"] == "official-homepage"
