# Epic 14 — Reranking + Context Packing Determinísticos

**Date:** 2026-06-09
**Status:** Concluído

## Summary
Adicionou reranking determinístico e context packing ao pipeline RAG para fornecer contextos NVIDIA limpos, organizados e relevantes ao Startup Action Brief. Sem LLM, sem chamadas externas, sem LangGraph.

## Created
- `src/rag/reranking.py` — deterministic composite score with RerankingConfig
- `src/rag/context_packing.py` — dedup, classify, limit, metrics; build_supporting_contexts()
- 5 new schemas: RerankingConfig, PackedContext, DroppedContext, PackingConfig, PackingResult, SupportingNvidiaContext
- 2 new eval modes: HYBRID_RERANKED, HYBRID_RERANKED_PACKED
- 8 new metrics in RagRetrievalMetrics (Epic 14 fields)
- 3 optional fields in Action Brief schemas for packed context

## Key Decisions
- Reranking formula: relevance_score×0.3 + gap/tech boosts + provenance penalty — no LLM
- Packing limits: per-tech=2, per-gap=3, global=5 — all configurable
- HYBRID_RERANKED = hybrid retrieve + rerank; HYBRID_RERANKED_PACKED = hybrid + rerank + pack
- PackedContext converted to RetrievedContext in eval layer to preserve schema compat
- RAG remains optional — Action Brief works without packing_result

## Test Results
38 novos testes (9 reranking, 13 packing, 11 eval, 5 brief). 276 testes totais, todos passando.
