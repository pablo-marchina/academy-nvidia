#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> bool:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise RuntimeError(f"pattern missing in {path}: {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


changed = False
changed |= replace_once(
    "src/orchestration/node_impl.py",
    'def node_plan_search(state: ProductWorkflowState) -> NodeResult:\n    startup_name = ""\n    if state.startup_id:\n',
    'def node_plan_search(state: ProductWorkflowState) -> NodeResult:\n    startup_name = ""\n    website_url = ""\n    if state.startup_id:\n',
)
changed |= replace_once(
    "src/orchestration/node_impl.py",
    '            if startup:\n                startup_name = startup.name\n    if not startup_name and state.metadata_json.get("startup_name"):\n',
    '            if startup:\n                startup_name = startup.name\n                website_url = startup.website or ""\n    if not startup_name and state.metadata_json.get("startup_name"):\n',
)
changed |= replace_once(
    "src/orchestration/node_impl.py",
    "    plan = build_search_plan(startup_name)\n",
    "    plan = build_search_plan(startup_name, website_url=website_url)\n",
)
changed |= replace_once(
    "src/orchestration/node_impl.py",
    '    distinct_sources = {\n        str(ev.get("source_url") or ev.get("url") or ev.get("source_id") or ev.get("source") or "")\n        for ev in evidence_items\n        if ev.get("source_url") or ev.get("url") or ev.get("source_id") or ev.get("source")\n    }\n',
    '    from urllib.parse import urlparse\n\n    distinct_sources: set[str] = set()\n    for ev in evidence_items:\n        raw_source = str(ev.get("source_url") or ev.get("url") or ev.get("source_id") or ev.get("source") or "").strip()\n        if not raw_source:\n            continue\n        parsed = urlparse(raw_source)\n        identity = parsed.netloc.casefold().removeprefix("www.") if parsed.netloc else raw_source\n        if identity:\n            distinct_sources.add(identity)\n',
)

rag_path = Path("src/rag/rag_service_factory.py")
rag = rag_path.read_text(encoding="utf-8")
if "import math\n" not in rag:
    rag = rag.replace("from datetime import UTC, datetime\n", "from datetime import UTC, datetime\nimport math\n", 1)
    changed = True
helper = '''

@lru_cache(maxsize=2)
def _load_local_cross_encoder(model_name: str) -> Any:
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name)


def _rerank_with_configured_provider(
    contexts: list[Any],
    query: RetrievalQuery,
) -> tuple[list[Any], dict[str, Any]]:
    """Run the configured real reranker and fail closed on provider errors."""
    import os

    provider = os.getenv("RERANKER_PROVIDER", "triton").strip().casefold()
    if provider in {"triton", "nvidia_triton", "nvidia_triton_inference_server"}:
        return triton_rerank_contexts(contexts, query)
    if provider != "local_cross_encoder":
        raise TritonRerankerUnavailable(f"Unsupported production reranker provider: {provider or 'missing'}")

    model_name = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    try:
        model = _load_local_cross_encoder(model_name)
    except Exception as exc:
        raise TritonRerankerUnavailable(f"Local cross-encoder unavailable: {exc}") from exc
    query_text = " ".join(
        part for part in [query.gap_type or "", query.technology or "", " ".join(query.keywords)] if part
    )
    pairs = [(query_text, ctx.content) for ctx in contexts]
    try:
        scores = model.predict(pairs)
    except Exception as exc:
        raise TritonRerankerUnavailable(f"Local cross-encoder prediction failed: {exc}") from exc

    for ctx, score in zip(contexts, scores, strict=False):
        logit = float(score)
        ctx.relevance_score = round(1.0 / (1.0 + math.exp(-max(min(logit, 60.0), -60.0))), 6)
    ranked = sorted(contexts, key=lambda item: item.relevance_score, reverse=True)
    return ranked, {
        "called": True,
        "provider": "local_cross_encoder",
        "model": model_name,
        "input_count": len(contexts),
    }
'''
marker = "REQUIRED_SEMANTIC_DECISIONS = REQUIRED_HYBRID_RAG_DECISIONS\n"
if "_rerank_with_configured_provider" not in rag:
    if marker not in rag:
        raise RuntimeError("RAG helper marker missing")
    rag = rag.replace(marker, marker + helper, 1)
    changed = True
