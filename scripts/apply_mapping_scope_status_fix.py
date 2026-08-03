from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src/recommendation/nvidia_technology_mapping.py"


def replace_once(old: str, new: str) -> None:
    text = PATH.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match, found {count}: {old[:240]}")
    PATH.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_selected_scope() -> None:
    old = '''    for gap_type_str, candidate_techs in GAP_TECHNOLOGY_CANDIDATES.items():\n        gap_result = gap_result_by_type.get(gap_type_str)\n        rag_ctxs = rag_contexts_by_gap.get(gap_type_str, [])\n'''
    new = '''    selected_gap_types = set(gap_result_by_type)\n    for gap_type_str, candidate_techs in GAP_TECHNOLOGY_CANDIDATES.items():\n        if gap_type_str not in selected_gap_types:\n            continue\n        gap_result = gap_result_by_type[gap_type_str]\n        rag_ctxs = rag_contexts_by_gap.get(gap_type_str, [])\n'''
    replace_once(old, new)


def patch_overall_status() -> None:
    old = '''    if is_blocked:\n        overall_status = NvidiaMappingStatus.BLOCKED_UNCALIBRATED_MAPPING.value\n    elif any(m.blockers and "No RAG contexts" in " ".join(m.blockers) for m in mappings) and not any(\n        m.production_allowed for m in mappings\n    ):\n        overall_status = NvidiaMappingStatus.NEEDS_MORE_EVIDENCE.value\n    elif any(m.production_allowed for m in mappings):\n        overall_status = NvidiaMappingStatus.PASSED.value\n    else:\n        overall_status = NvidiaMappingStatus.NEEDS_REVIEW.value\n'''
    new = '''    if is_blocked:\n        overall_status = NvidiaMappingStatus.BLOCKED_UNCALIBRATED_MAPPING.value\n    elif any(m.production_allowed for m in mappings):\n        overall_status = NvidiaMappingStatus.PASSED.value\n    elif any(m.supporting_rag_context_ids and m.supporting_evidence_ids for m in mappings):\n        # At least one candidate is evidence-grounded and RAG-grounded. A score\n        # below the calibrated production threshold requires review; unsupported\n        # sibling candidates must not downgrade the whole gap to missing evidence.\n        overall_status = NvidiaMappingStatus.NEEDS_REVIEW.value\n    elif mappings:\n        overall_status = NvidiaMappingStatus.NEEDS_MORE_EVIDENCE.value\n    else:\n        overall_status = NvidiaMappingStatus.FAILED.value\n'''
    replace_once(old, new)


def add_tests() -> None:
    path = ROOT / "tests/unit/test_mapping_selected_scope_contract.py"
    path.write_text(
        '''from __future__ import annotations\n\nfrom src.diagnosis.gap_diagnosis_scoring import diagnose_gaps_quantitative\nfrom src.diagnosis.schemas import GapType\nfrom src.recommendation.nvidia_technology_mapping import (\n    GAP_TECHNOLOGY_CANDIDATES,\n    build_nvidia_technology_mappings,\n)\n\n\ndef test_mapping_only_builds_candidates_for_selected_gap_and_reviews_supported_low_score() -> None:\n    evidence = [\n        {\n            "evidence_id": f"ev-{idx}",\n            "source_url": f"https://source{idx}.example/case",\n            "quote_or_evidence": "Visão computacional detecta plantas daninhas em imagens de drones.",\n            "source_quality_score": 0.75,\n            "evidence_confidence_score": 0.75,\n            "confidence": "high",\n        }\n        for idx in range(3)\n    ]\n    diagnosis = diagnose_gaps_quantitative(\n        run_id="selected-mapping-scope",\n        evidence_items=evidence,\n        accepted_evidence_items=evidence,\n    )\n    cv_gap = next(g for g in diagnosis.gaps if g.gap_type == GapType.COMPUTER_VISION_GAP)\n    contexts = [\n        {\n            "context_id": "ctx-tensorrt",\n            "chunk_id": "ctx-tensorrt",\n            "product": "TensorRT",\n            "nvidia_technology": "TensorRT",\n            "title": "TensorRT computer vision inference",\n            "content": "TensorRT optimizes computer vision inference workloads.",\n            "source_id": "nvidia-tensorrt",\n            "url": "https://docs.nvidia.example/tensorrt",\n            "relevance_score": 0.55,\n            "gap_types": ["computer_vision_gap"],\n        }\n    ]\n\n    result = build_nvidia_technology_mappings(\n        run_id="selected-mapping-scope",\n        rag_contexts_by_gap={cv_gap.gap_id: contexts, "computer_vision_gap": contexts},\n        gap_results=[cv_gap],\n        gap_metrics=diagnosis.metrics,\n        evidence_items=evidence,\n    )\n\n    mappings = result["nvidia_technology_mappings"]\n    assert len(mappings) == len(GAP_TECHNOLOGY_CANDIDATES["computer_vision_gap"])\n    assert {item["gap_type"] for item in mappings} == {"computer_vision_gap"}\n    supported = [item for item in mappings if item["supporting_rag_context_ids"]]\n    assert supported\n    assert result["mapping_status"] in {"passed", "needs_review"}\n    assert result["mapping_status"] != "needs_more_evidence"\n''',
        encoding="utf-8",
    )


def main() -> None:
    patch_selected_scope()
    patch_overall_status()
    add_tests()


if __name__ == "__main__":
    main()
