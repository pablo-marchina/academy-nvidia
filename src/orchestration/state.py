from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class WorkflowStatus:
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    DEGRADED = "degraded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    DEGRADED = "degraded"
    FAILED = "failed"


class ProductWorkflowState(BaseModel):
    workflow_id: str
    startup_id: str | None = None
    discovery_candidate_id: str | None = None
    analysis_run_id: str | None = None
    status: str = ""
    blockers: list[str] = []
    current_node: str = ""
    completed_nodes: list[str] = []
    failed_nodes: list[str] = []
    degraded_nodes: list[str] = []
    node_outputs: dict[str, Any] = {}
    evidence_ids: list[str] = []
    claim_ids: list[str] = []
    score_ids: list[str] = []
    gap_ids: list[str] = []
    mapping_ids: list[str] = []
    activation_recommendation_ids: list[str] = []
    dossier_id: str | None = None
    quality_run_id: str | None = None
    readiness_check_ids: list[str] = []
    error_message: str | None = None
    metadata_json: dict[str, Any] = {}
