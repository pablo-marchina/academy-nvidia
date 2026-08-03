#!/usr/bin/env python3
"""Fix gap evidence coverage units and corroborated-absence handling."""
from pathlib import Path

path = Path("src/diagnosis/gap_diagnosis_scoring.py")
text = path.read_text(encoding="utf-8")
old = '''    status: GapDiagnosisStatus
    prod_allowed = True
    gap_blockers: list[str] = []

    if len(evidence_items) == 0:
        status = GapDiagnosisStatus.NEEDS_MORE_EVIDENCE
        prod_allowed = False
        gap_blockers.append("No evidence items available for gap diagnosis")
    elif (
        min_evidence_coverage is not None
        and confidence_features.supporting_evidence_count < min_evidence_coverage * len(evidence_items)
    ):
        status = GapDiagnosisStatus.NEEDS_MORE_EVIDENCE
        prod_allowed = False
        gap_blockers.append(
            f"Supporting evidence count ({confidence_features.supporting_evidence_count}) "
            f"below minimum coverage ({min_evidence_coverage})"
        )
    elif production_threshold is not None and final_severity > production_threshold:
        status = GapDiagnosisStatus.FAILED
    else:
        status = GapDiagnosisStatus.PASSED
'''
new = '''    status: GapDiagnosisStatus
    prod_allowed = True
    gap_blockers: list[str] = []

    related_keywords = [item.value for item in GAP_TECH_MAP.get(gap_type, [])]
    supporting_evidence_count_raw = sum(
        1
        for item in evidence_items
        if _text_contains_any(
            str(item.get("text") or item.get("snippet") or item.get("claim") or ""),
            related_keywords,
        )
    ) if related_keywords else 0
    observed_evidence_coverage = (
        supporting_evidence_count_raw / len(evidence_items) if evidence_items else 0.0
    )
    distinct_sources = {
        str(item.get("source_id") or item.get("source_url") or item.get("url") or "").strip()
        for item in evidence_items
        if item.get("source_id") or item.get("source_url") or item.get("url")
    }
    corroborated_absence = (
        severity_features.relevant_signal_absence >= 0.5
        and len(evidence_items) >= 3
        and len(distinct_sources) >= 3
        and confidence_features.contradiction_count == 0.0
    )
    thresholds["observed_evidence_coverage"] = round(observed_evidence_coverage, 4)
    thresholds["corroborated_absence"] = 1.0 if corroborated_absence else 0.0

    if len(evidence_items) == 0:
        status = GapDiagnosisStatus.NEEDS_MORE_EVIDENCE
        prod_allowed = False
        gap_blockers.append("No evidence items available for gap diagnosis")
    elif (
        min_evidence_coverage is not None
        and observed_evidence_coverage < min_evidence_coverage
        and not corroborated_absence
    ):
        status = GapDiagnosisStatus.NEEDS_MORE_EVIDENCE
        prod_allowed = False
        gap_blockers.append(
            f"Observed gap-specific evidence coverage ({observed_evidence_coverage:.4f}) "
            f"below minimum ({min_evidence_coverage:.4f}) and absence is not "
            "corroborated by at least three distinct sources"
        )
    elif production_threshold is not None and final_severity > production_threshold:
        status = GapDiagnosisStatus.FAILED
    else:
        status = GapDiagnosisStatus.PASSED
'''
if old not in text:
    raise RuntimeError("gap evidence coverage block not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
Path(__file__).unlink()
print("gap evidence coverage now uses raw ratio and corroborated absence")
