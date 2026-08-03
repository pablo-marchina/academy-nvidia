from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one match in {path}: found {count}\n{old[:160]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: Path, old: str, new: str, expected: int) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"Expected {expected} matches in {path}: found {count}\n{old[:160]}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def patch_collection_test() -> None:
    path = ROOT / "tests/unit/test_governed_collection_scope.py"
    replace_once(
        path,
        '    assert result.status.value == "completed"',
        '    assert str(getattr(result.status, "value", result.status)) == "completed"',
    )


def patch_gap_semantics() -> None:
    path = ROOT / "src/diagnosis/gap_diagnosis_scoring.py"
    old = '''def _text_contains_any(text: str, keywords: list[str]) -> bool:\n    lower = text.lower()\n    return any(kw in lower for kw in keywords)\n\n\ndef _extract_texts_from_items(items: list[dict[str, Any]]) -> list[str]:\n    texts: list[str] = []\n    for item in items:\n        text = item.get("text") or item.get("snippet") or item.get("claim") or ""\n        if text:\n            texts.append(str(text))\n    return texts\n'''
    new = '''def _text_contains_any(text: str, keywords: list[str]) -> bool:\n    lower = text.casefold()\n    return any(kw.casefold() in lower for kw in keywords if kw)\n\n\ndef _evidence_text(item: dict[str, Any]) -> str:\n    """Return the canonical natural-language evidence payload across schemas."""\n    return str(\n        item.get("text")\n        or item.get("quote_or_evidence")\n        or item.get("snippet")\n        or item.get("claim")\n        or ""\n    )\n\n\n_TECHNICAL_GAP_KEYWORD_ALIASES: dict[str, list[str]] = {\n    "external_api_dependency": [\n        "external api", "api externa", "third-party api", "api dependency",\n        "openai api", "anthropic api", "model api",\n    ],\n    "high_inference_cost": [\n        "inference cost", "custo de inferência", "custo de inferencia",\n        "serving cost", "cost per token", "gpu cost",\n    ],\n    "high_latency": [\n        "high latency", "latência", "latencia", "inference speed",\n        "real-time inference", "inferência em tempo real", "inferencia em tempo real",\n    ],\n    "agent_governance_gap": [\n        "ai agent", "agente de ia", "agentes de ia", "agentic",\n        "guardrail", "governance", "governança", "governanca",\n    ],\n    "observability_gap": [\n        "observability", "observabilidade", "monitoring", "monitoramento",\n        "telemetry", "telemetria", "tracing",\n    ],\n    "model_evaluation_gap": [\n        "model evaluation", "avaliação de modelo", "avaliacao de modelo",\n        "benchmark", "evaluation framework", "evals",\n    ],\n    "privacy_or_controlled_deployment_gap": [\n        "privacy", "privacidade", "on-premise", "on premises", "on-prem",\n        "controlled deployment", "data sovereignty", "soberania de dados",\n    ],\n    "slow_data_pipeline": [\n        "data pipeline", "pipeline de dados", "etl", "data processing",\n        "processamento de dados", "stream processing",\n    ],\n    "heavy_tabular_processing": [\n        "tabular", "dados tabulares", "dataframe", "data frame",\n        "analytics workload", "carga analítica", "carga analitica",\n    ],\n    "voice_need": ["voice", "speech", "voz", "audio", "áudio", "transcription"],\n    "simulation_need": [\n        "simulation", "simulação", "simulacao", "digital twin", "gêmeo digital", "gemeo digital",\n    ],\n    "computer_vision_need": [\n        "computer vision", "visão computacional", "visao computacional",\n        "image recognition", "image analysis", "análise de imagem", "analise de imagem",\n        "drone imagery", "medical imaging", "diagnóstico por imagem", "diagnostico por imagem",\n        "object detection", "plantas daninhas",\n    ],\n    "robotics_need": ["robotics", "robótica", "robotica", "robot", "autonomous machine"],\n    "healthcare_compliance_need": [\n        "healthcare", "saúde", "saude", "medical", "medicina", "patient", "paciente",\n        "clinical", "clínico", "clinico", "diagnóstico", "diagnostico",\n    ],\n    "ai_cybersecurity_need": [\n        "cybersecurity", "cibersegurança", "ciberseguranca", "threat detection",\n        "fraud detection", "security operations",\n    ],\n}\n\n\ndef _technical_gap_keywords(technical_gaps: list[Any]) -> list[str]:\n    keywords: list[str] = []\n    for gap in technical_gaps:\n        value = str(getattr(gap, "value", gap))\n        candidates = [value, value.replace("_", " "), *_TECHNICAL_GAP_KEYWORD_ALIASES.get(value, [])]\n        for candidate in candidates:\n            normalized = candidate.strip().casefold()\n            if normalized and normalized not in keywords:\n                keywords.append(normalized)\n    return keywords\n\n\ndef _extract_texts_from_items(items: list[dict[str, Any]]) -> list[str]:\n    return [text for item in items if (text := _evidence_text(item))]\n'''
    replace_once(path, old, new)
    replace_all(
        path,
        '    related_keywords = [t.value for t in related_tech_gaps]',
        '    related_keywords = _technical_gap_keywords(related_tech_gaps)',
        2,
    )
    replace_all(
        path,
        '            text = str(item.get("text", "") or item.get("snippet", "") or item.get("claim", ""))',
        '            text = _evidence_text(item)',
        1,
    )
    replace_all(
        path,
        '        claim = str(item.get("text", "") or item.get("snippet", "") or item.get("claim", ""))',
        '        claim = _evidence_text(item)',
        1,
    )
    replace_all(
        path,
        '        sid = item.get("source_id") or item.get("url", "")',
        '        sid = item.get("source_url") or item.get("url") or item.get("source_id") or ""',
        2,
    )
    replace_once(
        path,
        '            str(item.get("text") or item.get("snippet") or item.get("claim") or ""),',
        '            _evidence_text(item),',
    )
    replace_once(
        path,
        '        str(item.get("source_id") or item.get("source_url") or item.get("url") or "").strip()',
        '        str(item.get("source_url") or item.get("url") or item.get("source_id") or "").strip()',
    )


