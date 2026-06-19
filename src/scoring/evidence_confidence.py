"""Evidence confidence scoring — feature extraction, weight application, calibration gating.

Produces a normalised ``evidence_confidence_score`` in [0, 1] when the
``weight.evidence_confidence_score.weights`` decision is calibrated, or
blocks with ``score_status="blocked_uncalibrated_weights"`` otherwise.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.extraction.schemas import ConfidenceLevel
from src.quality.decision_calibration_registry import (
    DecisionCalibrationRecord,
    get_project_decision_inventory,
    validate_decision_for_production,
)
from src.quantitative.params import CONFIDENCE_FLOAT_MAP, CONFIDENCE_SCORE_FACTORS

EVIDENCE_CONFIDENCE_WEIGHTS_DECISION_ID = "weight.evidence_confidence_score.weights"
EVIDENCE_CONFIDENCE_THRESHOLD_DECISION_ID = "threshold.evidence_confidence_score.production_min"


class ScoreStatus(str, Enum):
    BLOCKED_UNCALIBRATED_WEIGHTS = "blocked_uncalibrated_weights"
    CALIBRATED = "calibrated"


class ScoreCalibrationStatus(str, Enum):
    UNCALIBRATED = "uncalibrated"
    CALIBRATED = "calibrated"
    BASELINE_MEASURED = "baseline_measured"


CONFIDENCE_TO_FLOAT: dict[str, float] = {
    ConfidenceLevel.HIGH.value: CONFIDENCE_FLOAT_MAP.get("high", 1.0),
    ConfidenceLevel.MEDIUM.value: CONFIDENCE_FLOAT_MAP.get("medium", 0.6),
    ConfidenceLevel.LOW.value: CONFIDENCE_FLOAT_MAP.get("low", 0.3),
}


class EvidenceConfidenceFeatures(BaseModel):
    source_quality_score: float = Field(ge=0.0, le=1.0)
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    snippet_length: int = Field(ge=0)
    text_specificity_score: float = Field(ge=0.0, le=1.0)
    claim_support_count: int = Field(ge=0)
    supporting_source_count: int = Field(ge=0)
    cross_source_agreement_count: int = Field(ge=0)
    contradiction_count: int = Field(ge=0)
    factuality_status: str
    evidence_recency_days: float | None = None
    duplicate_penalty: float = Field(ge=0.0, le=1.0)
    unsupported_critical_claim_flag: bool = False


class EvidenceConfidenceScoreResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    score_status: ScoreStatus
    features: EvidenceConfidenceFeatures
    weights: dict[str, float]
    calibration_decision_id: str
    calibration_status: ScoreCalibrationStatus
    production_allowed: bool
    explanation: str
    blockers: list[str]


_DEFAULT_BLOCKING_WEIGHTS: dict[str, float] = {}


def _lookup_evidence_confidence_weights(
    inventory: list[DecisionCalibrationRecord] | None = None,
) -> tuple[dict[str, float] | None, str, bool, list[str]]:
    if inventory is None:
        inventory = get_project_decision_inventory()
    blockers: list[str] = []
    for rec in inventory:
        if rec.decision_id == EVIDENCE_CONFIDENCE_WEIGHTS_DECISION_ID:
            validation = validate_decision_for_production(rec)
            if not validation.passed:
                blockers.extend(validation.reasons)
                return None, rec.calibration_status.value, False, blockers
            if not isinstance(rec.current_value, dict):
                blockers.append(
                    f"Decision '{EVIDENCE_CONFIDENCE_WEIGHTS_DECISION_ID}' "
                    f"current_value is not a dict (got {type(rec.current_value).__name__})"
                )
                return None, rec.calibration_status.value, False, blockers
            return rec.current_value, rec.calibration_status.value, rec.production_allowed, blockers
    blockers.append(
        f"Decision '{EVIDENCE_CONFIDENCE_WEIGHTS_DECISION_ID}' not found in registry"
    )
    return None, ScoreCalibrationStatus.UNCALIBRATED.value, False, blockers


def _compute_text_specificity(text: str) -> float:
    if not text or not text.strip():
        return 0.0
    stripped = text.strip()
    if len(stripped) < 20:
        return 0.2
    words = stripped.split()
    if len(words) < 5:
        return 0.3
    numeric_count = sum(1 for w in words if any(c.isdigit() for c in w))
    proper_noun_hints = sum(
        1 for w in words if w and w[0].isupper() and w.lower() not in ("the", "a", "an", "this", "that", "it", "its")
    )
    specificity = 0.3
    specificity += min(0.3, len(words) / 100.0 * 0.3)
    specificity += min(0.2, numeric_count / max(1, len(words)) * 2.0)
    specificity += min(0.2, proper_noun_hints / max(1, len(words)) * 2.0)
    return min(1.0, specificity)


def _confidence_to_float(confidence_str: str) -> float:
    return CONFIDENCE_TO_FLOAT.get(confidence_str, 0.3)


def extract_evidence_confidence_features(
    evidence_item: dict[str, Any],
    validated_evidence: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> EvidenceConfidenceFeatures:
    now = now or datetime.now(timezone.utc)

    source_qs = float(evidence_item.get("source_quality_score", 0.5))

    confidence_str = str(evidence_item.get("confidence", ConfidenceLevel.MEDIUM.value))
    extraction_confidence = _confidence_to_float(confidence_str)

    snippet = str(evidence_item.get("snippet", evidence_item.get("text", "")))
    snippet_length = len(snippet)
    specificity = _compute_text_specificity(snippet)

    factuality = evidence_item.get("evidence_kind", "unverified")
    is_critical = bool(evidence_item.get("is_critical", False))
    is_unsupported = factuality in ("unverified", "weak_inference")

    duplicate_penalty = 0.3 if evidence_item.get("duplicate") else 0.0
    unsupported_critical = is_critical and is_unsupported

    collected_at = evidence_item.get("collected_at")
    recency_days: float | None = None
    if collected_at:
        try:
            if isinstance(collected_at, str):
                collected_dt = datetime.fromisoformat(collected_at)
            else:
                collected_dt = collected_at
            delta = now - collected_dt
            recency_days = delta.total_seconds() / 86400.0
        except (ValueError, TypeError):
            recency_days = None

    return EvidenceConfidenceFeatures(
        source_quality_score=source_qs,
        extraction_confidence=extraction_confidence,
        snippet_length=snippet_length,
        text_specificity_score=specificity,
        claim_support_count=evidence_item.get("claim_support_count", 0),
        supporting_source_count=evidence_item.get("supporting_source_count", 0),
        cross_source_agreement_count=evidence_item.get("cross_source_agreement_count", 0),
        contradiction_count=evidence_item.get("contradiction_count", 0),
        factuality_status=factuality,
        evidence_recency_days=recency_days,
        duplicate_penalty=duplicate_penalty,
        unsupported_critical_claim_flag=unsupported_critical,
    )


def _compute_weighted_score(
    features: EvidenceConfidenceFeatures,
    weights: dict[str, float],
) -> float:
    weight_sum = sum(weights.values())
    if weight_sum == 0.0:
        return 0.0

    feature_values: dict[str, float] = {
        "source_quality_score": features.source_quality_score,
        "extraction_confidence": features.extraction_confidence,
        "snippet_length": min(1.0, features.snippet_length / 500.0),
        "text_specificity_score": features.text_specificity_score,
        "claim_support_count": min(1.0, features.claim_support_count / 5.0),
        "supporting_source_count": min(1.0, features.supporting_source_count / 3.0),
        "cross_source_agreement_count": min(1.0, features.cross_source_agreement_count / 3.0),
        "contradiction_count": max(0.0, 1.0 - features.contradiction_count / 3.0),
        "factuality_status": {
            "fact": 1.0,
            "strong_inference": 0.8,
            "weak_inference": 0.4,
            "hypothesis": 0.5,
            "unverified": 0.1,
        }.get(features.factuality_status, 0.3),
        "duplicate_penalty": 1.0 - features.duplicate_penalty,
        "unsupported_critical_claim_flag": 0.0 if features.unsupported_critical_claim_flag else 1.0,
    }

    if features.evidence_recency_days is not None:
        feature_values["evidence_recency_days"] = max(0.0, 1.0 - features.evidence_recency_days / 365.0)

    raw = sum(
        weights.get(k, 0.0) * v
        for k, v in feature_values.items()
        if k in weights
    )
    raw /= weight_sum
    return max(0.0, min(1.0, raw))


def compute_evidence_confidence_score(
    evidence_item: dict[str, Any],
    validated_evidence: dict[str, Any] | None = None,
    inventory: list[DecisionCalibrationRecord] | None = None,
    now: datetime | None = None,
) -> EvidenceConfidenceScoreResult:
    features = extract_evidence_confidence_features(
        evidence_item, validated_evidence=validated_evidence, now=now
    )
    weights, cal_status, prod_allowed, blockers = _lookup_evidence_confidence_weights(inventory=inventory)

    if weights is None:
        return EvidenceConfidenceScoreResult(
            score=0.0,
            score_status=ScoreStatus.BLOCKED_UNCALIBRATED_WEIGHTS,
            features=features,
            weights=_DEFAULT_BLOCKING_WEIGHTS,
            calibration_decision_id=EVIDENCE_CONFIDENCE_WEIGHTS_DECISION_ID,
            calibration_status=ScoreCalibrationStatus(cal_status),
            production_allowed=False,
            explanation="Evidence confidence score blocked: weights missing or uncalibrated.",
            blockers=blockers,
        )

    score = _compute_weighted_score(features, weights)

    return EvidenceConfidenceScoreResult(
        score=score,
        score_status=ScoreStatus.CALIBRATED,
        features=features,
        weights=dict(weights),
        calibration_decision_id=EVIDENCE_CONFIDENCE_WEIGHTS_DECISION_ID,
        calibration_status=ScoreCalibrationStatus(cal_status),
        production_allowed=prod_allowed,
        explanation=f"Evidence confidence score computed from {len(weights)} weighted features.",
        blockers=[],
    )
