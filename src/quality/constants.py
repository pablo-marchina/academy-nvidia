from __future__ import annotations

from typing import Any

QUALITY_RUN_STATUS_RUNNING = "running"
QUALITY_RUN_STATUS_COMPLETED = "completed"
QUALITY_RUN_STATUS_FAILED = "failed"
QUALITY_RUN_STATUS_DEGRADED = "degraded"

METRIC_SEVERITY_INFO = "info"
METRIC_SEVERITY_WARN = "warn"
METRIC_SEVERITY_ERROR = "error"

METRIC_EVIDENCE_COVERAGE = "evidence_coverage"
METRIC_UNSUPPORTED_CLAIM_RATE = "unsupported_claim_rate"
METRIC_UNSUPPORTED_CRITICAL_CLAIM_COUNT = "unsupported_critical_claim_count"
METRIC_WEAK_CLAIM_RATE = "weak_claim_rate"
METRIC_DOSSIER_SECTION_COMPLETENESS = "dossier_section_completeness"
METRIC_MISSING_REQUIRED_SECTIONS = "missing_required_sections"
METRIC_ACTIVATION_PLAYBOOK_PRESENT = "activation_playbook_present"
METRIC_ACTIVATION_PLAYBOOK_EVIDENCE_SUPPORT = "activation_playbook_evidence_support"
METRIC_RECOMMENDATION_ACTIONABILITY_SCORE = "recommendation_actionability_score"
METRIC_DEGRADED_STATE_COUNT = "degraded_state_count"
METRIC_EXPORT_READINESS_SCORE = "export_readiness_score"
METRIC_REVIEW_READINESS_SCORE = "review_readiness_score"

DEFAULT_EVALUATOR_VERSION = "1.0"

DOSSIER_REQUIRED_SECTIONS: set[str] = {
    "metadata",
    "startup",
    "executive_verdict",
    "evidence_summary",
    "claims",
    "scores",
    "gaps",
    "nvidia_mappings",
    "activation_recommendations",
    "risks",
    "uncertainties",
    "review",
    "next_action",
}

THRESHOLDS: dict[str, dict[str, Any]] = {
    METRIC_EVIDENCE_COVERAGE: {
        "threshold": 0.60,
        "severity": METRIC_SEVERITY_WARN,
        "operator": "gte",
    },
    METRIC_UNSUPPORTED_CLAIM_RATE: {
        "threshold": 0.20,
        "severity": METRIC_SEVERITY_ERROR,
        "operator": "lte",
    },
    METRIC_UNSUPPORTED_CRITICAL_CLAIM_COUNT: {
        "threshold": 0.0,
        "severity": METRIC_SEVERITY_ERROR,
        "operator": "eq",
    },
    METRIC_DOSSIER_SECTION_COMPLETENESS: {
        "threshold": 0.85,
        "severity": METRIC_SEVERITY_ERROR,
        "operator": "gte",
    },
    METRIC_ACTIVATION_PLAYBOOK_PRESENT: {
        "threshold": 1.0,
        "severity": METRIC_SEVERITY_WARN,
        "operator": "eq",
    },
    METRIC_RECOMMENDATION_ACTIONABILITY_SCORE: {
        "threshold": 0.70,
        "severity": METRIC_SEVERITY_WARN,
        "operator": "gte",
    },
    METRIC_EXPORT_READINESS_SCORE: {
        "threshold": 0.70,
        "severity": METRIC_SEVERITY_INFO,
        "operator": "gte",
    },
    METRIC_REVIEW_READINESS_SCORE: {
        "threshold": 0.60,
        "severity": METRIC_SEVERITY_INFO,
        "operator": "gte",
    },
}