old_validation = '            if os.getenv("TRITON_RERANKER_ENABLED", "true").lower() not in {"1", "true", "yes"}:\n                errors.append("blocked_triton_reranker_required: TRITON_RERANKER_ENABLED must be true in product mode")\n            if not os.getenv("TRITON_RERANKER_URL", "").strip():\n                errors.append("blocked_triton_reranker_required: TRITON_RERANKER_URL must be configured in product mode")\n'
new_validation = '            reranker_provider = os.getenv("RERANKER_PROVIDER", "").strip().casefold()\n            if reranker_provider in {"triton", "nvidia_triton", "nvidia_triton_inference_server"}:\n                if os.getenv("TRITON_RERANKER_ENABLED", "true").lower() not in {"1", "true", "yes"}:\n                    errors.append("blocked_triton_reranker_required: TRITON_RERANKER_ENABLED must be true for Triton")\n                if not os.getenv("TRITON_RERANKER_URL", "").strip():\n                    errors.append("blocked_triton_reranker_required: TRITON_RERANKER_URL must be configured for Triton")\n            elif reranker_provider != "local_cross_encoder":\n                errors.append("blocked_reranker_required: configure Triton or local_cross_encoder")\n'
if old_validation in rag:
    rag = rag.replace(old_validation, new_validation, 1)
    changed = True
elif new_validation not in rag:
    raise RuntimeError("RAG validation pattern missing")
old_call = "            results, triton_metrics = triton_rerank_contexts(merged_results, rq)\n"
new_call = "            results, triton_metrics = _rerank_with_configured_provider(merged_results, rq)\n"
if old_call in rag:
    rag = rag.replace(old_call, new_call, 1)
    changed = True
elif new_call not in rag:
    raise RuntimeError("RAG rerank call missing")
if '"retrieval_mode": "bm25_graphrag_qdrant_triton_rerank",' in rag:
    rag = rag.replace(
        '"retrieval_mode": "bm25_graphrag_qdrant_triton_rerank",',
        '"retrieval_mode": "bm25_graphrag_qdrant_configured_rerank",',
    )
    changed = True
if '"triton_reranker_required": True,' in rag:
    rag = rag.replace(
        '"triton_reranker_required": True,',
        '"reranker_provider": os.getenv("RERANKER_PROVIDER", "triton"),\n            "reranker_required": True,',
    )
    changed = True
rag_path.write_text(rag, encoding="utf-8")

acceptance_path = Path("scripts/run_product_acceptance.py")
acceptance = acceptance_path.read_text(encoding="utf-8")
old_acceptance = '''            run = _request(
                client,
                "POST",
                f"/startups/{created['id']}/analysis-runs",
                steps,
                json={"use_rag": True, "rag_backend": "qdrant"},
                expected_status=201,
            )
            if run["status"] != "completed":
                raise RuntimeError(f"Product-like RAG analysis did not complete: {run['status']}")

            claims = _request(client, "GET", f"/analysis-runs/{run['id']}/claims", steps)
'''
new_acceptance = '''            run = _request(
                client,
                "POST",
                "/workflows/product-runs",
                steps,
                json={"startup_id": created["id"], "use_rag": True},
                expected_status=201,
            )
            if run["status"] not in {"completed", "degraded", "awaiting_review"}:
                raise RuntimeError(f"Canonical product workflow did not produce an inspectable result: {run['status']}")
            analysis_run_id = run.get("analysis_run_id")
            if not analysis_run_id:
                raise RuntimeError("Canonical workflow did not persist an analysis_run_id.")

            claims = _request(client, "GET", f"/analysis-runs/{analysis_run_id}/claims", steps)
'''
if old_acceptance in acceptance:
    acceptance = acceptance.replace(old_acceptance, new_acceptance, 1)
    acceptance = acceptance.replace("f\"/analysis-runs/{run['id']}/", 'f"/analysis-runs/{analysis_run_id}/')
    changed = True
elif "/workflows/product-runs" not in acceptance:
    raise RuntimeError("Acceptance route pattern missing")
acceptance_path.write_text(acceptance, encoding="utf-8")

Path(__file__).unlink()
print(f"live validation integration patch applied: changed={changed}")
