from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one match in {path}, found {count}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: str, marker: str, content: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if content.strip() in text:
        return
    count = text.count(marker)
    if count != 1:
        raise RuntimeError(f"Expected exactly one marker in {path}, found {count}: {marker!r}")
    target.write_text(text.replace(marker, content + marker, 1), encoding="utf-8")


# Triton receives one request containing a variable number of documents. The
# documents dimension is not an automatic Triton batch dimension.
replace_once(
    "models/cross_encoder/config.pbtxt",
    'max_batch_size: 64',
    'max_batch_size: 0',
)

# Gap diagnosis must recognize natural technical language and only attach the
# evidence that actually supports each gap family.
diagnosis_helpers = r'''
_GAP_SIGNAL_ALIASES: dict[GapType, tuple[str, ...]] = {
    GapType.COMPUTE_ACCELERATION_GAP: (
        "gpu acceleration", "compute acceleration", "high inference cost",
        "high latency", "throughput bottleneck",
    ),
    GapType.INFERENCE_PERFORMANCE_GAP: (
        "inference latency", "high latency", "low latency", "inference cost",
        "inference performance", "real time inference", "real-time inference",
        "model serving",
    ),
    GapType.TRAINING_SCALABILITY_GAP: (
        "training scalability", "distributed training", "training cost",
        "model training", "fine tuning", "fine-tuning",
    ),
    GapType.MLOPS_DEPLOYMENT_GAP: (
        "mlops", "model deployment", "model serving", "observability",
        "production monitoring", "agent governance",
    ),
    GapType.DATA_PIPELINE_GAP: (
        "data pipeline", "slow data pipeline", "etl", "big data",
        "data processing", "data engineering",
    ),
    GapType.MODEL_OPTIMIZATION_GAP: (
        "model optimization", "inference optimization", "quantization",
        "pruning", "distillation", "model compression",
    ),
    GapType.COMPUTER_VISION_GAP: (
        "computer vision", "visao computacional", "visual inspection",
        "inspecao visual", "image recognition", "object detection",
        "video analytics", "image analytics", "optical character recognition",
    ),
    GapType.GENAI_LLM_GAP: (
        "large language model", "llm", "generative ai", "ia generativa",
        "retrieval augmented generation", "conversational ai", "chatbot",
        "external api dependency",
    ),
    GapType.CYBERSECURITY_AI_GAP: (
        "cybersecurity", "ciberseguranca", "threat detection",
        "security operations", "network anomaly", "malware detection",
    ),
    GapType.NVIDIA_ECOSYSTEM_FIT_GAP: (
        "nvidia ecosystem", "nvidia", "cuda", "gpu acceleration", "gpu computing",
    ),
    GapType.EVIDENCE_COVERAGE_GAP: (
        "insufficient evidence", "missing evidence", "evidence coverage",
    ),
    GapType.TECHNICAL_DEPTH_GAP: (
        "technical architecture", "technical stack", "deployment architecture",
        "model architecture", "infrastructure architecture",
    ),
}


def _gap_signal_keywords(gap_type: GapType) -> list[str]:
    keywords = list(_GAP_SIGNAL_ALIASES.get(gap_type, ()))
    keywords.extend(item.value.replace("_", " ") for item in GAP_TECH_MAP.get(gap_type, []))
    return list(dict.fromkeys(keyword.casefold() for keyword in keywords if keyword))


def _evidence_item_text(item: dict[str, Any]) -> str:
    return str(
        item.get("text")
        or item.get("snippet")
        or item.get("claim")
        or item.get("quote_or_evidence")
        or ""
    )


def _matching_evidence_items(
    evidence_items: list[dict[str, Any]],
    gap_type: GapType,
) -> list[dict[str, Any]]:
    keywords = _gap_signal_keywords(gap_type)
    if not keywords:
        return []
    return [item for item in evidence_items if _text_contains_any(_evidence_item_text(item), keywords)]


def _numeric_evidence_confidence(item: dict[str, Any]) -> float:
    for key in ("evidence_confidence_score", "extraction_confidence", "confidence_score"):
        value = item.get(key)
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value)))
    value = item.get("confidence")
    if isinstance(value, str):
        return {"high": 1.0, "medium": 0.6, "low": 0.3}.get(value.casefold(), 0.0)
    return 0.0


'''
insert_before_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    "def _compute_uncertainty(\n",
    diagnosis_helpers,
)

replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    related_tech_gaps = GAP_TECH_MAP.get(gap_type, [])
    related_keywords = [t.value for t in related_tech_gaps]

    missing_required_signal_count = 0
    for kw in related_keywords:
        if not _text_contains_any(" ".join(all_texts), [kw]):
            missing_required_signal_count += 1
''',
    '''    related_keywords = _gap_signal_keywords(gap_type)
    matching_items = _matching_evidence_items(evidence_items, gap_type)
    matching_claim_count = _count_by_keyword(claim_texts, related_keywords)
    has_relevant_signal = bool(matching_items or matching_claim_count)
    missing_required_signal_count = 0 if has_relevant_signal else 1
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    weak_evidence_count = sum(
        1
        for item in evidence_items
        if isinstance(item.get("evidence_confidence_score"), (int, float))
        and float(item["evidence_confidence_score"]) < 0.4
    )
''',
    '''    weak_evidence_count = sum(
        1 for item in matching_items if _numeric_evidence_confidence(item) < 0.4
    )
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    relevant_signal_absence = missing_required_signal_count / max(1, len(related_keywords)) if related_keywords else 0.0
''',
    '''    relevant_signal_absence = 0.0 if has_relevant_signal else 1.0
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    uncertainty_penalty = _compute_uncertainty(
        evidence_count=len(evidence_items),
        avg_confidence=0.5,
    )
''',
    '''    matching_confidences = [_numeric_evidence_confidence(item) for item in matching_items]
    uncertainty_penalty = _compute_uncertainty(
        evidence_count=len(matching_items),
        avg_confidence=_mean(matching_confidences),
        min_expected=1,
    )
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    ev_texts = _extract_texts_from_items(evidence_items)
    ac_texts = _extract_texts_from_items(accepted_evidence_items)
    claim_texts = [str(c.get("claim_text", "")) for c in claims if isinstance(c, dict)]
    ev_texts + ac_texts + claim_texts

    related_tech_gaps = GAP_TECH_MAP.get(gap_type, [])
    related_keywords = [t.value for t in related_tech_gaps]

    supporting_evidence_count = 0
    if related_keywords:
        for item in evidence_items:
            text = str(item.get("text", "") or item.get("snippet", "") or item.get("claim", ""))
            if _text_contains_any(text, related_keywords):
                supporting_evidence_count += 1
''',
    '''    matching_items = _matching_evidence_items(evidence_items, gap_type)
    supporting_evidence_count = len(matching_items) / max(1, len(evidence_items))
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    for item in evidence_items:
        sid = item.get("source_id") or item.get("url", "")
        if sid:
            source_ids.add(sid)
''',
    '''    for item in matching_items:
        sid = item.get("source_id") or item.get("source_url") or item.get("url", "")
        if sid:
            source_ids.add(str(sid))
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    for item in evidence_items:
        ec = item.get("evidence_confidence_score")
        if isinstance(ec, (int, float)):
            confidences.append(float(ec))
''',
    '''    for item in matching_items:
        confidences.append(_numeric_evidence_confidence(item))
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    for item in evidence_items:
        sq = item.get("source_quality_score")
        if isinstance(sq, (int, float)):
            qualities.append(float(sq))
''',
    '''    for item in matching_items:
        sq = item.get("source_quality_score")
        if isinstance(sq, (int, float)):
            qualities.append(float(sq))
        elif item.get("source_type") == "official_site":
            qualities.append(1.0)
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    for item in evidence_items:
        sid = item.get("source_id") or item.get("url", "")
        claim = str(item.get("text", "") or item.get("snippet", "") or item.get("claim", ""))
