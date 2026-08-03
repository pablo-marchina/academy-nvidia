from __future__ import annotations

from pathlib import Path

path = Path(__file__).resolve().parents[1] / "src/recommendation/nvidia_technology_mapping.py"
text = path.read_text(encoding="utf-8")
old = '''        gap_result = gap_result_by_type.get(gap_type_str)\n        rag_ctxs = rag_contexts_by_gap.get(gap_type_str, [])\n\n        for tech in candidate_techs:\n'''
new = '''        gap_result = gap_result_by_type.get(gap_type_str)\n        rag_ctxs = rag_contexts_by_gap.get(gap_type_str, [])\n        if not rag_ctxs and gap_result is not None:\n            rag_ctxs = rag_contexts_by_gap.get(gap_result.gap_id, [])\n\n        for tech in candidate_techs:\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one mapping context lookup block, found {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
