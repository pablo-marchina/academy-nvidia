from __future__ import annotations

from src.diagnosis.gap_diagnosis_scoring import diagnose_gaps_quantitative
from src.diagnosis.schemas import GapType


def test_natural_quote_evidence_and_source_urls_make_relevant_gap_retrieval_eligible() -> None:
    evidence = [
        {
            "evidence_id": f"ev-{idx}",
            "source_url": f"https://source{idx}.example/case",
            "quote_or_evidence": (
                "Computer vision and drone imagery identify plantas daninhas using image analysis."
            ),
            "source_quality_score": 0.9,
            "evidence_confidence_score": 0.9,
            "confidence": "high",
        }
        for idx in range(3)
    ]

    summary = diagnose_gaps_quantitative(
        run_id="live-evidence-test",
        evidence_items=evidence,
        accepted_evidence_items=evidence,
        collection_metrics={
            "source_category_count": 2,
            "minimums": {"source_category_count": 2},
        },
        extraction_metrics={"total_extractions": 3, "failed_extractions": 0},
    )

    cv_gap = next(g for g in summary.gaps if g.gap_type == GapType.COMPUTER_VISION_GAP)
    assert cv_gap.production_allowed is True
    assert cv_gap.thresholds["observed_evidence_coverage"] == 1.0
    assert cv_gap.features.confidence.supporting_source_count > 0.0
    assert cv_gap.features.confidence.source_category_coverage == 1.0
    assert len(cv_gap.supporting_evidence_ids) == 3


def test_unrelated_gap_is_not_created_from_silence() -> None:
    evidence = [
        {
            "evidence_id": f"ev-{idx}",
            "source_url": f"https://source{idx}.example/case",
            "quote_or_evidence": "Computer vision detects weeds in drone imagery.",
            "source_quality_score": 0.9,
            "evidence_confidence_score": 0.9,
            "confidence": "high",
        }
        for idx in range(3)
    ]

    summary = diagnose_gaps_quantitative(
        run_id="no-false-gap-test",
        evidence_items=evidence,
        accepted_evidence_items=evidence,
    )

    cyber_gap = next(g for g in summary.gaps if g.gap_type == GapType.CYBERSECURITY_AI_GAP)
    assert cyber_gap.production_allowed is False
    assert cyber_gap.supporting_evidence_ids == []
