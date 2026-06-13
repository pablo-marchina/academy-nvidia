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
    dossier_summary: ActivationDossierSummaryRead | None = None
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
    top_activation_playbook: str | None = None
    activation_confidence: str | None = None
    activation_next_step: str | None = None
    technical_experiment_summary: str | None = None
    dossier_available: bool = False
    latest_dossier_id: str | None = None
    export_readiness_score: float | None = None
    review_readiness_score: float | None = None


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


_CLAIM_TYPE_PATTERN = (
    r"^(ai_native_claim|technical_stack_claim|market_claim|"
    r"production_readiness_claim|defensibility_claim|gap_claim|"
    r"nvidia_fit_claim|risk_claim|activation_claim|uncertainty_claim)$"
)
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


class ActivationPlaybookRead(BaseModel):
    playbook_id: str
    name: str
    description: str = ""
    target_gap_types: list[str] = Field(default_factory=list)
    target_claim_types: list[str] = Field(default_factory=list)
    nvidia_technologies: list[str] = Field(default_factory=list)
    technical_experiment: dict = Field(default_factory=dict)
    success_metrics: list[str] = Field(default_factory=list)
    recommended_motion: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    expected_value: str = ""
    implementation_complexity: str = ""
    version: str = ""


class ActivationPlaybookListResponse(BaseModel):
    playbooks: list[ActivationPlaybookRead]
    total: int


class ActivationRecommendationRead(BaseModel):
    id: str
    analysis_run_id: str
    playbook_id: str
    playbook_name: str
    matched_gap_types: list[str] = Field(default_factory=list)
    matched_claim_ids: list[str] = Field(default_factory=list)
    nvidia_technologies: list[str] = Field(default_factory=list)
    technical_experiment: str = ""
    success_metrics: list[str] = Field(default_factory=list)
    recommended_motion: str = ""
    priority: int = 4
    confidence: str = "low"
    reasoning: str = ""
    evidence_refs: list[dict] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    next_step: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ActivationRecommendationListResponse(BaseModel):
    items: list[ActivationRecommendationRead]
    total: int
    offset: int
    limit: int


class GenerateActivationRecommendationsResponse(BaseModel):
    recommendations: list[ActivationRecommendationRead]
    total: int


class ActivationDossierRead(BaseModel):
    id: str
    analysis_run_id: str
    version: int
    schema_version: str
    dossier_json: dict[str, Any]
    dossier_markdown: str
    is_latest: bool
    evidence_coverage: float
    unsupported_claim_count: int
    top_activation_playbook_id: str | None = None
    recommended_motion: str
    review_status: str | None = None
    created_at: datetime
    updated_at: datetime


class ActivationDossierGenerateResponse(BaseModel):
    dossier: ActivationDossierRead
    version: int
    is_new: bool


class ActivationDossierMarkdownRead(BaseModel):
    markdown: str
    dossier_id: str
    version: int


class ActivationDossierSummaryRead(BaseModel):
    dossier_id: str | None = None
    dossier_version: int | None = None
    dossier_available: bool = False
    evidence_coverage: float | None = None
    unsupported_claim_count: int | None = None
    top_activation_playbook_id: str | None = None
    recommended_motion: str | None = None
    review_status: str | None = None


class ProductQualityMetricRead(BaseModel):
    id: str
    quality_run_id: str
    metric_name: str
    metric_value: float
    threshold: float
    passed: bool
    severity: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ProductQualityRunRead(BaseModel):
    id: str
    analysis_run_id: str
    dossier_id: str | None = None
    action_brief_id: str | None = None
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    evaluator_version: str
    metrics: list[ProductQualityMetricRead] = Field(default_factory=list)
    metrics_json: dict[str, Any] = Field(default_factory=dict)
    summary_json: dict[str, Any] = Field(default_factory=dict)
    degraded_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductQualitySummaryRead(BaseModel):
    analysis_run_id: str
    quality_run_id: str | None = None
    status: str | None = None
    evaluator_version: str | None = None
    overall_status: str
    total_metrics: int
    passed_metrics: int
    failed_metrics: int
    export_readiness_score: float | None = None
    review_readiness_score: float | None = None
    degraded_reason: str | None = None
    metrics: dict[str, dict[str, Any]] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Product Capability & Configuration Registry Schemas