def patch_investigative_rag() -> None:
    path = ROOT / "src/rag/rag_service_factory.py"
    replace_once(
        path,
        'from src.diagnosis.schemas import GAP_TECH_MAP, GapDiagnosisResultItem, GapDiagnosisSummary',
        'from src.diagnosis.schemas import (\n    GAP_TECH_MAP,\n    GapDiagnosisResultItem,\n    GapDiagnosisStatus,\n    GapDiagnosisSummary,\n)',
    )
    old = '''        calibrated_gaps = [g for g in gap_items if g.production_allowed]\n\n        if not calibrated_gaps:\n            return QdrantRagService._empty_result(\n                status="rag_blocked_no_calibrated_gaps",\n                rag_retrieval_status="blocked_no_calibrated_gaps",\n                blockers=["No calibrated gaps with production_allowed=True"],\n                gap_count=len(gap_items),\n                calibrated_gap_count=0,\n                missing_rag_calibration_count=missing_rag_calibration_count,\n            )\n'''
    new = '''        production_gaps = [g for g in gap_items if g.production_allowed]\n        investigative_mode = False\n        calibrated_gaps = production_gaps\n\n        # NVIDIA retrieval can help investigate a calibrated hypothesis even when\n        # company evidence is not yet sufficient for a production decision. Keep\n        # this mode explicit and force the RAG result to needs_review; downstream\n        # release validation must never treat it as decision-ready.\n        if not calibrated_gaps:\n            investigative_candidates = [\n                g\n                for g in gap_items\n                if g.status in {GapDiagnosisStatus.NEEDS_MORE_EVIDENCE, GapDiagnosisStatus.NEEDS_REVIEW}\n                and g.calibration_decision_ids\n                and g.severity_score > 0.0\n            ]\n            calibrated_gaps = sorted(\n                investigative_candidates,\n                key=lambda item: (item.severity_score, item.confidence_score),\n                reverse=True,\n            )[:3]\n            investigative_mode = bool(calibrated_gaps)\n\n        if not calibrated_gaps:\n            diagnostics = [\n                {\n                    "gap_id": g.gap_id,\n                    "status": g.status.value,\n                    "severity": g.severity_score,\n                    "confidence": g.confidence_score,\n                    "production_allowed": g.production_allowed,\n                    "blockers": g.blockers,\n                }\n                for g in gap_items[:5]\n            ]\n            return QdrantRagService._empty_result(\n                status="rag_blocked_no_calibrated_gaps",\n                rag_retrieval_status="blocked_no_calibrated_gaps",\n                blockers=[f"No retrieval-eligible calibrated gaps; diagnostics={diagnostics}"],\n                gap_count=len(gap_items),\n                calibrated_gap_count=0,\n                missing_rag_calibration_count=missing_rag_calibration_count,\n            )\n'''
    replace_once(path, old, new)
    replace_once(
        path,
        '            "rag_blocker_count": 0,\n        }',
        '            "rag_blocker_count": 0,\n            "investigative_mode": investigative_mode,\n            "production_gap_count": len(production_gaps),\n        }',
    )
    old_status = '''        if retrieved_context_count == 0:\n            rag_retrieval_status = "needs_review"\n            top_status = "rag_needs_review"\n            review_required = True\n        elif gaps_without_context > 0:\n'''
    new_status = '''        if investigative_mode:\n            rag_retrieval_status = "needs_review"\n            top_status = "rag_needs_review"\n            review_required = True\n        elif retrieved_context_count == 0:\n            rag_retrieval_status = "needs_review"\n            top_status = "rag_needs_review"\n            review_required = True\n        elif gaps_without_context > 0:\n'''
    replace_once(path, old_status, new_status)
    replace_once(
        path,
        '            "blockers": None,\n        }',
        '            "blockers": (\n                ["RAG contexts were produced for calibrated hypotheses only; company gap evidence still requires review."]\n                if investigative_mode\n                else None\n            ),\n        }',
    )


