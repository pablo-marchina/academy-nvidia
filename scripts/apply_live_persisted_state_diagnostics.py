from __future__ import annotations

from pathlib import Path

# This one-shot patch is intentionally triggered after its workflow exists.
ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts/validate_live_outputs.py"
text = path.read_text(encoding="utf-8")

old = '''    workflow = workflow_response.json()\n    elapsed = round(time.perf_counter() - started, 3)\n    state = workflow.get("state") or {}\n'''
new = '''    workflow = workflow_response.json()\n    workflow_id = workflow.get("id")\n    if workflow_id:\n        persisted_response = client.get(\n            f"{base_url}/workflows/product-runs/{workflow_id}",\n            timeout=60.0,\n        )\n        persisted_response.raise_for_status()\n        workflow = persisted_response.json()\n    elapsed = round(time.perf_counter() - started, 3)\n    state = workflow.get("state") or {}\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one workflow response block, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''    rag_output = node_outputs.get("rag_output") if isinstance(node_outputs, dict) else {}\n    gap_output = node_outputs.get("gap_output") if isinstance(node_outputs, dict) else {}\n    if not isinstance(rag_output, dict):\n        rag_output = {}\n    if not isinstance(gap_output, dict):\n        gap_output = {}\n'''
new = '''    rag_output = node_outputs.get("rag_output") if isinstance(node_outputs, dict) else {}\n    gap_output = node_outputs.get("gap_output") if isinstance(node_outputs, dict) else {}\n    mapping_output = node_outputs.get("mapping_output") if isinstance(node_outputs, dict) else {}\n    if not isinstance(rag_output, dict):\n        rag_output = {}\n    if not isinstance(gap_output, dict):\n        gap_output = {}\n    if not isinstance(mapping_output, dict):\n        mapping_output = {}\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one node output diagnostics block, found {text.count(old)}")
text = text.replace(old, new, 1)

old = '''            "gap_diagnostics": [\n                {\n                    "gap_id": gap.get("gap_id"),\n                    "gap_type": gap.get("gap_type"),\n                    "status": gap.get("status"),\n                    "severity_score": gap.get("severity_score"),\n                    "confidence_score": gap.get("confidence_score"),\n                    "production_allowed": gap.get("production_allowed"),\n                    "thresholds": gap.get("thresholds", {}),\n                    "blockers": gap.get("blockers", []),\n                }\n                for gap in gap_output.get("gaps", [])\n                if isinstance(gap, dict)\n            ],\n'''
new = '''            "gap_diagnostics": [\n                {\n                    "gap_id": gap.get("gap_id"),\n                    "gap_type": gap.get("gap_type"),\n                    "status": gap.get("status"),\n                    "severity_score": gap.get("severity_score"),\n                    "confidence_score": gap.get("confidence_score"),\n                    "production_allowed": gap.get("production_allowed"),\n                    "supporting_evidence_ids": gap.get("supporting_evidence_ids", []),\n                    "thresholds": gap.get("thresholds", {}),\n                    "blockers": gap.get("blockers", []),\n                }\n                for gap in gap_output.get("gaps", [])\n                if isinstance(gap, dict)\n            ],\n            "mapping_status": mapping_output.get("mapping_status"),\n            "mapping_metrics": mapping_output.get("nvidia_mapping_metrics", {}),\n            "mapping_diagnostics": [\n                {\n                    "mapping_id": mapping.get("mapping_id"),\n                    "gap_type": mapping.get("gap_type"),\n                    "nvidia_technology": mapping.get("nvidia_technology"),\n                    "mapping_score": mapping.get("mapping_score"),\n                    "mapping_confidence": mapping.get("mapping_confidence"),\n                    "production_allowed": mapping.get("production_allowed"),\n                    "supporting_rag_context_ids": mapping.get("supporting_rag_context_ids", []),\n                    "supporting_evidence_ids": mapping.get("supporting_evidence_ids", []),\n                    "blockers": mapping.get("blockers", []),\n                }\n                for mapping in mapping_output.get("nvidia_technology_mappings", [])\n                if isinstance(mapping, dict)\n            ],\n'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one gap diagnostics output block, found {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
