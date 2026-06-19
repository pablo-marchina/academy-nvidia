"""Tests for quantitative ActionBrief generation.

Validates that generate_brief produces 100% quantitative, evidence-grounded,
blocking output with no LLM, Qdrant, scraping, or invented text.
"""

from __future__ import annotations

from typing import Any
from src.agents.graph import _generate_brief


def _state_with_recs(
    *,
    production_allowed: bool = True,
    nvidia_recommendations: list[dict[str, Any]] | None = None,
    ranking_status: str | None = "passed",
    unsupported_critical_claims_count: int = 0,
    quality: dict[str, Any] | None = None,
    run_id: str = "test-brief-001",
    startup_id: str | None = "startup-42",
    startup_name: str | None = "TestAI",
    scores: dict[str, Any] | None = None,
    gap_diagnosis_metrics: dict[str, Any] | None = None,
    evidence_validation_metrics: dict[str, Any] | None = None,
    accepted_evidence_items: list[dict[str, Any]] | None = None,
    evidence_items: list[dict[str, Any]] | None = None,
    claims: list[dict[str, Any]] | None = None,
    rag_contexts: list[str] | None = None,
    nvidia_rec_metrics: dict[str, Any] | None = None,
    executed_nodes: list[str] | None = None,
    blockers: list[str] | None = None,
    **overrides: Any,
) -> dict[str, Any]:
    if scores is None:
        scores = {"ai_native_score": 0.75, "nvidia_fit_score": 0.65}
    if gap_diagnosis_metrics is None:
        gap_diagnosis_metrics = {
            "total_gap_count": 2,
            "production_allowed_gap_count": 2,
            "blocked_gap_count": 0,
            "average_gap_severity": 0.7,
            "average_gap_confidence": 0.65,
        }
    if evidence_validation_metrics is None:
        evidence_validation_metrics = {
            "accepted_evidence_count": 3,
            "unsupported_critical_claims_count": 0,
        }
    if accepted_evidence_items is None:
        accepted_evidence_items = [
            {"id": "ev_0", "claim": "Uses OpenAI API"},
            {"id": "ev_1", "claim": "High inference cost"},
        ]
    if evidence_items is None:
        evidence_items = list(accepted_evidence_items)
    if claims is None:
        claims = [
            {"claim_text": "Uses external API for inference", "criticality": "normal", "support_status": "supported"},
            {"claim_text": "High inference cost on current cloud", "criticality": "critical", "support_status": "supported"},
        ]
    if rag_contexts is None:
        rag_contexts = ["NVIDIA NIM reduces cost", "TensorRT-LLM optimizes LLM"]
    if nvidia_recommendations is None:
        nvidia_recommendations = [
            {
                "recommendation_id": "rec-test-001-0",
                "gap_id": "gap-ext-api",
                "gap_type": "external_api_dependency",
                "nvidia_technology": "NVIDIA NIM",
                "mapping_score": 0.8,
                "mapping_confidence": 0.75,
                "recommendation_priority_score": 0.85,
                "confidence": 0.72,
                "uncertainty": 0.15,
                "business_impact": 0.7,
                "implementation_complexity": 0.3,
                "supporting_evidence_ids": ["ev_0"],
                "supporting_rag_context_ids": ["rag_0"],
                "calibration_decision_ids": ["recommendation.priority_score_weights"],
                "production_allowed": production_allowed,
                "blockers": [] if production_allowed else ["Mapping score below threshold"],
                "next_best_action": "Engage startup to discuss NVIDIA NIM",
                "reason": "Gap 'external_api_dependency' mapped to 'NVIDIA NIM'",
            },
        ]
    if nvidia_rec_metrics is None:
        nvidia_rec_metrics = {
            "mapping_count": 1,
            "recommendation_count": len(nvidia_recommendations),
            "production_allowed_recommendation_count": sum(
                1 for r in nvidia_recommendations if r.get("production_allowed", False)
            ),
            "blocked_recommendation_count": sum(
                1 for r in nvidia_recommendations if not r.get("production_allowed", False)
            ),
            "average_recommendation_priority_score": 0.85,
            "average_recommendation_confidence": 0.72,
            "recommendation_uncertainty_mean": 0.15,
            "evidence_supported_recommendation_rate": 1.0,
            "rag_supported_recommendation_rate": 1.0,
            "missing_recommendation_calibration_count": 0,
        }
    if executed_nodes is None:
        executed_nodes = [
            "preflight_configuration_check", "plan_search", "collect_sources",
            "extract_profile", "validate_evidence", "score_startup",
            "diagnose_gaps", "retrieve_nvidia_context", "build_technology_mappings",
            "rank_recommendations",
        ]
    if quality is None:
        quality = {"status": "passed", "failed_checks": [], "warning_checks": []}
    if blockers is None:
        blockers = []

    base: dict[str, Any] = {
        "run_id": run_id,
        "startup_id": startup_id,
        "startup_name": startup_name,
        "scores": scores,
        "gap_diagnosis_metrics": gap_diagnosis_metrics,
        "evidence_validation_metrics": evidence_validation_metrics,
        "accepted_evidence_items": accepted_evidence_items,
        "evidence_items": evidence_items,
        "claims": claims,
        "rag_contexts": rag_contexts,
        "nvidia_recommendations": nvidia_recommendations,
        "nvidia_recommendation_metrics": nvidia_rec_metrics,
        "ranking_status": ranking_status,
        "unsupported_critical_claims_count": unsupported_critical_claims_count,
        "quality": quality,
        "executed_nodes": executed_nodes,
        "blockers": blockers,
    }
    base.update(overrides)
    return base


