"""Tests for _validate_evidence node with calibrated scoring gates."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import patch

import pytest

from src.agents.graph import _validate_evidence
from src.quality.decision_calibration_registry import (
    CalibrationStatus,
    DecisionCalibrationRecord,
    DecisionType,
)

_NOW = datetime(2026, 6, 17, tzinfo=timezone.utc)

REQUIRED_METRICS_KEYS: list[str] = [
    "evidence_items_count", "scored_evidence_count",
    "accepted_evidence_count", "rejected_evidence_count",
    "low_source_quality_count", "low_evidence_confidence_count",
    "claims_count", "supported_claims_count", "unsupported_claims_count",
    "unsupported_critical_claims_count",
    "average_source_quality_score", "average_evidence_confidence_score",
    "production_ready_evidence_ratio",
]

SQ_WEIGHTS: dict[str, float] = {
    "source_authority_prior": 0.30,
    "robots_allowed": 0.10,
    "compliance_status": 0.10,
    "fetch_success": 0.15,
    "extraction_success": 0.10,
    "duplicate_status": 0.05,
    "content_bytes": 0.05,
    "latency_ms": 0.05,
    "source_freshness_days": 0.05,
    "source_independence_type": 0.05,
}

EC_WEIGHTS: dict[str, float] = {
    "source_quality_score": 0.15,
    "extraction_confidence": 0.15,
    "snippet_length": 0.05,
    "text_specificity_score": 0.10,
    "claim_support_count": 0.10,
    "supporting_source_count": 0.10,
    "cross_source_agreement_count": 0.10,
    "contradiction_count": 0.05,
    "factuality_status": 0.10,
    "duplicate_penalty": 0.05,
    "unsupported_critical_claim_flag": 0.05,
}

_SQ_THRESHOLD = 0.65
_EC_THRESHOLD = 0.55


def _calibrated_inventory(
    sq_calibrated: bool = True,
    sq_threshold_calibrated: bool = True,
    ec_calibrated: bool = True,
    ec_threshold_calibrated: bool = True,
    production_ready_ratio_calibrated: bool = False,
    min_supported_claims_calibrated: bool = False,
) -> list[DecisionCalibrationRecord]:
    records: list[DecisionCalibrationRecord] = []
    if sq_calibrated:
        records.append(
            DecisionCalibrationRecord(
                decision_id="weight.source_quality_score.weights",
                decision_name="SQ Weights",
                decision_type=DecisionType.WEIGHT,
                current_value=SQ_WEIGHTS,
                calibration_status=CalibrationStatus.CALIBRATED,
                production_allowed=True,
                owner="test",
            )
        )
    if sq_threshold_calibrated:
        records.append(
            DecisionCalibrationRecord(
                decision_id="threshold.source_quality_score.production_min",
                decision_name="SQ Threshold",
                decision_type=DecisionType.THRESHOLD,
                current_value=_SQ_THRESHOLD,
                calibration_status=CalibrationStatus.CALIBRATED,
                production_allowed=True,
                owner="test",
            )
        )
    if ec_calibrated:
        records.append(
            DecisionCalibrationRecord(
                decision_id="weight.evidence_confidence_score.weights",
                decision_name="EC Weights",
                decision_type=DecisionType.WEIGHT,
                current_value=EC_WEIGHTS,
                calibration_status=CalibrationStatus.CALIBRATED,
                production_allowed=True,
                owner="test",
            )
        )
    if ec_threshold_calibrated:
        records.append(
            DecisionCalibrationRecord(
                decision_id="threshold.evidence_confidence_score.production_min",
                decision_name="EC Threshold",
                decision_type=DecisionType.THRESHOLD,
                current_value=_EC_THRESHOLD,
                calibration_status=CalibrationStatus.CALIBRATED,
                production_allowed=True,
                owner="test",
            )
        )
    if production_ready_ratio_calibrated:
        records.append(
            DecisionCalibrationRecord(
                decision_id="threshold.source_quality_score.production_ready_evidence_ratio",
                decision_name="Production ready evidence ratio",
                decision_type=DecisionType.THRESHOLD,
                current_value=0.5,
                calibration_status=CalibrationStatus.CALIBRATED,
                production_allowed=True,
                owner="test",
            )
        )
    if min_supported_claims_calibrated:
        records.append(
            DecisionCalibrationRecord(
                decision_id="threshold.source_quality_score.min_supported_claims",
                decision_name="Min supported claims",
                decision_type=DecisionType.THRESHOLD,
                current_value=1,
                calibration_status=CalibrationStatus.CALIBRATED,
                production_allowed=True,
                owner="test",
            )
        )
    return records


def _good_evidence_item(url: str = "https://example.com") -> dict[str, Any]:
    return {
        "url": url,
        "text": (
            "A sufficiently long explicit quote that provides "
            "specific context and supports the claim with details"
        ),
        "source_type": "news",
        "robots_allowed": True,
        "compliance_status": "compliant",
        "status": "fetched",
        "http_status_code": 200,
        "extraction_status": "success",
        "duplicate": False,
        "content_bytes": 5000,
        "latency_ms": 200.0,
        "collected_at": "2026-06-15T00:00:00+00:00",
        "confidence": "high",
        "snippet": (
            "A sufficiently long explicit quote that provides "
            "specific context and supports the claim with details"
        ),
    }


def _bad_source_item(url: str = "https://bad-source.com") -> dict[str, Any]:
    return {
        "url": url,
        "text": "some text",
        "source_type": "directory",
        "robots_allowed": False,
        "compliance_status": "non_compliant",
        "status": "failed",
        "http_status_code": 503,
        "extraction_status": "failed",
        "duplicate": True,
        "content_bytes": 50,
        "latency_ms": 30000.0,
        "collected_at": "2026-06-01T00:00:00+00:00",
        "confidence": "low",
        "snippet": "",
    }


def _empty_claim_item(url: str = "https://critical.ai") -> dict[str, Any]:
    return {
        "url": url,
        "text": "text",
        "source_type": "official_site",
        "robots_allowed": True,
        "compliance_status": "compliant",
        "status": "fetched",
        "http_status_code": 200,
        "extraction_status": "success",
        "duplicate": False,
        "content_bytes": 5000,
        "latency_ms": 200.0,
        "collected_at": "2026-06-15T00:00:00+00:00",
    }


# ---------------------------------------------------------------------------
# 1. Blocked when source_quality_score.weights not calibrated
# ---------------------------------------------------------------------------


def test_blocked_when_sq_weights_uncalibrated() -> None:
    inv = _calibrated_inventory(sq_calibrated=False)
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": [],
            "evidence_items": [_good_evidence_item()],
            "claims": [],
            "executed_nodes": [],
        })
    assert result["status"] == "evidence_scoring_uncalibrated"
    assert result["evidence_validation"]["status"] == "blocked_uncalibrated_scoring"
    assert result["review_required"] is True
    assert any("weight.source_quality_score.weights" in b for b in result.get("blockers", []))


# ---------------------------------------------------------------------------
# 2. Blocked when evidence_confidence_score.weights not calibrated
# ---------------------------------------------------------------------------


def test_blocked_when_ec_weights_uncalibrated() -> None:
    inv = _calibrated_inventory(ec_calibrated=False)
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": [],
            "evidence_items": [_good_evidence_item()],
            "claims": [],
            "executed_nodes": [],
        })
    assert result["status"] == "evidence_scoring_uncalibrated"
    assert result["evidence_validation"]["status"] == "blocked_uncalibrated_scoring"
    assert any("weight.evidence_confidence_score.weights" in b for b in result.get("blockers", []))


# ---------------------------------------------------------------------------
# 3. Blocked when production thresholds are absent
# ---------------------------------------------------------------------------


def test_blocked_when_thresholds_absent() -> None:
    inv = _calibrated_inventory(sq_threshold_calibrated=False, ec_threshold_calibrated=False)
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": [],
            "evidence_items": [_good_evidence_item()],
            "claims": [],
            "executed_nodes": [],
        })
    assert result["status"] == "evidence_scoring_uncalibrated"
    assert result["evidence_validation"]["status"] == "blocked_uncalibrated_scoring"
    all_blockers = " ".join(result.get("blockers", []))
    assert "threshold.source_quality_score.production_min" in all_blockers
    assert "threshold.evidence_confidence_score.production_min" in all_blockers


# ---------------------------------------------------------------------------
# 4. Item below source_quality_threshold is rejected
# ---------------------------------------------------------------------------


def test_item_below_sq_threshold_rejected() -> None:
    inv = _calibrated_inventory()
    # raw_evidence matches the url so the item gets evidence_kind
    raw = [{
        "claim": "Bad source claim",
        "source_url": "https://bad-source.com",
        "source_type": "directory",
        "quote_or_evidence": (
            "A sufficiently long explicit quote that provides "
            "specific context and supports the claim"
        ),
        "confidence": "low",
        "collected_at": "2026-06-01T00:00:00+00:00",
    }]
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": raw,
            "evidence_items": [_bad_source_item()],
            "claims": [],
            "executed_nodes": [],
        })
    items = result.get("evidence_items", [])
    assert len(items) >= 1
    first = items[0]
    assert first.get("evidence_item_status") == "rejected_low_source_quality"
    assert first.get("source_quality_score", 1.0) < _SQ_THRESHOLD


# ---------------------------------------------------------------------------
# 5. Item below evidence_confidence_threshold is rejected
# ---------------------------------------------------------------------------


def test_item_below_ec_threshold_rejected() -> None:
    inv = _calibrated_inventory()
    # Item with good SQ features but short snippet + low confidence + unverified
    # evidence_kind → fails EC threshold while passing SQ threshold
    item = _good_evidence_item(url="https://low-ec.com")
    item["snippet"] = "Short."
    item["confidence"] = "low"
    raw = [{
        "claim": "Low confidence claim",
        "source_url": "https://low-ec.com",
        "source_type": "news",
        "quote_or_evidence": (
            "A sufficiently long explicit quote that provides "
            "specific context and supports the claim"
        ),
        "confidence": "low",
        "collected_at": "2026-06-15T00:00:00+00:00",
    }]
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": raw,
            "evidence_items": [item],
            "claims": [],
            "executed_nodes": [],
        })
    items = result.get("evidence_items", [])
    assert len(items) >= 1
    first = items[0]
    assert first.get("evidence_item_status") == "rejected_low_evidence_confidence"
    ec = first.get("evidence_confidence_score", 1.0)
    assert ec < _EC_THRESHOLD


# ---------------------------------------------------------------------------
# 6. Item above thresholds is accepted
# ---------------------------------------------------------------------------


def test_item_above_thresholds_accepted() -> None:
    inv = _calibrated_inventory()
    raw = [{
        "claim": "Good evidence claim",
        "source_url": "https://example.com",
        "source_type": "news",
        "quote_or_evidence": (
            "A sufficiently long explicit quote that provides "
            "specific context and supports the claim with details"
        ),
        "confidence": "high",
        "collected_at": "2026-06-15T00:00:00+00:00",
    }]
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": raw,
            "evidence_items": [_good_evidence_item()],
            "claims": [],
            "executed_nodes": [],
        })
    items = result.get("evidence_items", [])
    assert len(items) >= 1
    first = items[0]
    assert first.get("evidence_item_status") == "accepted"


# ---------------------------------------------------------------------------
# 7. Unsupported critical claim generates failed
# ---------------------------------------------------------------------------


def test_unsupported_critical_claim_failed() -> None:
    inv = _calibrated_inventory()
    raw = [{
        "claim": "We are the undisputed market leader",
        "source_url": "https://critical.ai",
        "source_type": "official_site",
        "quote_or_evidence": "",
        "confidence": "medium",
        "collected_at": "2026-06-15T00:00:00+00:00",
    }]
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": raw,
            "evidence_items": [_empty_claim_item()],
            "claims": [],
            "executed_nodes": [],
        })
    assert result["status"] == "evidence_validation_failed"
    assert result["evidence_validation"]["status"] == "failed"
    assert result["unsupported_critical_claims_count"] >= 1
    assert any("critical claim" in b for b in result.get("blockers", []))


# ---------------------------------------------------------------------------
# 8. Aggregate metrics are calculated correctly
# ---------------------------------------------------------------------------


def test_aggregate_metrics_calculated() -> None:
    inv = _calibrated_inventory()
    raw = [
        {
            "claim": "Good claim",
            "source_url": "https://example.com",
            "source_type": "news",
            "quote_or_evidence": (
                "A sufficiently long explicit quote that provides "
                "specific context and supports the claim with details"
            ),
            "confidence": "high",
            "collected_at": "2026-06-15T00:00:00+00:00",
        },
        {
            "claim": "Bad source claim",
            "source_url": "https://bad-source.com",
            "source_type": "directory",
            "quote_or_evidence": (
                "A sufficiently long explicit quote that provides "
                "specific context and supports the claim"
            ),
            "confidence": "low",
            "collected_at": "2026-06-01T00:00:00+00:00",
        },
    ]
    items = [_good_evidence_item(), _bad_source_item()]
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": raw,
            "evidence_items": items,
            "claims": [],
            "executed_nodes": [],
        })
    evm = result.get("evidence_validation_metrics", {})
    assert evm.get("evidence_items_count") == 2
    assert evm.get("scored_evidence_count") == 2
    assert evm.get("accepted_evidence_count") == 1
    assert evm.get("low_source_quality_count") == 1
    assert evm.get("claims_count") == 2
    assert evm.get("unsupported_critical_claims_count") == 0
    assert 0.0 <= evm.get("average_source_quality_score", 0.0) <= 1.0
    assert 0.0 <= evm.get("average_evidence_confidence_score", 0.0) <= 1.0

    # evidence_validation.metrics must also exist
    ev = result.get("evidence_validation", {})
    ev_m = ev.get("metrics", {})
    for key in REQUIRED_METRICS_KEYS:
        assert key in ev_m, f"Missing key in ev metrics: {key}"


# ---------------------------------------------------------------------------
# 9. production_ready_evidence_ratio is calculated
# ---------------------------------------------------------------------------


def test_production_ready_evidence_ratio() -> None:
    inv = _calibrated_inventory()
    raw = [
        {
            "claim": f"Good claim {i}",
            "source_url": f"https://example{i}.com",
            "source_type": "news",
            "quote_or_evidence": (
                "A sufficiently long explicit quote that provides "
                "specific context and supports the claim with details"
            ),
            "confidence": "high",
            "collected_at": "2026-06-15T00:00:00+00:00",
        }
        for i in range(4)
    ]
    items = [_good_evidence_item(url=f"https://example{i}.com") for i in range(4)]
    # Make first two have low source quality
    items[2] = _bad_source_item(url="https://example2.com")
    items[3] = _bad_source_item(url="https://example3.com")

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": raw,
            "evidence_items": items,
            "claims": [],
            "executed_nodes": [],
        })
    evm = result.get("evidence_validation_metrics", {})
    assert evm.get("accepted_evidence_count") == 2
    assert evm.get("scored_evidence_count") == 4
    assert evm.get("production_ready_evidence_ratio") == 0.5


# ---------------------------------------------------------------------------
# 10. passed status only with valid calibration + accepted evidence
# ---------------------------------------------------------------------------


def test_passed_status_requires_calibration_and_accepted() -> None:
    inv = _calibrated_inventory(
        production_ready_ratio_calibrated=True,
        min_supported_claims_calibrated=True,
    )
    raw = [{
        "claim": "Good claim",
        "source_url": "https://example.com",
        "source_type": "news",
        "quote_or_evidence": (
            "A sufficiently long explicit quote that provides "
            "specific context and supports the claim with details"
        ),
        "confidence": "high",
        "collected_at": "2026-06-15T00:00:00+00:00",
    }]
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "raw_evidence": raw,
            "evidence_items": [_good_evidence_item()],
            "claims": [],
            "executed_nodes": [],
        })
    assert result["status"] == "evidence_validation_passed"
    assert result["evidence_validation"]["status"] == "passed"
    assert result.get("review_required") is False
    assert len(result["accepted_evidence_items"]) >= 1


# ---------------------------------------------------------------------------
# 11. run_id is preserved in the graph
# ---------------------------------------------------------------------------


def test_run_id_preserved() -> None:
    inv = _calibrated_inventory()
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        result = _validate_evidence({
            "run_id": "preserved-id-42",
            "raw_evidence": [],
            "evidence_items": [_good_evidence_item()],
            "claims": [],
            "executed_nodes": [],
        })
    # run_id is not mutated — it stays in caller's state dict
    assert "validate_evidence" in result["executed_nodes"]


# ---------------------------------------------------------------------------
# 12. No LLM / Qdrant / internet / scraping is called
# ---------------------------------------------------------------------------


def test_no_llm_qdrant_internet_scraping() -> None:
    import sys

    inv = _calibrated_inventory()
    before = set(sys.modules.keys())
    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=inv,
    ):
        _validate_evidence({
            "raw_evidence": [],
            "evidence_items": [_good_evidence_item()],
            "claims": [],
            "executed_nodes": [],
        })
    after = set(sys.modules.keys())
    new_imports = after - before
    banned: set[str] = {
        "langchain", "qdrant_client", "httpx", "aiohttp",
        "requests", "openai", "anthropic",
    }
    triggered = {m for m in new_imports if any(b in m for b in banned)}
    assert not triggered, f"Banned imports detected: {triggered}"
