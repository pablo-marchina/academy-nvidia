# Decision 022 — Pipeline RAG Integration (Step 11)

**Epic:** 14.1
**Date:** 2026-06-09

## Context
Epic 14 delivered reranking and context packing as standalone modules. Epic 14.1 needed to integrate them into the main pipeline so that `StartupActionBrief` receives packed RAG context from the production flow — without external calls, LLM, LangGraph, or changes to scoring/diagnosis/recommendation.

## Decision
- `run_rag_pipeline()` lives in `src/rag/rag_pipeline.py` — keeps RAG logic isolated, independently callable.
- Called as Step 11 inside `run_full_pipeline()` — single entry point for callers.
- 5 optional parameters: `chunk_index`, `embedding_model`, `vector_store`, `reranking_config`, `packing_config` — all default to None (RAG disabled).
- `RagPipelineOutput` wraps `PackingResult` with `retrieval_mode`, `missing_context`, `rag_quality_summary`.
- `build_action_brief()` auto-extracts `packing_result` from `result.rag_output` when `packing_result is None` — backward compatible.
- Step 11 only runs when `gap_diagnosis is not None`.
- RAG does NOT alter `recommended_motion`, scores, or `evidence_used`.

## Alternatives
- RAG as standalone function called externally (adds complexity for callers)
- Always-run RAG (violates optional constraint)
- Modify `build_action_brief()` signature (breaks backward compat)

## Status
Implemented in Epic 14.1. 10 new tests, 286 total.
