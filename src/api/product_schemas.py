"""Pydantic contracts for the product API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from src.extraction.schemas import ConfidenceLevel, SourceType


class StartupEvidenceCreate(BaseModel):
    claim: str = Field(min_length=1)
    source_url: HttpUrl
    source_type: SourceType
    quote_or_evidence: str = Field(min_length=1)
    confidence: ConfidenceLevel
    collected_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StartupEvidenceRead(BaseModel):
    id: str
    claim: str
    source_url: str
    source_type: str
    quote_or_evidence: str
    confidence: str
    evidence_kind: str
    collected_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class StartupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    website: HttpUrl
    country: str = "Brazil"
    sector: str = Field(min_length=1, max_length=255)
    description: str = ""
    product_summary: str = ""
    status: str = "active"
    tags: list[str] = Field(default_factory=list)
    evidence: list[StartupEvidenceCreate] = Field(default_factory=list)


class StartupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    website: HttpUrl | None = None
    country: str | None = None
    sector: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    product_summary: str | None = None
    status: str | None = None
    tags: list[str] | None = None


class StartupListItem(BaseModel):
    id: str
    name: str
    website: str
    sector: str
    status: str
    latest_analysis_run_id: str | None = None
    latest_analysis_status: str | None = None
    review_decision: str | None = None
    created_at: datetime
    updated_at: datetime


class StartupRead(BaseModel):
    id: str
    name: str
    normalized_name: str
    website: str
    country: str
    sector: str
    description: str
    product_summary: str
    status: str
    tags: list[str] = Field(default_factory=list)
    evidence: list[StartupEvidenceRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class AnalysisRunCreate(BaseModel):
    use_rag: bool = False
    rag_backend: str = "qdrant"
    pipeline_version: str = "current"
    corpus_version: str | None = None


class ReadinessCheckRead(BaseModel):
    code: str
    severity: str
    status: str
    user_message: str
    internal_detail: str
    recommended_action: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime


class AnalysisRunRead(BaseModel):
    id: str
    startup_id: str
    status: str
    error_message: str | None = None
    degraded_reason: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    pipeline_version: str
    corpus_version: str | None = None
    input_snapshot: dict[str, Any] = Field(default_factory=dict)
    output_snapshot: dict[str, Any] = Field(default_factory=dict)
    scores: list[dict[str, Any]] = Field(default_factory=list)
    gaps: list[dict[str, Any]] = Field(default_factory=list)
    nvidia_mappings: list[dict[str, Any]] = Field(default_factory=list)
    readiness_checks: list[ReadinessCheckRead] = Field(default_factory=list)
    action_brief_id: str | None = None
    claim_summary: ClaimSummaryRead | None = None
    created_at: datetime
    updated_at: datetime


class ActionBriefRead(BaseModel):
    id: str
    analysis_run_id: str
    version: int
    schema_version: str
    brief_json: dict[str, Any]
    brief_markdown: str
    is_latest: bool
    created_at: datetime
    updated_at: datetime


_REVIEW_DECISIONS = r"^(approve|reject|needs_more_evidence|monitor|contact|not_recommended)$"


class ReviewDecisionCreate(BaseModel):
    decision: str = Field(..., pattern=_REVIEW_DECISIONS)
    reviewer: str = Field(min_length=1, max_length=255)
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReviewDecisionRead(BaseModel):
    id: str
    analysis_run_id: str
    decision: str
    reviewer: str
    notes: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ExportCreate(BaseModel):
    export_type: str = Field(..., pattern=r"^(json|markdown)$")


class ExportRead(BaseModel):
    id: str
    analysis_run_id: str
    action_brief_id: str | None = None
    export_type: str
    status: str
    storage_path: str
    content_hash: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class OpportunityListItem(BaseModel):
    startup_id: str
    startup_name: str
    latest_analysis_run_id: str | None = None
    recommended_motion: str | None = None
    inception_fit_score: float | None = None
    ai_native_score: float | None = None
    production_readiness_score: float | None = None
    composite_score: float | None = None
    confidence: str | None = None
    status: str
    top_gaps: list[str] = Field(default_factory=list)
    top_nvidia_mappings: list[str] = Field(default_factory=list)
    degraded_count: int = 0
    last_analyzed_at: datetime | None = None
    review_status: str | None = None
    unsupported_claim_count: int | None = None
    evidence_coverage: float | None = None


class OpportunityListResponse(BaseModel):
    items: list[OpportunityListItem]
    total: int
    offset: int
    limit: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class PaginationParams(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class ProductHealthRead(BaseModel):
    status: str
    app_mode: str
    product_persistence_enabled: bool
    database_available: bool
    schema_ready: bool
    database_url: str
    error: str | None = None


class DependencyItemRead(BaseModel):
    name: str
    configured: bool
    available: bool
    required: bool
    status: str
    detail: str | None = None


class DependencyHealthRead(BaseModel):
    status: str
    corpus_version: str | None = None
    dependencies: list[DependencyItemRead]


_CLAIM_TYPE_PATTERN = r"^(ai_native_claim|technical_stack_claim|market_claim|production_readiness_claim|defensibility_claim|gap_claim|nvidia_fit_claim|risk_claim|activation_claim|uncertainty_claim)$"
_SUPPORT_LEVEL_PATTERN = r"^(unsupported|weak|medium|strong)$"
_REVIEW_STATUS_PATTERN = r"^(unreviewed|approved|rejected|needs_more_evidence)$"


class ClaimRead(BaseModel):
    id: str
    startup_id: str
    analysis_run_id: str
    claim_text: str
    claim_type: str
    support_level: str
    confidence: str
    evidence_refs: list[dict[str, Any]] = Field(default_factory=list)
    used_in_score: bool = False
    used_in_gap: bool = False
    used_in_mapping: bool = False
    used_in_brief: bool = False
    review_status: str = "unreviewed"
    reviewer_notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ClaimListResponse(BaseModel):
    items: list[ClaimRead]
    total: int
    offset: int
    limit: int


class ClaimReviewUpdate(BaseModel):
    review_status: str = Field(..., pattern=_REVIEW_STATUS_PATTERN)
    reviewer_notes: str = ""


class EvidenceCoverageRead(BaseModel):
    total_claims: int
    supported_claims: int
    unsupported_claims: int
    weak_claims: int
    critical_claims: int
    critical_supported_claims: int
    evidence_coverage: float
    unsupported_claim_rate: float
    avg_claim_confidence: float


class ClaimSummaryRead(BaseModel):
    total_claims: int
    supported_claims: int
    unsupported_claims: int
    evidence_coverage: float