def patch_live_report() -> None:
    path = ROOT / "scripts/validate_live_outputs.py"
    replace_once(
        path,
        '''    completed = workflow.get("status") in {"completed", "degraded", "awaiting_review"}\n    classification_ok = classification in case["expected_classifications"]\n    recommendation_ok = bool(expected_match)\n    provenance_ok = supporting_rec_count > 0\n    output_complete = all(output_fields.values())\n    passed = completed and classification_ok and recommendation_ok and provenance_ok and output_complete\n''',
        '''    completed = workflow.get("status") in {"completed", "degraded", "awaiting_review"}\n    node_outputs = state.get("node_outputs") or {}\n    rag_output = node_outputs.get("rag_output") if isinstance(node_outputs, dict) else {}\n    gap_output = node_outputs.get("gap_output") if isinstance(node_outputs, dict) else {}\n    if not isinstance(rag_output, dict):\n        rag_output = {}\n    if not isinstance(gap_output, dict):\n        gap_output = {}\n    rag_retrieval_status = str(rag_output.get("rag_retrieval_status") or "missing")\n    decision_ready = rag_retrieval_status == "passed"\n    classification_ok = classification in case["expected_classifications"]\n    recommendation_ok = bool(expected_match)\n    provenance_ok = supporting_rec_count > 0\n    output_complete = all(output_fields.values())\n    passed = (\n        completed\n        and decision_ready\n        and classification_ok\n        and recommendation_ok\n        and provenance_ok\n        and output_complete\n    )\n''',
    )
    replace_once(
        path,
        '            "collection_metrics": (state.get("node_outputs") or {}).get("collection_metrics", {}),',
        '''            "collection_metrics": node_outputs.get("collection_metrics", {}),\n            "rag_retrieval_status": rag_retrieval_status,\n            "decision_ready": decision_ready,\n            "rag_metrics": rag_output.get("rag_retrieval_metrics", {}),\n            "gap_diagnosis_status": gap_output.get("gap_diagnosis_status"),\n            "gap_metrics": gap_output.get("metrics", {}),\n            "gap_diagnostics": [\n                {\n                    "gap_id": gap.get("gap_id"),\n                    "gap_type": gap.get("gap_type"),\n                    "status": gap.get("status"),\n                    "severity_score": gap.get("severity_score"),\n                    "confidence_score": gap.get("confidence_score"),\n                    "production_allowed": gap.get("production_allowed"),\n                    "thresholds": gap.get("thresholds", {}),\n                    "blockers": gap.get("blockers", []),\n                }\n                for gap in gap_output.get("gaps", [])\n                if isinstance(gap, dict)\n            ],''',
    )


def add_tests() -> None:
    path = ROOT / "tests/unit/test_gap_live_evidence_semantics.py"
    path.write_text(
        '''from __future__ import annotations\n\nfrom src.diagnosis.gap_diagnosis_scoring import diagnose_gaps_quantitative\nfrom src.diagnosis.schemas import GapType\n\n\ndef test_natural_quote_evidence_and_source_urls_make_relevant_gap_retrieval_eligible() -> None:\n    evidence = [\n        {\n            "evidence_id": f"ev-{idx}",\n            "source_url": f"https://source{idx}.example/case",\n            "quote_or_evidence": (\n                "Computer vision and drone imagery identify plantas daninhas using image analysis."\n            ),\n            "source_quality_score": 0.9,\n            "evidence_confidence_score": 0.9,\n            "confidence": "high",\n        }\n        for idx in range(3)\n    ]\n\n    summary = diagnose_gaps_quantitative(\n        run_id="live-evidence-test",\n        evidence_items=evidence,\n        accepted_evidence_items=evidence,\n        collection_metrics={\n            "source_categories_covered": ["official_site", "news"],\n            "expected_categories": 2,\n        },\n        extraction_metrics={"total_extractions": 3, "failed_extractions": 0},\n    )\n\n    cv_gap = next(g for g in summary.gaps if g.gap_type == GapType.COMPUTER_VISION_GAP)\n    assert cv_gap.production_allowed is True\n    assert cv_gap.thresholds["observed_evidence_coverage"] == 1.0\n    assert cv_gap.features.confidence.supporting_source_count > 0.0\n    assert len(cv_gap.supporting_evidence_ids) == 3\n''',
        encoding="utf-8",
    )


def main() -> None:
    patch_collection_test()
    patch_gap_semantics()
    patch_investigative_rag()
    patch_live_report()
    add_tests()


if __name__ == "__main__":
    main()
