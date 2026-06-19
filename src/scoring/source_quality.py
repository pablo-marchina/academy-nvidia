"""Source quality scoring — feature extraction, weight application, calibration gating.

Produces a normalised ``source_quality_score`` in [0, 1] when the
``weight.source_quality_score.weights`` decision is calibrated, or
blocks with ``score_status="blocked_uncalibrated_weights"`` otherwise.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from src.extraction.schemas import SourceType
from src.quality.decision_calibration_registry import (
    DecisionCalibrationRecord,
    get_project_decision_inventory,
    validate_decision_for_production,
)

SOURCE_QUALITY_WEIGHTS_DECISION_ID = "weight.source_quality_score.weights"
SOURCE_QUALITY_THRESHOLD_DECISION_ID = "threshold.source_quality_score.production_min"


class ScoreStatus(str, Enum):
    BLOCKED_UNCALIBRATED_WEIGHTS = "blocked_uncalibrated_weights"
    CALIBRATED = "calibrated"


class ScoreCalibrationStatus(str, Enum):
    UNCALIBRATED = "uncalibrated"
    CALIBRATED = "calibrated"
    BASELINE_MEASURED = "baseline_measured"


SOURCE_AUTHORITY_PRIOR: dict[str, float] = {
    SourceType.OFFICIAL_SITE.value: 1.0,
    SourceType.NEWS.value: 0.8,
    SourceType.FOUNDER_PROFILE.value: 0.7,
    SourceType.BLOG.value: 0.6,
    SourceType.JOB_POST.value: 0.5,
    SourceType.DIRECTORY.value: 0.4,
}

SOURCE_INDEPENDENCE_MAP: dict[str, str] = {
    SourceType.OFFICIAL_SITE.value: "self_reported",
    SourceType.NEWS.value: "third_party",
    SourceType.FOUNDER_PROFILE.value: "self_reported",
    SourceType.BLOG.value: "self_reported",
    SourceType.JOB_POST.value: "third_party",
    SourceType.DIRECTORY.value: "third_party",
}


class SourceQualityFeatures(BaseModel):
    source_category: str
    source_authority_prior: float = Field(ge=0.0, le=1.0)
    robots_allowed: bool
    compliance_status: str
    fetch_success: bool
    extraction_success: bool
    duplicate_status: str
    content_bytes: int = Field(ge=0)
    latency_ms: float = Field(ge=0.0)
    source_freshness_days: float | None = None
    source_independence_type: str | None = None
    historical_success_rate: float | None = Field(None, ge=0.0, le=1.0)
    historical_evidence_yield: float | None = Field(None, ge=0.0)


class SourceQualityScoreResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    score_status: ScoreStatus
    features: SourceQualityFeatures
    weights: dict[str, float]
    calibration_decision_id: str
    calibration_status: ScoreCalibrationStatus
    production_allowed: bool
    explanation: str
    blockers: list[str]


_DEFAULT_BLOCKING_WEIGHTS: dict[str, float] = {}


def _lookup_source_quality_weights(
    inventory: list[DecisionCalibrationRecord] | None = None,
) -> tuple[dict[str, float] | None, str, bool, list[str]]:
    if inventory is None:
        inventory = get_project_decision_inventory()
    blockers: list[str] = []
    for rec in inventory:
        if rec.decision_id == SOURCE_QUALITY_WEIGHTS_DECISION_ID:
            validation = validate_decision_for_production(rec)
            if not validation.passed:
                blockers.extend(validation.reasons)
                return None, rec.calibration_status.value, False, blockers
            if not isinstance(rec.current_value, dict):
                blockers.append(
                    f"Decision '{SOURCE_QUALITY_WEIGHTS_DECISION_ID}' "
                    f"current_value is not a dict (got {type(rec.current_value).__name__})"
                )
                return None, rec.calibration_status.value, False, blockers
            return rec.current_value, rec.calibration_status.value, rec.production_allowed, blockers
    blockers.append(
        f"Decision '{SOURCE_QUALITY_WEIGHTS_DECISION_ID}' not found in registry"
    )
    return None, ScoreCalibrationStatus.UNCALIBRATED.value, False, blockers


def _lookup_threshold(
    decision_id: str,
    inventory: list[DecisionCalibrationRecord] | None = None,
) -> float | None:
    if inventory is None:
        inventory = get_project_decision_inventory()
    for rec in inventory:
        if rec.decision_id == decision_id:
            if isinstance(rec.current_value, (int, float)):
                return float(rec.current_value)
            return None
    return None


def extract_source_quality_features(
    evidence_item: dict[str, Any],
    now: datetime | None = None,
) -> SourceQualityFeatures:
    now = now or datetime.now(timezone.utc)
    source_type_str = str(evidence_item.get("source_type", SourceType.DIRECTORY.value))
    if source_type_str not in SOURCE_AUTHORITY_PRIOR:
        source_type_str = SourceType.DIRECTORY.value

    authority_prior = SOURCE_AUTHORITY_PRIOR.get(source_type_str, 0.4)
    independence = SOURCE_INDEPENDENCE_MAP.get(source_type_str)

    collected_at = evidence_item.get("collected_at")
    freshness_days: float | None = None
    if collected_at:
        try:
            if isinstance(collected_at, str):
                collected_dt = datetime.fromisoformat(collected_at)
            else:
                collected_dt = collected_at
            delta = now - collected_dt
            freshness_days = delta.total_seconds() / 86400.0
        except (ValueError, TypeError):
            freshness_days = None

    return SourceQualityFeatures(
        source_category=source_type_str,
        source_authority_prior=authority_prior,
        robots_allowed=bool(evidence_item.get("robots_allowed", False)),
        compliance_status=str(evidence_item.get("compliance_status", "unknown")),
        fetch_success=evidence_item.get("status") == "fetched"
        or evidence_item.get("http_status_code", 500) < 400,
        extraction_success=evidence_item.get("extraction_status") == "success",
        duplicate_status="duplicate" if evidence_item.get("duplicate") else "unique",
        content_bytes=int(evidence_item.get("content_bytes", 0)),
        latency_ms=float(evidence_item.get("latency_ms", 0.0)),
        source_freshness_days=freshness_days,
        source_independence_type=independence,
        historical_success_rate=None,
        historical_evidence_yield=None,
    )


def _compute_weighted_score(
    features: SourceQualityFeatures,
    weights: dict[str, float],
) -> float:
    weight_sum = sum(weights.values())
    if weight_sum == 0.0:
        return 0.0

    feature_values: dict[str, float] = {
        "source_authority_prior": features.source_authority_prior,
        "robots_allowed": 1.0 if features.robots_allowed else 0.0,
        "compliance_status": 1.0 if features.compliance_status == "compliant" else 0.0,
        "fetch_success": 1.0 if features.fetch_success else 0.0,
        "extraction_success": 1.0 if features.extraction_success else 0.0,
        "duplicate_status": 1.0 if features.duplicate_status == "unique" else 0.3,
        "content_bytes": min(1.0, features.content_bytes / 10000.0),
        "latency_ms": max(0.0, 1.0 - features.latency_ms / 10000.0),
    }

    if features.source_freshness_days is not None:
        feature_values["source_freshness_days"] = max(0.0, 1.0 - features.source_freshness_days / 365.0)

    if features.historical_success_rate is not None:
        feature_values["historical_success_rate"] = features.historical_success_rate

    if features.historical_evidence_yield is not None:
        feature_values["historical_evidence_yield"] = min(1.0, features.historical_evidence_yield / 10.0)

    raw = sum(
        weights.get(k, 0.0) * v
        for k, v in feature_values.items()
        if k in weights
    )
    raw /= weight_sum
    return max(0.0, min(1.0, raw))


def compute_source_quality_score(
    evidence_item: dict[str, Any],
    inventory: list[DecisionCalibrationRecord] | None = None,
    now: datetime | None = None,
) -> SourceQualityScoreResult:
    features = extract_source_quality_features(evidence_item, now=now)
    weights, cal_status, prod_allowed, blockers = _lookup_source_quality_weights(inventory=inventory)

    if weights is None:
        return SourceQualityScoreResult(
            score=0.0,
            score_status=ScoreStatus.BLOCKED_UNCALIBRATED_WEIGHTS,
            features=features,
            weights=_DEFAULT_BLOCKING_WEIGHTS,
            calibration_decision_id=SOURCE_QUALITY_WEIGHTS_DECISION_ID,
            calibration_status=ScoreCalibrationStatus(cal_status),
            production_allowed=False,
            explanation="Source quality score blocked: weights missing or uncalibrated.",
            blockers=blockers,
        )

    score = _compute_weighted_score(features, weights)

    return SourceQualityScoreResult(
        score=score,
        score_status=ScoreStatus.CALIBRATED,
        features=features,
        weights=dict(weights),
        calibration_decision_id=SOURCE_QUALITY_WEIGHTS_DECISION_ID,
        calibration_status=ScoreCalibrationStatus(cal_status),
        production_allowed=prod_allowed,
        explanation=f"Source quality score computed from {len(weights)} weighted features.",
        blockers=[],
    )