# ── Test 1: only production_allowed=true recommendations in top_recommendations ──


class TestGenerateBriefProductionAllowed:
    def test_only_production_allowed_in_top(self) -> None:
        state = _state_with_recs(
            nvidia_recommendations=[
                {
                    "recommendation_id": "rec-1",
                    "gap_id": "gap-1",
                    "gap_type": "inference_performance_gap",
                    "nvidia_technology": "TensorRT",
                    "mapping_score": 0.8,
                    "mapping_confidence": 0.75,
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.72,
                    "uncertainty": 0.15,
                    "supporting_evidence_ids": ["ev_1"],
                    "supporting_rag_context_ids": ["rag_1"],
                    "calibration_decision_ids": [],
                    "production_allowed": True,
                    "blockers": [],
                    "next_best_action": "Engage on TensorRT",
                    "reason": "Gap 'inference' mapped to 'TensorRT'",
                },
                {
                    "recommendation_id": "rec-2",
                    "gap_id": "gap-2",
                    "gap_type": "data_pipeline_gap",
                    "nvidia_technology": "cuDF",
                    "mapping_score": 0.4,
                    "mapping_confidence": 0.3,
                    "recommendation_priority_score": 0.3,
                    "confidence": 0.25,
                    "uncertainty": 0.5,
                    "supporting_evidence_ids": [],
                    "supporting_rag_context_ids": [],
                    "calibration_decision_ids": [],
                    "production_allowed": False,
                    "blockers": ["Mapping score below production threshold"],
                    "next_best_action": "",
                    "reason": "Gap 'data_pipeline' mapped to 'cuDF'",
                },
            ],
        )
        result = _generate_brief(state)
        ab = result["action_brief"]
        assert len(ab["top_recommendations"]) == 1
        assert ab["top_recommendations"][0]["recommendation_id"] == "rec-1"

    def test_blocked_recs_not_in_top(self) -> None:
        state = _state_with_recs(
            nvidia_recommendations=[
                {
                    "recommendation_id": "rec-blocked",
                    "gap_id": "gap-b",
                    "gap_type": "mlops_deployment_gap",
                    "nvidia_technology": "NVIDIA AI Enterprise",
                    "mapping_score": 0.3,
                    "mapping_confidence": 0.2,
                    "recommendation_priority_score": 0.2,
                    "confidence": 0.15,
                    "uncertainty": 0.6,
                    "supporting_evidence_ids": [],
                    "supporting_rag_context_ids": [],
                    "calibration_decision_ids": [],
                    "production_allowed": False,
                    "blockers": ["Uncalibrated mapping"],
                    "next_best_action": "",
                    "reason": "Blocked",
                },
            ],
            nvidia_rec_metrics={
                "recommendation_count": 1,
                "production_allowed_recommendation_count": 0,
                "blocked_recommendation_count": 1,
                "average_recommendation_priority_score": 0.2,
                "average_recommendation_confidence": 0.15,
                "recommendation_uncertainty_mean": 0.6,
                "evidence_supported_recommendation_rate": 0.0,
                "rag_supported_recommendation_rate": 0.0,
                "missing_recommendation_calibration_count": 1,
            },
        )
        result = _generate_brief(state)
        ab = result["action_brief"]
        assert len(ab["top_recommendations"]) == 0
        brief_status = ab["brief_status"]
        assert "blocked" in brief_status or brief_status == "blocked_no_production_recommendations"


