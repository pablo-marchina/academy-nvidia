"""Schemas for Product RAG module.

Epic 14 adds: RerankingConfig, PackedContext, DroppedContext, PackingResult,
SupportingNvidiaContext.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RagSource(BaseModel):
    source_id: str
    title: str
    url: str | None = None
    product: str
    gap_types: list[str] = Field(default_factory=list)
    version: str = "1.0"
    document_type: str = "nvidia_corpus"
    content_hash: str | None = None
    previous_content_hash: str | None = None
    collected_at: str | None = None
    last_checked_at: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    freshness_policy: str | None = None
    stale_after_days: int | None = None
    is_active: bool = True
    deprecated_at: str | None = None
    superseded_by: str | None = None
    deprecation_reason: str | None = None


class RagDocument(BaseModel):
    source_id: str
    title: str
    raw_text: str


class RagChunk(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    content: str
    product: str
    gap_types: list[str] = Field(default_factory=list)
    url: str | None = None
    version: str = "1.0"
    document_type: str = "nvidia_corpus"
    content_hash: str | None = None
    previous_content_hash: str | None = None
    collected_at: str | None = None
    last_checked_at: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    freshness_policy: str | None = None
    stale_after_days: int | None = None
    is_active: bool = True
    deprecated_at: str | None = None
    superseded_by: str | None = None
    deprecation_reason: str | None = None


class RetrievalQuery(BaseModel):
    technology: str | None = None
    gap_type: str | None = None
    keywords: list[str] = Field(default_factory=list)
    include_deprecated: bool = False
    include_expired: bool = False
    include_stale: bool = False


class RetrievedContext(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    content: str
    product: str
    gap_types: list[str] = Field(default_factory=list)
    url: str | None = None
    relevance_score: float = 0.0
    version: str = "1.0"
    valid_from: str | None = None
    valid_until: str | None = None
    freshness_policy: str | None = None
    stale_after_days: int | None = None
    is_active: bool = True
    deprecated_at: str | None = None
    superseded_by: str | None = None


class PlaybookRetrievalResult(BaseModel):
    query: RetrievalQuery
    contexts: list[RetrievedContext] = Field(default_factory=list)
    total_found: int = 0
    missing_context: bool = False
    reasoning: str = ""


# ------------------------------------------------------------------
# Epic 14 — Reranking + Context Packing schemas
# ------------------------------------------------------------------


class RerankingConfig(BaseModel):
    boost_gap_match: float = 0.3
    boost_technology_match: float = 0.2
    penalty_no_provenance: float = -0.5
    penalty_duplicate: float = -0.3
    penalty_irrelevant: float = -0.2
    boost_known_source: float = 0.1


class PackedContext(BaseModel):
    chunk_id: str
    source_id: str
    title: str
    content: str
    product: str
    gap_types: list[str] = Field(default_factory=list)
    url: str | None = None
    relevance_score: float = 0.0
    rerank_score: float = 0.0
    matched_gap: str | None = None
    matched_technology: str | None = None
    version: str = "1.0"
    valid_from: str | None = None
    valid_until: str | None = None
    freshness_policy: str | None = None
    stale_after_days: int | None = None
    is_active: bool = True
    deprecated_at: str | None = None
    superseded_by: str | None = None


class DroppedContext(BaseModel):
    chunk_id: str
    reason: str
    rerank_score: float = 0.0


class PackingConfig(BaseModel):
    max_total: int = 5
    max_per_technology: int = 2
    max_per_gap: int = 3


class PackingResult(BaseModel):
    packed: list[PackedContext] = Field(default_factory=list)
    dropped: list[DroppedContext] = Field(default_factory=list)
    total_raw: int = 0
    total_packed: int = 0
    total_dropped: int = 0
    provenance_coverage: float = 0.0
    gap_coverage: float = 0.0
    technology_coverage: float = 0.0
    context_budget_used: float = 0.0
    noise_reduction_score: float = 0.0


class SupportingNvidiaContext(BaseModel):
    gap_type: str
    technology: str
    contexts: list[PackedContext] = Field(default_factory=list)
    total_available: int = 0
    total_dropped: int = 0


class RagPipelineOutput(BaseModel):
    packing_result: PackingResult | None = None
    retrieval_mode: str = "lexical"
    missing_context: bool = True
    rag_quality_summary: str = ""