''',
    '''    for item in matching_items:
        sid = item.get("source_id") or item.get("source_url") or item.get("url", "")
        claim = _evidence_item_text(item)
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''        supporting_evidence_count=round(min(1.0, supporting_evidence_count / _MAX_SUPPORTING_EVIDENCE), 4),
''',
    '''        supporting_evidence_count=round(min(1.0, supporting_evidence_count), 4),
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    if len(evidence_items) == 0:
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
''',
    '''    matching_items = _matching_evidence_items(evidence_items, gap_type)
    evidence_coverage = len(matching_items) / max(1, len(evidence_items))
    if len(evidence_items) == 0:
        status = GapDiagnosisStatus.NEEDS_MORE_EVIDENCE
        prod_allowed = False
        gap_blockers.append("No evidence items available for gap diagnosis")
    elif not matching_items:
        status = GapDiagnosisStatus.NEEDS_MORE_EVIDENCE
        prod_allowed = False
        gap_blockers.append(f"No evidence semantically supports gap '{gap_type.value}'")
    elif min_evidence_coverage is not None and evidence_coverage < min_evidence_coverage:
        status = GapDiagnosisStatus.NEEDS_MORE_EVIDENCE
        prod_allowed = False
        gap_blockers.append(
            f"Evidence coverage ({round(evidence_coverage, 4)}) below minimum ({min_evidence_coverage})"
        )
''',
)
replace_once(
    "src/diagnosis/gap_diagnosis_scoring.py",
    '''    supporting_ids: list[str] = []
    for item in evidence_items:
        eid = item.get("id") or item.get("evidence_id") or ""
        if eid:
            supporting_ids.append(str(eid))
''',
    '''    supporting_ids: list[str] = []
    for item in matching_items:
        eid = item.get("id") or item.get("evidence_id") or ""
        if eid:
            supporting_ids.append(str(eid))
''',
)

# Mapping provenance has two independent sides: startup evidence supports the
# diagnosed gap; NVIDIA corpus contexts support the NVIDIA technology.
replace_once(
    "src/recommendation/nvidia_technology_mapping.py",
    '''    tech_keywords = [technology.lower(), technology.lower().replace("nvidia ", "")]
    ev_for_tech = [
        item
        for item in evidence_items
        if _text_contains_any(
            str(item.get("text", "") or item.get("snippet", "") or item.get("claim", "")),
            tech_keywords,
        )
    ]
    evidence_count = len(ev_for_tech)
''',
    '''    supporting_evidence_ids = set(gap_result.supporting_evidence_ids if gap_result else [])
    ev_for_tech = [
        item
        for item in evidence_items
        if str(item.get("id") or item.get("evidence_id") or "") in supporting_evidence_ids
    ]
    evidence_count = len(ev_for_tech)
''',
)
replace_once(
    "src/recommendation/nvidia_technology_mapping.py",
    '''        ec = item.get("evidence_confidence_score")
        if isinstance(ec, (int, float)):
            ev_confidences.append(float(ec))
''',
    '''        ec = item.get("evidence_confidence_score", item.get("extraction_confidence"))
        if isinstance(ec, (int, float)):
            ev_confidences.append(float(ec))
        elif isinstance(item.get("confidence"), str):
            ev_confidences.append({"high": 1.0, "medium": 0.6, "low": 0.3}.get(str(item["confidence"]).casefold(), 0.0))
''',
)
replace_once(
    "src/recommendation/nvidia_technology_mapping.py",
    '''        sid = item.get("source_id") or item.get("url", "")
''',
    '''        sid = item.get("source_id") or item.get("source_url") or item.get("url", "")
''',
)
replace_once(
    "src/recommendation/nvidia_technology_mapping.py",
    '''        gap_result = gap_result_by_type.get(gap_type_str)
        rag_ctxs = rag_contexts_by_gap.get(gap_type_str, [])

        for tech in candidate_techs:
''',
    '''        gap_result = gap_result_by_type.get(gap_type_str)
        rag_ctxs = rag_contexts_by_gap.get(gap_type_str, [])
        if gap_result is None or not gap_result.production_allowed or not gap_result.supporting_evidence_ids:
            continue

        for tech in candidate_techs:
''',
)
replace_once(
    "src/recommendation/nvidia_technology_mapping.py",
    '''            ev_ids: list[str] = []
            tech_keywords_search = [tech.lower(), tech.replace("nvidia ", "").strip().lower()]
            for item in evidence_items:
                eid = item.get("id") or item.get("evidence_id") or ""
                if eid and _text_contains_any(
                    str(item.get("text", "") or item.get("snippet", "") or item.get("claim", "")),
                    tech_keywords_search,
                ):
                    ev_ids.append(str(eid))
''',
    '''            ev_ids = list(dict.fromkeys(str(eid) for eid in gap_result.supporting_evidence_ids if eid))
