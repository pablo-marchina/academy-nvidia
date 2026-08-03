from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "src/diagnosis/gap_diagnosis_scoring.py"
text = path.read_text(encoding="utf-8")

old = '''    elif production_threshold is not None and final_severity > production_threshold:\n        status = GapDiagnosisStatus.FAILED\n    else:\n        status = GapDiagnosisStatus.PASSED\n'''
new = '''    elif production_threshold is not None and final_severity > production_threshold:\n        # Crossing the calibrated severity threshold means a gap was detected;\n        # it is not a failure of the diagnosis process. Keep it retrieval-eligible\n        # and explicitly mark it for review by downstream decision makers.\n        status = GapDiagnosisStatus.NEEDS_REVIEW\n    else:\n        status = GapDiagnosisStatus.PASSED\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one threshold status block, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''    if status == GapDiagnosisStatus.PASSED:\n        explanation_parts.append("All checks passed.")\n    elif status == GapDiagnosisStatus.FAILED:\n        explanation_parts.append(f"Severity exceeds production threshold ({production_threshold}).")\n    elif status == GapDiagnosisStatus.NEEDS_MORE_EVIDENCE:\n        explanation_parts.append("Insufficient evidence for reliable diagnosis.")\n'''
new = '''    if status == GapDiagnosisStatus.PASSED:\n        explanation_parts.append("No decision-threshold gap was detected from the available evidence.")\n    elif status == GapDiagnosisStatus.NEEDS_REVIEW:\n        explanation_parts.append(\n            f"Evidence-supported gap exceeds the calibrated severity threshold ({production_threshold}) and requires review."\n        )\n    elif status == GapDiagnosisStatus.FAILED:\n        explanation_parts.append("The diagnosis process failed a validity gate.")\n    elif status == GapDiagnosisStatus.NEEDS_MORE_EVIDENCE:\n        explanation_parts.append("Insufficient positive evidence for reliable diagnosis.")\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one explanation block, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''        recommended_investigation=(\n            "Collect additional evidence for this gap area."\n            if status == GapDiagnosisStatus.NEEDS_MORE_EVIDENCE\n            else "No further investigation required at this time."\n        ),\n'''
new = '''        recommended_investigation=(\n            "Collect additional positive evidence for this gap area."\n            if status == GapDiagnosisStatus.NEEDS_MORE_EVIDENCE\n            else (\n                "Review the supporting company evidence and retrieve NVIDIA technical context."\n                if status == GapDiagnosisStatus.NEEDS_REVIEW\n                else "No further investigation required at this time."\n            )\n        ),\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one investigation block, found {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
