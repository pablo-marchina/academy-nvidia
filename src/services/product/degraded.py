"""Explicit degraded-state definitions for product operations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DegradedStateDefinition:
    code: str
    severity: str
    user_message: str
    recommended_action: str


DEGRADED_STATES: dict[str, DegradedStateDefinition] = {
    "QDRANT_UNAVAILABLE": DegradedStateDefinition(
        code="QDRANT_UNAVAILABLE",
        severity="warning",
        user_message="Vector search is unavailable for this analysis.",
        recommended_action="Verify QDRANT_URL, credentials, and the Qdrant service.",
    ),
    "RAG_UNAVAILABLE": DegradedStateDefinition(
        code="RAG_UNAVAILABLE",
        severity="warning",
        user_message="NVIDIA retrieval context was unavailable or incomplete.",
        recommended_action="Verify the corpus, embedding provider, and vector backend.",
    ),
    "CORPUS_STALE": DegradedStateDefinition(
        code="CORPUS_STALE",
        severity="warning",
        user_message="The NVIDIA corpus may be stale.",
        recommended_action="Run the corpus freshness audit and maintenance workflow.",
    ),
    "MISSING_EVIDENCE": DegradedStateDefinition(
        code="MISSING_EVIDENCE",
        severity="warning",
        user_message="The analysis has material missing evidence.",
        recommended_action="Collect and validate additional public startup evidence.",
    ),
    "SCORE_INCOMPLETE": DegradedStateDefinition(
        code="SCORE_INCOMPLETE",
        severity="error",
        user_message="One or more required product scores are incomplete.",
        recommended_action="Inspect the pipeline output and score inputs before review.",
    ),
    "EVAL_FAILED": DegradedStateDefinition(
        code="EVAL_FAILED",
        severity="warning",
        user_message="A configured quality evaluation did not pass.",
        recommended_action="Inspect the evaluation report before using the result.",
    ),
    "PRODUCT_DB_UNAVAILABLE": DegradedStateDefinition(
        code="PRODUCT_DB_UNAVAILABLE",
        severity="error",
        user_message="The transactional product database is unavailable.",
        recommended_action="Verify PRODUCT_DB_URL and database access.",
    ),
    "UNSUPPORTED_CRITICAL_CLAIM": DegradedStateDefinition(
        code="UNSUPPORTED_CRITICAL_CLAIM",
        severity="error",
        user_message="One or more critical claims lack evidence support.",
        recommended_action="Review unsupported critical claims and collect additional evidence.",
    ),
    "LOW_EVIDENCE_COVERAGE": DegradedStateDefinition(
        code="LOW_EVIDENCE_COVERAGE",
        severity="warning",
        user_message="The analysis has low evidence coverage.",
        recommended_action="Improve evidence collection to increase claim support ratio.",
    ),
    "WEAK_NVIDIA_FIT_EVIDENCE": DegradedStateDefinition(
        code="WEAK_NVIDIA_FIT_EVIDENCE",
        severity="warning",
        user_message="NVIDIA fit claims have weak or missing evidence.",
        recommended_action="Collect additional evidence linking the startup to NVIDIA technologies.",
    ),
    "BRIEF_HAS_UNSUPPORTED_CLAIM": DegradedStateDefinition(
        code="BRIEF_HAS_UNSUPPORTED_CLAIM",
        severity="warning",
        user_message="The Action Brief contains unsupported claims.",
        recommended_action="Review brief claims and add supporting evidence before finalizing.",
    ),
    "SCORE_HAS_LOW_EVIDENCE_SUPPORT": DegradedStateDefinition(
        code="SCORE_HAS_LOW_EVIDENCE_SUPPORT",
        severity="warning",
        user_message="A high score is based on low-confidence evidence.",
        recommended_action="Validate the evidence underlying the score before making decisions.",
    ),
}
