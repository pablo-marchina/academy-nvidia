"""Tests for _run_quality_gates consuming ranking_status and recommendation calibration."""

from __future__ import annotations

from typing import Any

from src.agents.graph import _run_quality_gates


def _make_state(
    *,
    ranking_status: str | None = "passed",
    nvidia_recommendation_metrics: dict[str, Any] | None = None,
    nvidia_recommendations: list[dict[str, Any]] | None = None,
    unsupported_critical_claims_count: int = 0,
    blockers: list[str] | None = None,
    evidence_items: list[dict[str, Any]] | None = None,
    rag_contexts: list[str] | None = None,
    gap_diagnosis_status: str | None = "passed",
    gap_diagnosis_metrics: dict[str, Any] | None = None,
    rag_retrieval_status: str | None = "passed",
    evidence_validation: dict[str, Any] | None = None,
    startup_scoring_summary: dict[str, Any] | None = None,
    nvidia_mapping_summary: dict[str, Any] | None = None,
    executed_nodes: list[str] | None = None,
    nvidia_recommendation_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if nvidia_recommendation_metrics is None:
        nvidia_recommendation_metrics = {
            "ranking_status": ranking_status or "",
            "recommendation_count": 1,
            "average_recommendation_priority_score": 0.75,
            "average_recommendation_confidence": 0.7,
            "rag_supported_recommendation_rate": 1.0,
            "evidence_supported_recommendation_rate": 1.0,
            "missing_recommendation_calibration_count": 0,
        }
    if nvidia_recommendations is None:
        nvidia_recommendations = [
            {
                "gap_type": "inference_performance_gap",
                "nvidia_technology": "TensorRT",
                "production_allowed": True,
                "blockers": [],
                "recommendation_priority_score": 0.85,
                "confidence": 0.8,
                "supporting_rag_context_ids": ["rag-1"],
                "supporting_evidence_ids": ["ev-1"],
                "calibration_decision_ids": [
                    "recommendation.priority_score_weights",
                    "recommendation.production_threshold",
                ],
            },
        ]
    if blockers is None:
        blockers = []
    if evidence_items is None:
        evidence_items = [{"url": "https://example.com", "text": "evidence"}]
    if rag_contexts is None:
        rag_contexts = ["ctx1"]
    if gap_diagnosis_metrics is None:
        gap_diagnosis_metrics = {
            "total_gap_count": 1,
            "production_allowed_gap_count": 1,
            "blocked_gap_count": 0,
            "missing_calibration_count": 0,
        }
    if evidence_validation is None:
        evidence_validation = {"status": "passed"}
    if startup_scoring_summary is None:
        startup_scoring_summary = {"scoring_status": "passed"}
    if nvidia_mapping_summary is None:
        nvidia_mapping_summary = {"mapping_status": "passed"}
    if executed_nodes is None:
        executed_nodes = []

    return {
        "executed_nodes": executed_nodes,
        "unsupported_critical_claims_count": unsupported_critical_claims_count,
        "blockers": blockers,
        "evidence_items": evidence_items,
        "rag_contexts": rag_contexts,
        "nvidia_recommendations": nvidia_recommendations,
        "nvidia_recommendation_metrics": nvidia_recommendation_metrics,
        "nvidia_recommendation_summary": nvidia_recommendation_summary or {},
        "gap_diagnosis_status": gap_diagnosis_status,
        "gap_diagnosis_metrics": gap_diagnosis_metrics,
        "rag_retrieval_status": rag_retrieval_status,
        "evidence_validation": evidence_validation,
        "startup_scoring_summary": startup_scoring_summary,
        "nvidia_mapping_summary": nvidia_mapping_summary,
    }


class TestQualityGatesRankingBlocked:
    def test_ranking_blocked_no_mappings_blocks_quality(self) -> None:
        state = _make_state(
            ranking_status="blocked_no_nvidia_mappings",
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert any("blocked_no_nvidia_mappings" in c for c in quality["failed_checks"])

    def test_ranking_blocked_uncalibrated_mapping_blocks_quality(self) -> None:
        state = _make_state(
            ranking_status="blocked_uncalibrated_mapping",
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert any("blocked_uncalibrated_mapping" in c for c in quality["failed_checks"])

    def test_ranking_blocked_uncalibrated_recommendation_blocks_quality(self) -> None:
        state = _make_state(
            ranking_status="blocked_uncalibrated_recommendation",
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert any("blocked_uncalibrated_recommendation" in c for c in quality["failed_checks"])

    def test_ranking_failed_blocks_quality(self) -> None:
        state = _make_state(
            ranking_status="failed",
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert any("failed" in c for c in quality["failed_checks"])

    def test_ranking_needs_review_warns_quality(self) -> None:
        state = _make_state(
            ranking_status="needs_review",
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert any("needs_review" in c for c in quality["warning_checks"])

    def test_missing_ranking_status_blocks_quality(self) -> None:
        state = _make_state(
            ranking_status=None,
            nvidia_recommendation_metrics={},
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert any("missing" in c.lower() for c in quality["failed_checks"])


class TestQualityGatesRecommendationProduction:
    def test_recommendation_not_production_allowed_blocks_quality(self) -> None:
        state = _make_state(
            ranking_status="passed",
            nvidia_recommendations=[
                {
                    "gap_type": "inference_performance_gap",
                    "nvidia_technology": "TensorRT",
                    "production_allowed": False,
                    "blockers": ["Mapping score below production threshold"],
                    "recommendation_priority_score": 0.3,
                    "confidence": 0.3,
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                    "calibration_decision_ids": [],
                },
            ],
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"

    def test_recommendation_blocked_by_calibration_fails(self) -> None:
        state = _make_state(
            ranking_status="passed",
            nvidia_recommendations=[
                {
                    "gap_type": "inference_performance_gap",
                    "nvidia_technology": "TensorRT",
                    "production_allowed": False,
                    "blockers": ["Calibration decisions missing for recommendation"],
                    "recommendation_priority_score": 0.0,
                    "confidence": 0.0,
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                    "calibration_decision_ids": [],
                },
            ],
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert "calibrat" in quality["status"] or "failed" in quality["status"]


class TestQualityGatesAllGreen:
    def test_all_green_passes_quality(self) -> None:
        state = _make_state()
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] == "passed"
        assert result["status"] == "quality_passed"
        assert result["review_required"] is False

    def test_quality_metrics_contain_recommendation_fields(self) -> None:
        state = _make_state()
        result = _run_quality_gates(state)
        metrics = result["quality"]["metrics"]
        expected_fields = [
            "recommendation_count",
            "production_allowed_recommendation_count",
            "blocked_recommendation_count",
            "needs_review_recommendation_count",
            "average_recommendation_priority_score",
            "average_recommendation_confidence",
            "rag_supported_recommendation_rate",
            "evidence_supported_recommendation_rate",
            "missing_recommendation_calibration_count",
            "ranking_status",
            "mapping_status",
            "scoring_status",
        ]
        for field in expected_fields:
            assert field in metrics, f"Missing quality metric: {field}"

    def test_gaps_evidence_rag_scoring_mapping_all_green(self) -> None:
        state = _make_state()
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] == "passed"
        assert quality["failed_checks"] == []


class TestQualityGatesUnsupportedCriticalClaims:
    def test_unsupported_critical_claim_blocks(self) -> None:
        state = _make_state(
            unsupported_critical_claims_count=2,
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert any("unsupported_critical_claims" in c for c in quality["failed_checks"])

    def test_zero_unsupported_critical_claims_allows(self) -> None:
        state = _make_state(
            unsupported_critical_claims_count=0,
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] == "passed"


class TestQualityGatesMissingCalibration:
    def test_missing_recommendation_calibration_blocks_quality(self) -> None:
        state = _make_state(
            ranking_status="passed",
            nvidia_recommendation_metrics={
                "ranking_status": "passed",
                "missing_recommendation_calibration_count": 6,
            },
        )
        result = _run_quality_gates(state)
        quality = result["quality"]
        assert quality["status"] != "passed"
        assert "blocked_uncalibrated" in quality["status"] or "failed" in quality["status"]


class TestQualityGatesNoExternalCalls:
    def test_no_llm_qdrant_scraping_imported(self) -> None:
        import sys as _sys

        before = set(_sys.modules.keys())
        state = _make_state()
        result = _run_quality_gates(state)
        assert result is not None
        after = set(_sys.modules.keys())
        new = after - before
        banned = {"langchain", "qdrant_client", "playwright", "openai", "anthropic"}
        triggered = {m for m in new if any(b in m for b in banned)}
        assert not triggered, f"Banned imports triggered: {triggered}"
