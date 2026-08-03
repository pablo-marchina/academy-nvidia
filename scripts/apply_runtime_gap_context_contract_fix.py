from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE_IMPL = ROOT / "src/orchestration/node_impl.py"


def replace_once(old: str, new: str) -> None:
    text = NODE_IMPL.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match, found {count}: {old[:220]}")
    NODE_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_gap_id_normalization() -> None:
    old = '''    if gap_id in {item.value for item in GapType}:\n        return gap_id\n    try:\n        technical_gap = TechnicalGap(gap_id)\n'''
    new = '''    known_gap_types = {item.value for item in GapType}\n    if gap_id in known_gap_types:\n        return gap_id\n    # Quantitative diagnosis emits stable runtime IDs such as\n    # ``gap-3-mlops_deployment_gap``. Preserve the semantic suffix instead of\n    # collapsing every runtime ID to the NVIDIA ecosystem fallback.\n    for gap_type in GapType:\n        if gap_id.endswith(gap_type.value):\n            return gap_type.value\n    try:\n        technical_gap = TechnicalGap(gap_id)\n'''
    replace_once(old, new)


def patch_context_flattening() -> None:
    old = '''        raw_by_gap = result.get("rag_contexts_by_gap", {})\n        if isinstance(raw_by_gap, dict):\n            for items in raw_by_gap.values():\n                if isinstance(items, list):\n                    contexts.extend([item for item in items if isinstance(item, dict)])\n'''
    new = '''        raw_by_gap = result.get("rag_contexts_by_gap", {})\n        if isinstance(raw_by_gap, dict):\n            for gap_key, items in raw_by_gap.items():\n                if not isinstance(items, list):\n                    continue\n                for item in items:\n                    if not isinstance(item, dict):\n                        continue\n                    context = dict(item)\n                    if not context.get("gap_types") and not context.get("gap_type"):\n                        context["gap_types"] = [str(gap_key)]\n                    contexts.append(context)\n'''
    replace_once(old, new)


def patch_context_grouping() -> None:
    old = '''def _rag_contexts_by_gap(contexts: list[Any], gap_ids: list[str]) -> dict[str, list[dict[str, Any]]]:\n    normalized = [_as_state_dict(ctx) for ctx in contexts]\n    target_gap_types = {_gap_type_for_runtime_gap(gap_id) for gap_id in gap_ids}\n    grouped: dict[str, list[dict[str, Any]]] = {gap_type: [] for gap_type in target_gap_types}\n    for ctx in normalized:\n        if not ctx:\n            continue\n        ctx_gap_types = {str(gap_type) for gap_type in ctx.get("gap_types", [])}\n        if not ctx_gap_types:\n            ctx_gap_types = target_gap_types\n        for gap_type in ctx_gap_types & target_gap_types:\n            grouped.setdefault(gap_type, []).append(ctx)\n    return grouped\n'''
    new = '''def _rag_contexts_by_gap(contexts: list[Any], gap_ids: list[str]) -> dict[str, list[dict[str, Any]]]:\n    normalized = [_as_state_dict(ctx) for ctx in contexts]\n    selected = {gap_id: _gap_type_for_runtime_gap(gap_id) for gap_id in gap_ids}\n    grouped: dict[str, list[dict[str, Any]]] = {}\n    for gap_id, gap_type in selected.items():\n        grouped.setdefault(gap_id, [])\n        grouped.setdefault(gap_type, [])\n\n    for ctx in normalized:\n        if not ctx:\n            continue\n        raw_labels = ctx.get("gap_types") or ctx.get("gap_type") or []\n        if isinstance(raw_labels, str):\n            raw_labels = [raw_labels]\n        labels = {str(label) for label in raw_labels if label}\n        normalized_labels = {_gap_type_for_runtime_gap(label) for label in labels}\n\n        matched = False\n        for gap_id, gap_type in selected.items():\n            if gap_id in labels or gap_type in labels or gap_type in normalized_labels:\n                for key in (gap_id, gap_type):\n                    bucket = grouped.setdefault(key, [])\n                    if ctx not in bucket:\n                        bucket.append(ctx)\n                matched = True\n\n        # Contexts without an explicit gap label were produced by a query over\n        # the selected gaps, so retain them for audit rather than silently drop.\n        if not labels and not matched:\n            for gap_id, gap_type in selected.items():\n                for key in (gap_id, gap_type):\n                    bucket = grouped.setdefault(key, [])\n                    if ctx not in bucket:\n                        bucket.append(ctx)\n    return grouped\n'''
    replace_once(old, new)