# ── Test 2: no production recommendations blocks brief ──


class TestGenerateBriefNoProduction:
    def test_no_production_recommendations_blocks(self) -> None:
        state = _state_with_recs(
            nvidia_recommendations=[],
            nvidia_rec_metrics={
                "recommendation_count": 0,
                "production_allowed_recommendation_count": 0,
                "blocked_recommendation_count": 0,
                "average_recommendation_priority_score": 0.0,
                "average_recommendation_confidence": 0.0,
                "recommendation_uncertainty_mean": 0.0,
                "evidence_supported_recommendation_rate": 0.0,
                "rag_supported_recommendation_rate": 0.0,
                "missing_recommendation_calibration_count": 0,
            },
        )
        result = _generate_brief(state)
        assert result["brief_status"] == "blocked_no_production_recommendations"
        assert result["status"] == "brief_blocked"
        assert result["review_required"] is True
        assert len(result["action_brief"]["top_recommendations"]) == 0


# ── Test 3: ranking_status != passed blocks brief ──


class TestGenerateBriefRankingBlocked:
    def test_ranking_not_passed_blocks(self) -> None:
        for bad_status in ("blocked_no_nvidia_mappings", "blocked_uncalibrated_mapping",
                           "blocked_uncalibrated_recommendation", "failed", "needs_review"):
            state = _state_with_recs(ranking_status=bad_status)
            result = _generate_brief(state)
            assert result.get("brief_status") == "blocked_ranking_not_passed", f"Ranking {bad_status} should block"
            assert result["status"] == "brief_blocked"

    def test_ranking_none_blocks(self) -> None:
        state = _state_with_recs(ranking_status=None)
        result = _generate_brief(state)
        assert result.get("brief_status") == "blocked_ranking_not_passed"


# ── Test 4: unsupported critical claim generates failed ──


class TestGenerateBriefUnsupportedCritical:
    def test_unsupported_critical_claim_fails(self) -> None:
        state = _state_with_recs(
            unsupported_critical_claims_count=2,
            evidence_validation_metrics={"unsupported_critical_claims_count": 2},
        )
        result = _generate_brief(state)
        assert result.get("brief_status") == "failed_unsupported_critical_claim"
        assert result["status"] == "brief_failed"
        assert result["review_required"] is False
        blockers = result.get("blockers", [])
        assert any("critical claim" in b for b in blockers)


# ── Test 5: top_recommendations preserve scores, confidence, uncertainty ──


