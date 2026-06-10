"""Schemas for RAG Evaluation — retrieval metrics and quality gates."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.rag.schemas import RetrievalQuery, RetrievedContext


class RagEvalCase(BaseModel):
    """A golden query case for RAG evaluation."""

    case_id: str
    description: str
    query: RetrievalQuery
    expected_source_ids: list[str] = Field(default_factory=list)
    expected_products: list[str] = Field(default_factory=list)
    is_critical: bool = False
    top_k_for_test: int = 3


class RagRetrievalMetrics(BaseModel):
    """Metrics computed from a single retrieval result against golden expectations."""

    hit_at_k: bool = False
    expected_source_coverage: float = 0.0
    expected_product_coverage: float = 0.0
    irrelevant_context_count: int = 0
    missing_context_count: int = 0
    top_1_expected_match: bool = False
    context_precision: float = 0.0


class RagEvalResult(BaseModel):
    """Result of evaluating a single golden query."""

    case_id: str
    case_description: str
    passed: bool
    is_critical: bool = False
    metrics: RagRetrievalMetrics
    retrieved_contexts: list[RetrievedContext] = Field(default_factory=list)
    expected_source_ids: list[str] = Field(default_factory=list)
    expected_products: list[str] = Field(default_factory=list)
    failure_reasons: list[str] = Field(default_factory=list)


class RagQualityGateResult(BaseModel):
    """Result of a single quality gate."""

    gate_name: str
    passed: bool
    details: str
    failed_cases: list[str] = Field(default_factory=list)