def patch_selected_gap_filter() -> None:
    old = '''    if parsed:\n        return parsed\n\n    score = state.evidence_weighted_scores or state.scores or {}\n'''
    new = '''    if parsed:\n        selected_gap_ids = set(state.gap_ids)\n        selected_gap_types = {_gap_type_for_runtime_gap(gap_id) for gap_id in state.gap_ids}\n        selected = [\n            item\n            for item in parsed\n            if item.gap_id in selected_gap_ids or item.gap_type.value in selected_gap_types\n        ]\n        if selected:\n            return selected\n\n    score = state.evidence_weighted_scores or state.scores or {}\n'''
    replace_once(old, new)


def add_tests() -> None:
    path = ROOT / "tests/unit/test_runtime_gap_context_contract.py"
    path.write_text(
        '''from __future__ import annotations\n\nfrom src.orchestration.node_impl import (\n    _gap_results_for_mapping,\n    _gap_type_for_runtime_gap,\n    _rag_contexts_by_gap,\n)\nfrom src.orchestration.state import ProductWorkflowState\n\n\ndef _gap(gap_id: str, gap_type: str, *, production_allowed: bool) -> dict:\n    return {\n        "gap_id": gap_id,\n        "gap_type": gap_type,\n        "severity_score": 0.5,\n        "confidence_score": 0.6,\n        "uncertainty": 0.2,\n        "status": "needs_review",\n        "features": {\n            "severity": {\n                "missing_required_signal_count": 0.0,\n                "weak_evidence_count": 0.0,\n                "rejected_evidence_count": 0.0,\n                "unsupported_claim_count": 0.0,\n                "low_confidence_evidence_count": 0.0,\n                "relevant_signal_absence": 0.0,\n                "nvidia_fit_opportunity_signal_count": 0.5,\n                "implementation_complexity_proxy": 0.5,\n                "business_impact_proxy": 0.5,\n                "uncertainty_penalty": 0.2,\n            },\n            "confidence": {\n                "supporting_evidence_count": 0.5,\n                "supporting_source_count": 0.5,\n                "average_evidence_confidence": 0.6,\n                "average_source_quality": 0.6,\n                "cross_source_agreement_count": 0.5,\n                "contradiction_count": 0.0,\n                "extraction_success_rate": 1.0,\n                "source_category_coverage": 0.5,\n            },\n        },\n        "weights": {},\n        "thresholds": {},\n        "supporting_evidence_ids": ["evidence-1"],\n        "production_allowed": production_allowed,\n        "explanation": "test",\n        "blockers": [],\n        "calibration_decision_ids": [\n            "gap_diagnosis.severity_weights",\n            "gap_diagnosis.confidence_weights",\n            "gap_diagnosis.production_threshold",\n            "gap_diagnosis.uncertainty_penalty",\n            "gap_diagnosis.minimum_evidence_coverage",\n        ],\n    }\n\n\ndef test_runtime_gap_id_preserves_semantic_gap_type() -> None:\n    assert _gap_type_for_runtime_gap("gap-3-mlops_deployment_gap") == "mlops_deployment_gap"\n    assert _gap_type_for_runtime_gap("gap-6-computer_vision_gap") == "computer_vision_gap"\n\n\ndef test_rag_context_is_grouped_by_runtime_id_and_semantic_type() -> None:\n    context = {\n        "context_id": "ctx-1",\n        "gap_types": ["gap-3-mlops_deployment_gap"],\n        "product": "NVIDIA AI Enterprise",\n        "content": "MLOps deployment guidance",\n    }\n    grouped = _rag_contexts_by_gap([context], ["gap-3-mlops_deployment_gap"])\n    assert grouped["gap-3-mlops_deployment_gap"] == [context]\n    assert grouped["mlops_deployment_gap"] == [context]\n\n\ndef test_mapping_receives_only_selected_runtime_gaps() -> None:\n    selected_id = "gap-3-mlops_deployment_gap"\n    state = ProductWorkflowState(\n        workflow_id="workflow-test",\n        gap_ids=[selected_id],\n        node_outputs={\n            "gap_output": {\n                "gaps": [\n                    _gap(selected_id, "mlops_deployment_gap", production_allowed=True),\n                    _gap("gap-6-computer_vision_gap", "computer_vision_gap", production_allowed=False),\n                ]\n            }\n        },\n    )\n    gaps = _gap_results_for_mapping(state)\n    assert [gap.gap_id for gap in gaps] == [selected_id]\n''',
        encoding="utf-8",
    )


def main() -> None:
    patch_gap_id_normalization()
    patch_context_flattening()
    patch_context_grouping()
    patch_selected_gap_filter()
    add_tests()


if __name__ == "__main__":
    main()
