# Epic 14.1 — Integrate RAG Reranking + Context Packing into Main Pipeline

**Date:** 2026-06-09
**Status:** Concluído

## Summary
Integrou `run_rag_pipeline()` como Step 11 opcional no pipeline principal (`run_full_pipeline()`). RAG coleta contextos por gap+tech, deduplica, reranka (opcional), empacota (opcional) e propaga `RagPipelineOutput` ao `PipelineResult`. O `build_action_brief()` extrai automaticamente o `packing_result` para as seções "Supporting NVIDIA Context". RAG não altera scoring, diagnosis ou `recommended_motion`. 10 novos testes de integração.

## Created
- `src/rag/rag_pipeline.py` — `run_rag_pipeline()` orchestration
- `RagPipelineOutput` schema em `src/rag/schemas.py`
- Step 11 em `src/pipeline/run_pipeline.py` — 5 parâmetros RAG opcionais (chunk_index, embedding_model, vector_store, reranking_config, packing_config)
- Auto-extração em `src/briefing/action_brief.py`
- 10 testes em `tests/unit/test_pipeline_rag.py`

## Key Decisions
- RAG dentro de `run_full_pipeline()` como Step 11 — entrada única, opcional via None
- `run_rag_pipeline()` separada em `src/rag/rag_pipeline.py` — RAG fora de `run_pipeline.py`
- `RagPipelineOutput` wrappa `PackingResult` com retrieval_mode, missing_context, rag_quality_summary
- Auto-extração no `build_action_brief()` — zero mudança em callers existentes
- Step 11 só executa quando gap_diagnosis não é None

## Test Results
10 novos testes (pipeline com contextos, sem RAG, empty index, brief section, dropped not in brief, motion unchanged, provenance, quality summary, backward compat, lexical mode). 286 testes totais, todos passando.