class TestGenerateBriefPreserveScores:
    def test_preserves_scores_confidence_uncertainty(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        recs = result["action_brief"]["top_recommendations"]
        assert len(recs) >= 1
        rec = recs[0]
        assert rec["recommendation_priority_score"] == 0.85
        assert rec["recommendation_confidence"] == 0.72
        assert rec["uncertainty"] == 0.15

    def test_preserves_mapping_scores(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        recs = result["action_brief"]["top_recommendations"]
        rec = recs[0]
        assert rec["mapping_score"] == 0.8
        assert rec["mapping_confidence"] == 0.75


# ── Test 6: top_recommendations preserve evidence/rag ids ──


class TestGenerateBriefPreserveIds:
    def test_preserves_supporting_evidence_ids(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        rec = result["action_brief"]["top_recommendations"][0]
        assert "ev_0" in rec["supporting_evidence_ids"]

    def test_preserves_supporting_rag_context_ids(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        rec = result["action_brief"]["top_recommendations"][0]
        assert "rag_0" in rec["supporting_rag_context_ids"]


# ── Test 7: brief_metrics are calculated ──


class TestGenerateBriefMetrics:
    def test_brief_metrics_contain_required_fields(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        bm = result["brief_metrics"]
        expected_fields = [
            "recommendation_count",
            "production_allowed_recommendation_count",
            "blocked_recommendation_count",
            "average_recommendation_priority_score",
            "average_recommendation_confidence",
            "recommendation_uncertainty_mean",
            "covered_gap_count",
            "total_gap_count",
            "accepted_evidence_count",
            "supporting_rag_context_count",
            "rag_supported_recommendation_rate",
            "evidence_supported_recommendation_rate",
            "unsupported_critical_claims_count",
            "blocker_count",
            "calibration_decision_count",
            "missing_calibration_count",
        ]
        for field in expected_fields:
            assert field in bm, f"Missing brief metric: {field}"

    def test_brief_metrics_values_are_correct(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        bm = result["brief_metrics"]
        assert bm["recommendation_count"] == 1
        assert bm["production_allowed_recommendation_count"] == 1
        assert bm["blocked_recommendation_count"] == 0
        assert bm["average_recommendation_priority_score"] == 0.85
        assert bm["average_recommendation_confidence"] == 0.72
        assert bm["unsupported_critical_claims_count"] == 0


# ── Test 8: audit_trail ──


class TestGenerateBriefAuditTrail:
    def test_audit_trail_contains_executed_nodes(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        audit = result["action_brief"]["audit_trail"]
        assert "generate_brief" in audit["executed_nodes"]
        assert "rank_recommendations" in audit["executed_nodes"]

    def test_audit_trail_contains_calibration_evidence_rag_ids(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        audit = result["action_brief"]["audit_trail"]
        assert "recommendation.priority_score_weights" in audit["calibration_decision_ids"]
        assert "ev_0" in audit["evidence_ids"]
        assert "rag_0" in audit["rag_context_ids"]

    def test_audit_trail_contains_blockers_and_quality_status(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        audit = result["action_brief"]["audit_trail"]
        assert audit["quality_gate_status"] == "passed"


# ── Test 9: executive_summary_quantitative is numeric ──


class TestGenerateBriefExecutiveSummary:
    def test_executive_summary_is_numeric(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        es = result["action_brief"]["executive_summary_quantitative"]
        assert isinstance(es, dict)
        assert isinstance(es.get("production_allowed_recommendations"), (int, float))
        assert isinstance(es.get("average_priority_score"), (int, float))
        assert isinstance(es.get("average_confidence"), (int, float))

    def test_executive_summary_no_persuasive_text(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        es = result["action_brief"]["executive_summary_quantitative"]
        for v in es.values():
            assert isinstance(v, (int, float, str)), f"Non-numeric value in exec summary: {v}"


# ── Test 10: no LLM / Qdrant / scraping / internet ──


class TestGenerateBriefNoExternal:
    def test_no_llm_qdrant_scraping_imported(self) -> None:
        import sys as _sys
        before = set(_sys.modules.keys())
        state = _state_with_recs()
        _generate_brief(state)
        after = set(_sys.modules.keys())
        new = after - before
        banned = {"langchain", "qdrant_client", "playwright", "openai", "anthropic", "httpx"}
        triggered = {m for m in new if any(b in m for b in banned)}
        assert not triggered, f"Banned imports triggered: {triggered}"


# ── Test 11: run_id preserved ──


class TestGenerateBriefRunId:
    def test_run_id_preserved(self) -> None:
        state = _state_with_recs(run_id="preserve-me-999")
        result = _generate_brief(state)
        assert result["action_brief"]["run_id"] == "preserve-me-999"


# ── Test 12: executed_nodes contains generate_brief ──


class TestGenerateBriefExecutedNodes:
    def test_executed_nodes_contains_generate_brief(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        assert "generate_brief" in result["executed_nodes"]
        idx = result["executed_nodes"].index("generate_brief")
        assert idx > result["executed_nodes"].index("rank_recommendations")


# ── Test 13: quality gate blocks brief ──


class TestGenerateBriefQualityGate:
    def test_quality_failed_blocks(self) -> None:
        state = _state_with_recs(quality={"status": "failed", "failed_checks": ["blockers_count > 0"], "warning_checks": []})
        result = _generate_brief(state)
        assert result.get("brief_status") == "blocked_quality_gate"

    def test_quality_blocked_uncalibrated_blocks(self) -> None:
        state = _state_with_recs(quality={"status": "blocked_uncalibrated_gap_diagnosis", "failed_checks": ["missing_calibration"], "warning_checks": []})
        result = _generate_brief(state)
        assert result.get("brief_status") == "blocked_quality_gate"


# ── Test 14: consistency check — rec without evidence/rag as production_allowed ──


class TestGenerateBriefConsistency:
    def test_rec_without_evidence_fails_inconsistency(self) -> None:
        state = _state_with_recs(
            nvidia_recommendations=[
                {
                    "recommendation_id": "rec-no-ev",
                    "gap_id": "gap-x",
                    "gap_type": "compute_acceleration_gap",
                    "nvidia_technology": "NVIDIA NIM",
                    "mapping_score": 0.8,
                    "mapping_confidence": 0.75,
                    "recommendation_priority_score": 0.8,
                    "confidence": 0.7,
                    "uncertainty": 0.2,
                    "supporting_evidence_ids": [],
                    "supporting_rag_context_ids": ["rag_1"],
                    "calibration_decision_ids": [],
                    "production_allowed": True,
                    "blockers": [],
                    "next_best_action": "Engage",
                    "reason": "Test",
                },
            ],
            nvidia_rec_metrics={
                "recommendation_count": 1,
                "production_allowed_recommendation_count": 1,
                "blocked_recommendation_count": 0,
                "average_recommendation_priority_score": 0.8,
                "average_recommendation_confidence": 0.7,
                "recommendation_uncertainty_mean": 0.2,
                "evidence_supported_recommendation_rate": 0.0,
                "rag_supported_recommendation_rate": 1.0,
                "missing_recommendation_calibration_count": 0,
            },
        )
        result = _generate_brief(state)
        assert result.get("brief_status") == "failed"
        assert result["action_brief"]["top_recommendations"] == []
        assert any("supporting_evidence_ids" in b for b in result.get("blockers", []))

    def test_quality_needs_review_sets_brief_needs_review(self) -> None:
        state = _state_with_recs(
            quality={
                "status": "needs_review",
                "failed_checks": [],
                "warning_checks": ["rag_retrieval_status is needs_review"],
            },
        )
        result = _generate_brief(state)
        assert result.get("brief_status") == "needs_review"
        assert result["status"] == "brief_needs_review"
        assert result["review_required"] is True

    def test_uncalibrated_inputs_block_brief(self) -> None:
        state = _state_with_recs(
            nvidia_rec_metrics={
                "recommendation_count": 1,
                "production_allowed_recommendation_count": 1,
                "blocked_recommendation_count": 0,
                "average_recommendation_priority_score": 0.85,
                "average_recommendation_confidence": 0.72,
                "recommendation_uncertainty_mean": 0.15,
                "evidence_supported_recommendation_rate": 1.0,
                "rag_supported_recommendation_rate": 1.0,
                "missing_recommendation_calibration_count": 1,
            },
        )
        result = _generate_brief(state)
        assert result.get("brief_status") == "blocked_uncalibrated_inputs"
        assert result["status"] == "brief_blocked"


# ── Test 15: top_recommendations have all required fields ──


class TestGenerateBriefRequiredFields:
    def test_top_recommendations_have_all_fields(self) -> None:
        state = _state_with_recs()
        result = _generate_brief(state)
        recs = result["action_brief"]["top_recommendations"]
        assert len(recs) >= 1
        rec = recs[0]
        required_fields = [
            "recommendation_id", "nvidia_technology", "gap_id", "gap_type",
            "recommendation_priority_score", "recommendation_confidence",
            "uncertainty", "mapping_score", "mapping_confidence",
            "business_impact", "implementation_complexity",
            "ai_native_score_value", "nvidia_fit_score_value",
            "gap_severity_score", "gap_confidence_score",
            "supporting_evidence_ids", "supporting_rag_context_ids",
            "supporting_claim_ids", "calibration_decision_ids",
            "next_best_action", "reason_grounded_in_scores",
            "production_allowed",
        ]
        for field in required_fields:
            assert field in rec, f"Missing required field in top_recommendation: {field}"


# ── Test 16: blocking rules — recommendation production_allowed=false in top_recommendations ──


class TestGenerateBriefBlockingRules:
    def test_blocked_recommendations_appear_in_blockers_section(self) -> None:
        state = _state_with_recs(
            nvidia_recommendations=[
                {
                    "recommendation_id": "rec-prod",
                    "gap_id": "gap-p",
                    "gap_type": "inference_performance_gap",
                    "nvidia_technology": "TensorRT",
                    "mapping_score": 0.9,
                    "mapping_confidence": 0.85,
                    "recommendation_priority_score": 0.9,
                    "confidence": 0.8,
                    "uncertainty": 0.1,
                    "supporting_evidence_ids": ["ev_0"],
                    "supporting_rag_context_ids": ["rag_0"],
                    "calibration_decision_ids": [],
                    "production_allowed": True,
                    "blockers": [],
                    "next_best_action": "Engage",
                    "reason": "Good",
                },
                {
                    "recommendation_id": "rec-blocked-2",
                    "gap_id": "gap-b2",
                    "gap_type": "data_pipeline_gap",
                    "nvidia_technology": "cuDF",
                    "mapping_score": 0.3,
                    "mapping_confidence": 0.2,
                    "recommendation_priority_score": 0.2,
                    "confidence": 0.15,
                    "uncertainty": 0.7,
                    "supporting_evidence_ids": [],
                    "supporting_rag_context_ids": [],
                    "calibration_decision_ids": [],
                    "production_allowed": False,
                    "blockers": ["Calibration decisions missing for recommendation"],
                    "next_best_action": "",
                    "reason": "Bad",
                },
            ],
            nvidia_rec_metrics={
                "recommendation_count": 2,
                "production_allowed_recommendation_count": 1,
                "blocked_recommendation_count": 1,
                "average_recommendation_priority_score": 0.55,
                "average_recommendation_confidence": 0.475,
                "recommendation_uncertainty_mean": 0.4,
                "evidence_supported_recommendation_rate": 0.5,
                "rag_supported_recommendation_rate": 0.5,
                "missing_recommendation_calibration_count": 0,
            },
        )
        result = _generate_brief(state)
        ab = result["action_brief"]
        assert len(ab["top_recommendations"]) == 1
        top_ids = [r["recommendation_id"] for r in ab["top_recommendations"]]
        assert "rec-prod" in top_ids
        assert "rec-blocked-2" not in top_ids
        blocker_descriptions = [b["description"] for b in ab["blockers"]]
        assert any("rec-blocked-2" in d for d in blocker_descriptions), (
            "Blocked recommendation should appear in blockers section"
        )


# ── Test 17: passed status when all conditions met ──


class TestGenerateBriefPassed:
    def test_passed_when_all_conditions_met(self) -> None:
        state = _state_with_recs(
            production_allowed=True,
            ranking_status="passed",
            unsupported_critical_claims_count=0,
            quality={"status": "passed", "failed_checks": [], "warning_checks": []},
        )
        result = _generate_brief(state)
        assert result.get("brief_status") == "passed"
        assert result["status"] == "brief_generated"
        assert result["review_required"] is False
