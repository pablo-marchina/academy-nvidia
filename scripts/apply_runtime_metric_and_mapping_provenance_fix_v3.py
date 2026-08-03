from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:180]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_first(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected at least one match in {path}: {old[:180]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_gap_runtime_metrics() -> None:
    path = ROOT / "src/diagnosis/gap_diagnosis_scoring.py"
    old = '''    source_category_coverage = 0.0\n    if collection_metrics:\n        categories = collection_metrics.get("source_categories_covered", [])\n        observed_count = (\n            len(categories)\n            if isinstance(categories, list)\n            else int(collection_metrics.get("source_category_count", 0) or 0)\n        )\n        minimums = collection_metrics.get("minimums", {})\n        expected = collection_metrics.get("expected_categories")\n        if not isinstance(expected, int | float) or expected <= 0:\n            expected = (minimums.get("source_category_count", 2) if isinstance(minimums, dict) else 2)\n        if expected and expected > 0:\n            source_category_coverage = min(1.0, observed_count / float(expected))\n'''
    new = '''    source_category_coverage = 0.0\n    if collection_metrics:\n        categories = collection_metrics.get("source_categories_covered")\n        if isinstance(categories, list) and categories:\n            observed_count = len(categories)\n        else:\n            observed_count = int(collection_metrics.get("source_category_count", 0) or 0)\n        minimums = collection_metrics.get("minimums", {})\n        expected = collection_metrics.get("expected_categories")\n        if not isinstance(expected, int | float) or expected <= 0:\n            expected = (minimums.get("source_category_count", 2) if isinstance(minimums, dict) else 2)\n        if expected and expected > 0:\n            source_category_coverage = min(1.0, observed_count / float(expected))\n'''
    replace_once(path, old, new)


def patch_mapping_provenance() -> None:
    path = ROOT / "src/recommendation/nvidia_technology_mapping.py"
    old = '''            score_feat, conf_feat = extract_mapping_features(\n                gap_type=gap_type_str,\n                technology=tech,\n                rag_contexts=rag_ctxs,\n                evidence_items=evidence_items,\n                gap_result=gap_result,\n            )\n\n            if is_blocked:\n'''
    new = '''            score_feat, conf_feat = extract_mapping_features(\n                gap_type=gap_type_str,\n                technology=tech,\n                rag_contexts=rag_ctxs,\n                evidence_items=evidence_items,\n                gap_result=gap_result,\n            )\n\n            # Provenance is factual metadata and must survive score/calibration\n            # blockers. A blocked decision is not the same as absent evidence.\n            rag_ctx_ids: list[str] = []\n            for ctx in rag_ctxs:\n                cid = ctx.get("context_id") or ctx.get("chunk_id") or ""\n                if cid and _context_matches_technology(ctx, tech):\n                    rag_ctx_ids.append(str(cid))\n\n            ev_ids: list[str] = []\n            gap_support_ids = set(gap_result.supporting_evidence_ids if gap_result else [])\n            for item in evidence_items:\n                eid = _evidence_id(item)\n                if eid and eid in gap_support_ids:\n                    ev_ids.append(eid)\n\n            if is_blocked:\n'''
    replace_once(path, old, new)

    old = '''                        supporting_rag_context_ids=[],\n                        supporting_evidence_ids=[],\n                        calibration_decision_ids=REQUIRED_MAPPING_DECISIONS,\n'''
    new = '''                        supporting_rag_context_ids=rag_ctx_ids,\n                        supporting_evidence_ids=ev_ids,\n                        calibration_decision_ids=REQUIRED_MAPPING_DECISIONS,\n'''
    replace_first(path, old, new)

    old = '''            # ── Supporting IDs ──────────────────────────────────────────\n            rag_ctx_ids: list[str] = []\n            for ctx in rag_ctxs:\n                cid = ctx.get("context_id") or ctx.get("chunk_id") or ""\n                if cid and _context_matches_technology(ctx, tech):\n                    rag_ctx_ids.append(str(cid))\n\n            ev_ids: list[str] = []\n            gap_support_ids = set(gap_result.supporting_evidence_ids if gap_result else [])\n            for item in evidence_items:\n                eid = _evidence_id(item)\n                if eid and eid in gap_support_ids:\n                    ev_ids.append(eid)\n\n            # ── Determine status ────────────────────────────────────────\n'''
    replace_once(path, old, "            # ── Determine status ────────────────────────────────────────\n")


def main() -> None:
    patch_gap_runtime_metrics()
    patch_mapping_provenance()


if __name__ == "__main__":
    main()
