from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:180]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_gap_scoring() -> None:
    path = ROOT / "src/diagnosis/gap_diagnosis_scoring.py"
    replace_once(
        path,
        '''    corroborated_absence = (\n        severity_features.relevant_signal_absence >= 0.5\n        and len(evidence_items) >= 3\n        and len(distinct_sources) >= 3\n        and confidence_features.contradiction_count == 0.0\n    )\n''',
        '''    # Absence of a public mention is not evidence that an operational gap\n    # exists. Three independent sources can corroborate a positive signal, but\n    # they cannot turn silence about latency, cost, governance, or MLOps into a\n    # factual diagnosis. Keep the field for audit compatibility and force it off.\n    corroborated_absence = False\n''',
    )
    replace_once(
        path,
        '''    supporting_ids: list[str] = []\n    for item in evidence_items:\n        eid = item.get("id") or item.get("evidence_id") or ""\n        if eid:\n            supporting_ids.append(str(eid))\n''',
        '''    supporting_ids: list[str] = []\n    for item in evidence_items:\n        if not related_keywords or not _text_contains_any(_evidence_text(item), related_keywords):\n            continue\n        eid = item.get("id") or item.get("evidence_id") or ""\n        if eid:\n            supporting_ids.append(str(eid))\n''',
    )
    replace_once(
        path,
        '''    source_category_coverage = 0.0\n    if collection_metrics:\n        categories = collection_metrics.get("source_categories_covered", [])\n        expected = collection_metrics.get("expected_categories", 8)\n        if expected and expected > 0:\n            source_category_coverage = len(categories) / expected\n''',
        '''    source_category_coverage = 0.0\n    if collection_metrics:\n        categories = collection_metrics.get("source_categories_covered", [])\n        observed_count = (\n            len(categories)\n            if isinstance(categories, list)\n            else int(collection_metrics.get("source_category_count", 0) or 0)\n        )\n        minimums = collection_metrics.get("minimums", {})\n        expected = collection_metrics.get("expected_categories")\n        if not isinstance(expected, int | float) or expected <= 0:\n            expected = (minimums.get("source_category_count", 2) if isinstance(minimums, dict) else 2)\n        if expected and expected > 0:\n            source_category_coverage = min(1.0, observed_count / float(expected))\n''',
    )


def patch_orchestration_propagation() -> None:
    path = ROOT / "src/orchestration/node_impl.py"
    replace_once(
        path,
        '''        state_updates={\n            "evidence_items": result.get("evidence_items", []),\n            "startup_profile": result.get("startup_profile", {}),\n        },\n''',
        '''        state_updates={\n            "evidence_items": result.get("evidence_items", []),\n            "startup_profile": result.get("startup_profile", {}),\n            "node_outputs": {\n                **state.node_outputs,\n                "claims": result.get("claims", []),\n                "extraction_metrics": result.get("extraction_metrics", {}),\n            },\n        },\n''',
    )
    replace_once(
        path,
        '''    accepted = state.node_outputs.get("validated_evidence", []) or state.evidence_items\n    evidence_validation = {\n''',
        '''    accepted = state.node_outputs.get("validated_evidence", []) or state.evidence_items\n    claims = state.node_outputs.get("claims", [])\n    if not isinstance(claims, list):\n        claims = []\n    evidence_validation = {\n''',
    )
    replace_once(path, '            claims=[],\n            evidence_validation=evidence_validation,', '            claims=claims,\n            evidence_validation=evidence_validation,')


def patch_contract_tests() -> None:
    path = ROOT / "tests/unit/test_gap_evidence_coverage_contract.py"
    replace_once(
        path,
        '''def test_absence_is_reliable_only_when_three_sources_corroborate_it() -> None:\n    gap_type = GapType.INFERENCE_PERFORMANCE_GAP\n    evidence = [\n        _evidence(1, "The company builds artificial intelligence products."),\n        _evidence(2, "The product serves enterprise customers."),\n        _evidence(3, "The platform automates operational workflows."),\n    ]\n\n    result = diagnose_gaps_quantitative(\n        run_id="corroborated-absence",\n        evidence_items=evidence,\n        accepted_evidence_items=evidence,\n        claims=[],\n        inventory=get_project_decision_inventory(),\n    )\n    gap = next(item for item in result.gaps if item.gap_type == gap_type)\n\n    assert gap.thresholds["observed_evidence_coverage"] == 0.0\n    assert gap.thresholds["corroborated_absence"] == 1.0\n    assert gap.production_allowed is True\n    assert gap.status != GapDiagnosisStatus.NEEDS_MORE_EVIDENCE\n''',
        '''def test_absence_across_three_sources_does_not_invent_an_operational_gap() -> None:\n    gap_type = GapType.INFERENCE_PERFORMANCE_GAP\n    evidence = [\n        _evidence(1, "The company builds artificial intelligence products."),\n        _evidence(2, "The product serves enterprise customers."),\n        _evidence(3, "The platform automates operational workflows."),\n    ]\n\n    result = diagnose_gaps_quantitative(\n        run_id="corroborated-absence",\n        evidence_items=evidence,\n        accepted_evidence_items=evidence,\n        claims=[],\n        inventory=get_project_decision_inventory(),\n    )\n    gap = next(item for item in result.gaps if item.gap_type == gap_type)\n\n    assert gap.thresholds["observed_evidence_coverage"] == 0.0\n    assert gap.thresholds["corroborated_absence"] == 0.0\n    assert gap.production_allowed is False\n    assert gap.status == GapDiagnosisStatus.NEEDS_MORE_EVIDENCE\n    assert gap.supporting_evidence_ids == []\n''',
    )

    path = ROOT / "tests/unit/test_gap_live_evidence_semantics.py"
    text = path.read_text(encoding="utf-8")
    text += '''\n\ndef test_unrelated_gap_is_not_created_from_silence() -> None:\n    evidence = [\n        {\n            "evidence_id": f"ev-{idx}",\n            "source_url": f"https://source{idx}.example/case",\n            "quote_or_evidence": "Computer vision detects weeds in drone imagery.",\n            "source_quality_score": 0.9,\n            "evidence_confidence_score": 0.9,\n            "confidence": "high",\n        }\n        for idx in range(3)\n    ]\n\n    summary = diagnose_gaps_quantitative(\n        run_id="no-false-gap-test",\n        evidence_items=evidence,\n        accepted_evidence_items=evidence,\n    )\n\n    cyber_gap = next(g for g in summary.gaps if g.gap_type == GapType.CYBERSECURITY_AI_GAP)\n    assert cyber_gap.production_allowed is False\n    assert cyber_gap.supporting_evidence_ids == []\n'''
    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch_gap_scoring()
    patch_orchestration_propagation()
    patch_contract_tests()


if __name__ == "__main__":
    main()
