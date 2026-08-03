from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src/diagnosis/gap_diagnosis_scoring.py"
text = PATH.read_text(encoding="utf-8")

old = '    related_keywords = [item.value for item in GAP_TECH_MAP.get(gap_type, [])]\n'
if text.count(old) != 1:
    raise RuntimeError(f"Expected one raw related_keywords assignment, found {text.count(old)}")
text = text.replace(old, '    related_keywords = _technical_gap_keywords(GAP_TECH_MAP.get(gap_type, []))\n', 1)

old_sources = '''    distinct_sources = {\n        str(item.get("source_url") or item.get("url") or item.get("source_id") or "").strip()\n        for item in evidence_items\n        if item.get("source_id") or item.get("source_url") or item.get("url")\n    }\n'''
if text.count(old_sources) != 1:
    raise RuntimeError(f"Expected one obsolete distinct_sources block, found {text.count(old_sources)}")
text = text.replace(old_sources, "", 1)

old_message = '''            f"Observed gap-specific evidence coverage ({observed_evidence_coverage:.4f}) "\n            f"below minimum ({min_evidence_coverage:.4f}) and absence is not "\n            "corroborated by at least three distinct sources"\n'''
new_message = '''            f"Observed positive gap-specific evidence coverage ({observed_evidence_coverage:.4f}) "\n            f"below minimum ({min_evidence_coverage:.4f}); public silence is not "\n            "accepted as proof of an operational gap"\n'''
if text.count(old_message) != 1:
    raise RuntimeError(f"Expected one obsolete blocker message, found {text.count(old_message)}")
text = text.replace(old_message, new_message, 1)

PATH.write_text(text, encoding="utf-8")