# ---------------------------------------------------------------------------


class ProductCapabilityRead(BaseModel):
    capability_id: str
    name: str
    description: str
    category: str
    required: bool
    status: str
    status_reason: str = ""
    required_env_vars: list[str] = Field(default_factory=list)
    optional_env_vars: list[str] = Field(default_factory=list)
    required_extras: list[str] = Field(default_factory=list)
    required_services: list[str] = Field(default_factory=list)
    setup_instructions: str = ""
    failure_mode: str = ""
    user_visible: bool = True
    documentation_ref: str = ""


class ProductConfigurationItemRead(BaseModel):
    key: str
    description: str
    required: bool
    secret: bool = False
    default: str = ""
    current_value: str | None = None
    is_set: bool = False


class ProductSetupChecklistItem(BaseModel):
    key: str
    description: str
    is_set: bool
    required: bool


class ProductSetupChecklistRead(BaseModel):
    items: list[ProductSetupChecklistItem]
    total: int
    completed: int
    pending: int


class ProductReadinessRead(BaseModel):
    ready: bool
    blocking_missing_config: list[dict[str, Any]] = Field(default_factory=list)
    optional_missing_config: list[dict[str, Any]] = Field(default_factory=list)
    unavailable_capabilities: list[dict[str, Any]] = Field(default_factory=list)
    degraded_capabilities: list[dict[str, Any]] = Field(default_factory=list)
    setup_checklist: list[ProductSetupChecklistItem] = Field(default_factory=list)
    user_messages: list[str] = Field(default_factory=list)


class OptionalFeatureStatusRead(BaseModel):
    capability_id: str
    name: str
    status: str
    reason: str = ""
    setup_instructions: str = ""


# ---------------------------------------------------------------------------
# Discovery Schemas
# ---------------------------------------------------------------------------


class DiscoverySourceRead(BaseModel):
    source_id: str
    name: str
    source_type: str
    base_url: str
    country_scope: str
    sector_scope: str
    allowed: bool
    requires_api_key: bool
    rate_limit_hint: str
    collection_method: str
    robots_or_terms_note: str
    enabled_by_default: bool
    notes: str
    usable: bool


class DiscoveryRunRead(BaseModel):
    id: str
    source_id: str | None = None
    status: str
    error_message: str | None = None
    results_count: int = 0
    candidates_created: int = 0
    duplicates_found: int = 0
    query_json: dict[str, Any] = Field(default_factory=dict)
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DiscoveryRunListResponse(BaseModel):
    items: list[DiscoveryRunRead]
    total: int
    offset: int
    limit: int


class DiscoveryCandidateRead(BaseModel):
    id: str
    discovery_run_id: str | None = None
    source_id: str
    discovered_name: str
    normalized_name: str
    website: str
    country: str
    sector: str
    description: str
    source_url: str
    raw_text_excerpt: str
    ai_native_signals_json: dict[str, Any] = Field(default_factory=dict)
    evidence_refs_json: list[dict[str, Any]] = Field(default_factory=list)
    confidence: str
    status: str
    promoted_startup_id: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class DiscoveryCandidateListResponse(BaseModel):
    items: list[DiscoveryCandidateRead]
    total: int
    offset: int
    limit: int


class ManualSeedEntry(BaseModel):
    name: str = Field(default="", max_length=255)
    website: str = ""
    sector: str = ""
    description: str = ""
    country: str = "Brazil"


class ManualSeedRequest(BaseModel):
    entries: list[ManualSeedEntry] = Field(min_length=1, max_length=200)


class ManualSeedResponse(BaseModel):
    discovery_run_id: str
    status: str
    total_entries: int
    candidates_created: int
    duplicates_found: int


class UrlListRequest(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=200)


class UrlListResponse(BaseModel):
    discovery_run_id: str
    status: str
    total_urls: int
    candidates_created: int
    duplicates_found: int
    errors: list[str] = Field(default_factory=list)


class PromoteCandidateResponse(BaseModel):
    candidate_id: str
    startup_id: str
    status: str


class DedupCandidateResponse(BaseModel):
    duplicate_of_candidate_id: str | None = None
    duplicate_of_startup_id: str | None = None
