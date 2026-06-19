"""Typed state definitions for the LangGraph workflow."""

from __future__ import annotations

from typing import Any, TypedDict


class StartupRadarState(TypedDict, total=False):
    run_id: str
    thread_id: str
    analysis_run_id: str | None
    startup_id: str | None
    startup_name: str | None
    website_url: str | None
    notes: str | None
    status: str
    blockers: list[str]
    executed_nodes: list[str]
    search_plan: dict[str, Any]
    search_plan_metrics: dict[str, Any]
    evidence_items: list[dict[str, Any]]
    raw_evidence: list[dict[str, Any]]
    startup_profile: dict[str, Any]
    validated_evidence: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    evidence_validation: dict[str, Any]
    unsupported_critical_claims_count: int
    scores: dict[str, float]
    classification_result: dict[str, Any]
    defensibility_result: dict[str, Any]
    inception_fit_result: dict[str, Any]
    production_readiness_result: dict[str, Any]
    gaps: list[str]
    gap_diagnosis: dict[str, Any]
    gap_diagnosis_summary: dict[str, Any] | None
    gap_diagnosis_status: str | None
    gap_diagnosis_metrics: dict[str, Any] | None
    rag_contexts: list[str]
    rag_queries_by_gap: dict[str, Any]
    rag_contexts_by_gap: dict[str, list[dict[str, Any]]]
    rag_retrieval_status: str
    selected_retriever_strategy: str
    ragas_eval_reference: dict[str, Any] | None
    rag_metrics: dict[str, Any]
    recommendations: list[dict[str, Any]]
    recommendation_metrics: dict[str, Any]
    startup_brief: str
    action_brief: dict[str, Any]
    brief_metrics: dict[str, Any]
    quality: dict[str, Any] | None
    review_required: bool
    review_payload: dict[str, Any]
    review_decision: str
    review_notes: str
    reviewed_by: str
    evidence_retry_count: int
    max_evidence_retries: int
    evidence_request_reason: str
    source_candidates: list[dict[str, Any]]
    raw_evidence_candidates: list[dict[str, Any]]
    collection_metrics: dict[str, Any]
    collection_status: str
    extraction_metrics: dict[str, Any]
    extraction_status: str
    evidence_validation_metrics: dict[str, Any]
    accepted_evidence_items: list[dict[str, Any]]
    rejected_evidence_items: list[dict[str, Any]]
    startup_scoring_summary: dict[str, Any]
    nvidia_technology_mappings: list[dict[str, Any]]
    nvidia_mapping_metrics: dict[str, Any]
    nvidia_mapping_calibration_metrics: dict[str, Any]
    nvidia_mapping_summary: dict[str, Any] | None
    nvidia_recommendations: list[dict[str, Any]]
    nvidia_recommendation_metrics: dict[str, Any]
    nvidia_recommendation_summary: dict[str, Any] | None
    ranking_status: str | None
    recommendation_production_allowed: bool
    brief_status: str | None
    brief_calibration_snapshot: dict[str, Any] | None
    brief_quality_gate_snapshot: dict[str, Any] | None
