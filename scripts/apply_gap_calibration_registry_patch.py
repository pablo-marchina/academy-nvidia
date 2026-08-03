#!/usr/bin/env python3
"""Register all measured gap-diagnosis decisions already documented in code."""
from pathlib import Path

path = Path("src/quality/decision_calibration_registry.py")
text = path.read_text(encoding="utf-8")
start = text.index("def _gap_diagnosis_decisions() -> list[DecisionCalibrationRecord]:")
end = text.index("\n\ndef _ingestion_corpus_decisions()", start)
replacement = '''def _gap_diagnosis_decisions() -> list[DecisionCalibrationRecord]:
    """Gap diagnosis baseline measured on the repository calibration set.

    The current baseline is synthetic and must not be represented as human
    validation. It is nevertheless a measured, reproducible baseline used by
    the 74-case gap-diagnosis regression suite. Live release validation then
    checks the resulting gaps against real-company evidence and fails closed.
    """
    calibrated_at = datetime(2026, 6, 18, tzinfo=UTC)
    severity_weights: dict[str, float] = {
        "missing_required_signal_count": 0.20,
        "weak_evidence_count": 0.15,
        "rejected_evidence_count": 0.15,
        "unsupported_claim_count": 0.15,
        "low_confidence_evidence_count": 0.10,
        "relevant_signal_absence": 0.10,
        "nvidia_fit_opportunity_signal_count": 0.05,
        "implementation_complexity_proxy": 0.05,
        "business_impact_proxy": 0.03,
        "uncertainty_penalty": 0.02,
    }
    confidence_weights: dict[str, float] = {
        "supporting_evidence_count": 0.20,
        "supporting_source_count": 0.15,
        "average_evidence_confidence": 0.15,
        "average_source_quality": 0.15,
        "cross_source_agreement_count": 0.10,
        "contradiction_count": 0.10,
        "extraction_success_rate": 0.08,
        "source_category_coverage": 0.07,
    }
    evidence = (
        "scripts/calibrate_gap_diagnosis.py --mode=synthetic; "
        "src/evaluation/gap_diagnosis_baseline.py; "
        "tests/evals/test_gap_diagnosis_baseline.py. Sixty seeded calibration "
        "entries produced severity Spearman=0.9877 and confidence Spearman=0.9949; "
        "the release evaluation executes 74 gap-diagnosis regression cases. "
        "This is a reproducible synthetic baseline, not human-label validation."
    )
    limitations = (
        "Baseline measured on synthetic reference labels. Keep live output review "
        "and abstention gates active; replace with human-labeled calibration when "
        "data/eval/golden_gap_diagnosis_baseline.json has at least 20 labels."
    )
    common = {
        "calibration_status": CalibrationStatus.BASELINE_MEASURED,
        "production_allowed": True,
        "owner": "team-diagnosis",
        "last_calibrated_at": calibrated_at,
        "evidence_source": evidence,
        "notes": limitations,
    }
    return [
        DecisionCalibrationRecord(
            decision_id="gap_diagnosis.severity_weights",
            decision_name="Gap Diagnosis: Severity Feature Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=severity_weights,
            metric_name="gap_diagnosis_severity_weights",
            value_origin="scripts/calibrate_gap_diagnosis.py :: synthetic grid search candidate 1",
            calibration_method=CalibrationMethod.GRID_SEARCH,
            **common,
        ),
        DecisionCalibrationRecord(
            decision_id="gap_diagnosis.confidence_weights",
            decision_name="Gap Diagnosis: Confidence Feature Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=confidence_weights,
            metric_name="gap_diagnosis_confidence_weights",
            value_origin="scripts/calibrate_gap_diagnosis.py :: synthetic grid search candidate 1",
            calibration_method=CalibrationMethod.GRID_SEARCH,
            **common,
        ),
        DecisionCalibrationRecord(
            decision_id="gap_diagnosis.production_threshold",
            decision_name="Gap Diagnosis: Production Severity Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.3197,
            metric_name="gap_diagnosis_production_threshold",
            value_origin="scripts/calibrate_gap_diagnosis.py :: P5 synthetic severity distribution",
            calibration_method=CalibrationMethod.PERCENTILE_RULE,
            **common,
        ),
        DecisionCalibrationRecord(
            decision_id="gap_diagnosis.uncertainty_penalty",
            decision_name="Gap Diagnosis: Uncertainty Penalty",
            decision_type=DecisionType.WEIGHT,
            current_value=0.0,
            metric_name="gap_diagnosis_uncertainty_penalty",
            value_origin="scripts/calibrate_gap_diagnosis.py :: minimum max-error sensitivity result",
            calibration_method=CalibrationMethod.SENSITIVITY_ANALYSIS,
            **common,
        ),
        DecisionCalibrationRecord(
            decision_id="gap_diagnosis.minimum_evidence_coverage",
            decision_name="Gap Diagnosis: Minimum Evidence Coverage Ratio",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.20,
            metric_name="gap_diagnosis_min_evidence_coverage",
            value_origin="scripts/calibrate_gap_diagnosis.py :: P25 synthetic evidence ratio",
            calibration_method=CalibrationMethod.PERCENTILE_RULE,
            **common,
        ),
    ]
'''
path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")
Path(__file__).unlink()
print("registered complete measured gap-diagnosis decision group")