''',
)

# Strengthen the release workflow so it proves the RAG path and output
# provenance instead of only checking container health.
replace_once(
    ".github/workflows/release-validation.yml",
    '''          content = content.replace(
              'replace-with-a-random-database-password',
              'ci-db-4b9de674c49343d5999d8bb8531d1be8d31ee1fa',
          )
''',
    '''          content = content.replace(
              'replace-with-a-random-database-password',
              'ci-db-4b9de674c49343d5999d8bb8531d1be8d31ee1fa',
          )
          content = content.replace(
              'replace-with-a-random-qdrant-api-key',
              'ci-qdrant-9e33e60a68f949fab84379afd8210dcbb781ff99',
          )
''',
)
replace_once(
    ".github/workflows/release-validation.yml",
    '''"name":"documents","shape":[2],"datatype":"BYTES"''',
    '''"name":"documents","shape":[2,1],"datatype":"BYTES"''',
)
replace_once(
    ".github/workflows/release-validation.yml",
    '''              completed|degraded|awaiting_review)
''',
    '''              completed|awaiting_review)
''',
)
validation_step = r'''      - name: Validate real RAG and recommendation output contract
        run: |
          workflow_id=$(python -c "import json; print(json.load(open('release-workflow.json'))['workflow']['id'])")
          curl --fail --silent --show-error \
            "http://localhost:3000/api/workflows/product-runs/${workflow_id}" > workflow-result.json
          curl --fail --silent --show-error \
            "http://localhost:3000/api/workflows/product-runs/${workflow_id}/nodes" > workflow-nodes.json
          python - <<'PY'
          import json
          from pathlib import Path

          payload = json.loads(Path('workflow-result.json').read_text(encoding='utf-8'))
          nodes = json.loads(Path('workflow-nodes.json').read_text(encoding='utf-8'))
          assert payload['status'] in {'completed', 'awaiting_review'}, payload
          assert not payload.get('error_message'), payload

          state = payload['state']
          completed = set(state.get('completed_nodes', []))
          required_nodes = {
              'diagnose_gaps',
              'retrieve_nvidia_context',
              'enhance_contexts_with_techniques',
              'map_nvidia_technologies',
              'rank_recommendations',
              'rank_with_expected_utility',
              'generate_brief',
              'run_quality_gates',
          }
          assert required_nodes <= completed, (required_nodes - completed, payload)
          node_status = {item['node_name']: item['status'] for item in nodes}
          for name in required_nodes:
              assert node_status.get(name) == 'completed', (name, node_status, payload)

          outputs = state.get('node_outputs', {})
          rag = outputs.get('rag_output', {})
          metrics = rag.get('rag_retrieval_metrics', {})
          assert rag.get('rag_retrieval_status') == 'passed', rag
          assert metrics.get('retrieval_mode') == 'bm25_graphrag_qdrant_triton_rerank', metrics
          assert metrics.get('bm25_active') is True, metrics
          assert metrics.get('graphrag_active') is True, metrics
          assert metrics.get('triton_reranker_required') is True, metrics
          assert metrics.get('retrieved_context_count', 0) > 0, metrics
          assert metrics.get('citation_ready_context_count', 0) > 0, metrics
          assert metrics.get('reranked_context_count', 0) > 0, metrics
          assert metrics.get('gaps_without_context_count') == 0, metrics

          contexts = state.get('nvidia_contexts', [])
          assert contexts, state
          assert all(ctx.get('citation_ready') for ctx in contexts), contexts
          assert all(ctx.get('source_id') and ctx.get('url') for ctx in contexts), contexts
          assert all(ctx.get('retrieval_mode') == 'bm25_graphrag_qdrant_triton_rerank' for ctx in contexts), contexts
          assert all(ctx.get('bm25_active') is True for ctx in contexts), contexts
          assert all(ctx.get('graphrag_active') is True for ctx in contexts), contexts
          assert all(ctx.get('triton_reranker_active') is True for ctx in contexts), contexts
          assert all((ctx.get('triton_reranker_metadata') or {}).get('called') is True for ctx in contexts), contexts

          gaps = (outputs.get('gap_output') or {}).get('gaps', [])
          production_gaps = {
              gap['gap_type']: set(gap.get('supporting_evidence_ids') or [])
              for gap in gaps
              if gap.get('production_allowed') and gap.get('supporting_evidence_ids')
          }
          assert production_gaps, gaps
          assert 'computer_vision_gap' in production_gaps, production_gaps
          unsupported = {
              'genai_llm_gap', 'cybersecurity_ai_gap', 'data_pipeline_gap',
              'training_scalability_gap', 'nvidia_ecosystem_fit_gap',
          }
          assert not (unsupported & set(production_gaps)), production_gaps

          mapping_result = outputs.get('nvidia_mapping_result', {})
          mappings = [item for item in mapping_result.get('nvidia_technology_mappings', []) if item.get('production_allowed')]
          assert mappings, mapping_result
          assert len(mappings) <= 4, mappings
          for mapping in mappings:
              assert mapping['gap_type'] in production_gaps, mapping
              assert set(mapping.get('supporting_evidence_ids') or []) <= production_gaps[mapping['gap_type']], mapping
              assert mapping.get('supporting_evidence_ids'), mapping
              assert mapping.get('supporting_rag_context_ids'), mapping
          technologies = {item['nvidia_technology'] for item in mappings}
          assert technologies <= {'TensorRT', 'NVIDIA NIM', 'NVIDIA AI Enterprise', 'NVIDIA API Catalog'}, technologies
          assert 'TensorRT' in technologies, technologies

          recommendation_result = outputs.get('nvidia_recommendation_result', {})
          recommendations = recommendation_result.get('nvidia_recommendations', [])
          assert recommendations, recommendation_result
          assert len(recommendations) <= 2, recommendations
          assert state.get('quality_gates_result', {}).get('status') == 'passed', state.get('quality_gates_result')
          assert state.get('brief'), state
          assert state.get('analysis_run_id'), state
          assert state.get('evidence_ids'), state
          assert state.get('gap_ids'), state
          assert state.get('mapping_ids'), state

          report = {
              'workflow_id': payload['id'],
              'status': payload['status'],
              'completed_nodes': sorted(required_nodes),
              'rag_metrics': metrics,
              'production_gaps': {key: sorted(value) for key, value in production_gaps.items()},
              'production_mappings': mappings,
              'recommendations': recommendations,
              'quality_gates': state.get('quality_gates_result'),
          }
          Path('rag-e2e-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
          print(json.dumps(report, indent=2))
          PY

'''
insert_before_once(
    ".github/workflows/release-validation.yml",
    "      - name: Capture release diagnostics\n",
    validation_step,
)
replace_once(
    ".github/workflows/release-validation.yml",
    '''            workflow-result.json
            compose-ps.txt
''',
    '''            workflow-result.json
            workflow-nodes.json
            rag-e2e-validation.json
            compose-ps.txt
''',
)

# Focused regression tests for semantic gap matching and two-sided provenance.
Path("tests/unit/test_rag_e2e_output_contract.py").write_text(
    r'''from __future__ import annotations

from src.diagnosis.gap_diagnosis_scoring import extract_gap_confidence_features
from src.diagnosis.schemas import (
    GapConfidenceFeatures,
    GapDiagnosisFeatures,
    GapDiagnosisResultItem,
    GapDiagnosisStatus,
    GapSeverityFeatures,
    GapType,
)
import src.recommendation.nvidia_technology_mapping as mapping_module


def _features() -> GapDiagnosisFeatures:
    return GapDiagnosisFeatures(
        severity=GapSeverityFeatures(
            missing_required_signal_count=0.0,
            weak_evidence_count=0.0,
            rejected_evidence_count=0.0,
            unsupported_claim_count=0.0,
            low_confidence_evidence_count=0.0,
            relevant_signal_absence=0.0,
            nvidia_fit_opportunity_signal_count=0.5,
            implementation_complexity_proxy=0.5,
            business_impact_proxy=0.5,
            uncertainty_penalty=0.0,
        ),
        confidence=GapConfidenceFeatures(
            supporting_evidence_count=1.0,
            supporting_source_count=1.0,
            average_evidence_confidence=0.95,
            average_source_quality=1.0,
            cross_source_agreement_count=0.0,
            contradiction_count=0.0,
            extraction_success_rate=1.0,
            source_category_coverage=1.0,
        ),
    )


def _gap(gap_type: GapType, evidence_ids: list[str]) -> GapDiagnosisResultItem:
    return GapDiagnosisResultItem(
        gap_id=f"gap-{gap_type.value}",
        gap_type=gap_type,
        severity_score=0.65,
        confidence_score=0.9,
        uncertainty=0.05,
        status=GapDiagnosisStatus.PASSED,
        features=_features(),
        weights={},
        thresholds={},
        supporting_evidence_ids=evidence_ids,
        production_allowed=True,
    )


def test_natural_computer_vision_phrase_supports_only_cv_gap() -> None:
    evidence = [{
        "evidence_id": "ev-cv",
        "text": "Industrial computer vision and visual inspection for manufacturing plants.",
        "source_id": "official",
        "source_url": "https://example.com/product",
        "source_type": "official_site",
        "extraction_confidence": 0.95,
        "source_quality_score": 1.0,
    }]
    cv = extract_gap_confidence_features(GapType.COMPUTER_VISION_GAP, evidence, evidence, [], {}, {})
    llm = extract_gap_confidence_features(GapType.GENAI_LLM_GAP, evidence, evidence, [], {}, {})
    assert cv.supporting_evidence_count == 1.0
    assert cv.average_evidence_confidence == 0.95
    assert llm.supporting_evidence_count == 0.0


def test_mapping_uses_gap_evidence_and_rag_context_for_distinct_claims(monkeypatch) -> None:
    evidence = [{
        "evidence_id": "ev-cv",
        "text": "Industrial computer vision and visual inspection for manufacturing plants.",
        "source_id": "official",
        "source_url": "https://example.com/product",
        "source_type": "official_site",
        "extraction_confidence": 0.95,
        "source_quality_score": 1.0,
    }]
    context = {
        "context_id": "ctx-tensorrt",
        "chunk_id": "ctx-tensorrt",
        "product": "TensorRT",
        "title": "TensorRT inference optimization",
        "content": "TensorRT optimizes deep-learning inference for computer vision workloads.",
        "source_id": "nvidia-tensorrt",
        "url": "https://docs.nvidia.com/deeplearning/tensorrt/",
        "relevance_score": 0.95,
        "citation_ready": True,
    }
    values = {
        "nvidia_mapping.mapping_score_weights": {
            "gap_severity_score": 1.0,
            "gap_confidence_score": 1.0,
            "rag_context_count_for_technology": 1.0,
            "rag_relevance_mean_for_technology": 1.0,
            "evidence_support_count": 1.0,
            "evidence_confidence_mean": 1.0,
            "source_quality_mean": 1.0,
            "technology_topic_match_count": 1.0,
            "startup_profile_signal_match_count": 0.0,
            "uncertainty_penalty": 0.0,
        },
        "nvidia_mapping.mapping_confidence_weights": {
            "supporting_rag_context_count": 1.0,
            "supporting_evidence_count": 1.0,
            "average_rag_relevance_score": 1.0,
            "average_evidence_confidence_score": 1.0,
            "cross_source_support_count": 1.0,
            "contradiction_count": 0.0,
            "corpus_payload_completeness_rate": 1.0,
        },
        "nvidia_mapping.production_threshold": 0.0,
        "nvidia_mapping.minimum_rag_contexts": 1,
        "nvidia_mapping.minimum_evidence_support": 1,
        "nvidia_mapping.uncertainty_penalty": 0.0,
        "nvidia_mapping.technology_priority_policy": {},
    }
    monkeypatch.setattr(mapping_module, "_lookup_calibration_group", lambda *args, **kwargs: (values, True, []))
    result = mapping_module.build_nvidia_technology_mappings(
        run_id="run-1",
        rag_contexts_by_gap={"computer_vision_gap": [context]},
        gap_results=[
            _gap(GapType.COMPUTER_VISION_GAP, ["ev-cv"]),
            _gap(GapType.GENAI_LLM_GAP, []),
        ],
        gap_metrics=None,
        evidence_items=evidence,
        inventory=[],
    )
    mappings = result["nvidia_technology_mappings"]
    assert mappings
    assert {item["gap_type"] for item in mappings} == {"computer_vision_gap"}
    tensorrt = next(item for item in mappings if item["nvidia_technology"] == "TensorRT")
    assert tensorrt["production_allowed"] is True
    assert tensorrt["supporting_evidence_ids"] == ["ev-cv"]
    assert tensorrt["supporting_rag_context_ids"] == ["ctx-tensorrt"]
    assert "TensorRT" not in evidence[0]["text"]
''',
    encoding="utf-8",
)

print("Applied RAG E2E correctness fixes")
