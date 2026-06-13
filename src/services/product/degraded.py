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
        recommended_action=(
            "Collect additional evidence linking the startup to NVIDIA technologies."
        ),
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
    "NO_ACTIVATION_PLAYBOOK_MATCH": DegradedStateDefinition(
        code="NO_ACTIVATION_PLAYBOOK_MATCH",
        severity="warning",
        user_message="No activation playbook matched the diagnosed gaps.",
        recommended_action=(
            "Review gap diagnosis and collect additional evidence " "to enable a playbook match."
        ),
    ),
    "PLAYBOOK_LOW_EVIDENCE_SUPPORT": DegradedStateDefinition(
        code="PLAYBOOK_LOW_EVIDENCE_SUPPORT",
        severity="warning",
        user_message="Activation playbook match has low evidence support.",
        recommended_action=(
            "Collect additional evidence to increase confidence " "in the recommended playbook."
        ),
    ),
    "PLAYBOOK_UNSUPPORTED_CLAIMS": DegradedStateDefinition(
        code="PLAYBOOK_UNSUPPORTED_CLAIMS",
        severity="error",
        user_message="Activation playbook matched but critical claims are unsupported.",
        recommended_action=(
            "Review unsupported critical claims and strengthen evidence "
            "before proceeding with the playbook."
        ),
    ),
    "DOSSIER_LOW_EVIDENCE_COVERAGE": DegradedStateDefinition(
        code="DOSSIER_LOW_EVIDENCE_COVERAGE",
        severity="warning",
        user_message="The dossier has low evidence coverage.",
        recommended_action="Improve evidence collection and regenerate the dossier.",
    ),
    "DOSSIER_UNSUPPORTED_CRITICAL_CLAIMS": DegradedStateDefinition(
        code="DOSSIER_UNSUPPORTED_CRITICAL_CLAIMS",
        severity="error",
        user_message="The dossier contains unsupported critical claims.",
        recommended_action="Review unsupported claims and collect additional evidence.",
    ),
    "DOSSIER_NO_ACTIVATION_PLAYBOOK": DegradedStateDefinition(
        code="DOSSIER_NO_ACTIVATION_PLAYBOOK",
        severity="warning",
        user_message="The dossier has no matching activation playbook.",
        recommended_action="Review gap diagnosis to enable a playbook match.",
    ),
    "DOSSIER_MISSING_REVIEW": DegradedStateDefinition(
        code="DOSSIER_MISSING_REVIEW",
        severity="info",
        user_message="The dossier has no human review recorded.",
        recommended_action="Record a review decision for this analysis run.",
    ),
    "DOSSIER_INCOMPLETE_SCORES": DegradedStateDefinition(
        code="DOSSIER_INCOMPLETE_SCORES",
        severity="warning",
        user_message="The dossier has one or more missing scores.",
        recommended_action="Inspect pipeline output and rerun analysis if needed.",
    ),
    "QUALITY_LOW_EVIDENCE_COVERAGE": DegradedStateDefinition(
        code="QUALITY_LOW_EVIDENCE_COVERAGE",
        severity="warning",
        user_message="Quality evaluation detected low evidence coverage.",
        recommended_action="Improve evidence collection to increase the support ratio.",
    ),
    "QUALITY_HIGH_UNSUPPORTED_CLAIM_RATE": DegradedStateDefinition(
        code="QUALITY_HIGH_UNSUPPORTED_CLAIM_RATE",
        severity="warning",
        user_message="Quality evaluation shows a high rate of unsupported claims.",
        recommended_action="Review and collect additional evidence for unsupported claims.",
    ),
    "QUALITY_UNSUPPORTED_CRITICAL": DegradedStateDefinition(
        code="QUALITY_UNSUPPORTED_CRITICAL",
        severity="error",
        user_message="Quality evaluation found unsupported critical claims.",
        recommended_action="Collect evidence for all critical claims before proceeding.",
    ),
    "QUALITY_INCOMPLETE_DOSSIER": DegradedStateDefinition(
        code="QUALITY_INCOMPLETE_DOSSIER",
        severity="warning",
        user_message="Quality evaluation found the dossier has missing required sections.",
        recommended_action="Regenerate the dossier after filling missing sections.",
    ),
    "QUALITY_NO_PLAYBOOK": DegradedStateDefinition(
        code="QUALITY_NO_PLAYBOOK",
        severity="warning",
        user_message="Quality evaluation found no activation playbook match.",
        recommended_action="Review gap diagnosis and regenerate playbook recommendations.",
    ),
    "QUALITY_LOW_ACTIONABILITY": DegradedStateDefinition(
        code="QUALITY_LOW_ACTIONABILITY",
        severity="warning",
        user_message="Quality evaluation found recommendations with low actionability.",
        recommended_action=(
            "Review recommendations and ensure motion, next step, "
            "experiment, and metrics are defined."
        ),
    ),
    "QUALITY_LOW_EXPORT_READINESS": DegradedStateDefinition(
        code="QUALITY_LOW_EXPORT_READINESS",
        severity="warning",
        user_message="Quality evaluation shows low export readiness score.",
        recommended_action=(
            "Improve dossier quality, evidence coverage, " "and reduce unsupported claims."
        ),
    ),
    "QUALITY_LOW_REVIEW_READINESS": DegradedStateDefinition(
        code="QUALITY_LOW_REVIEW_READINESS",
        severity="warning",
        user_message="Quality evaluation shows low review readiness score.",
        recommended_action="Complete a human review and improve evidence coverage.",
    ),
    "PLAYBOOK_MISSING_SUCCESS_METRICS": DegradedStateDefinition(
        code="PLAYBOOK_MISSING_SUCCESS_METRICS",
        severity="warning",
        user_message="Activation playbook is missing defined success metrics.",
        recommended_action=(
            "Ensure success metrics are defined " "before starting the playbook experiment."
        ),
    ),
}
