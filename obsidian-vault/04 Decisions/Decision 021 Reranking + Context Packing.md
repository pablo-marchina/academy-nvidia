# Decision 021 — Reranking + Context Packing Determinísticos

**Epic:** 14
**Date:** 2026-06-09

## Context
Epic 14 required reranking and context packing for the RAG pipeline without external calls, LLM, LangGraph, or changes to scoring/diagnosis/recommendation.

## Decision
- Deterministic reranking via composite score: relevance×0.3 + gap_match×0.3 + tech_match×0.2 - provenance - duplicate - irrelevant penalties. Clamped to [0,1].
- Context packing: dedup by chunk_id, classify by gap/tech, apply per-tech (2), per-gap (3), global (5) limits. Metrics: provenance, gap/tech coverage, budget, noise reduction.
- 2 new eval modes: HYBRID_RERANKED, HYBRID_RERANKED_PACKED. 8 new metrics in RagRetrievalMetrics.
- Action Brief: optional packing_result, injects Supporting NVIDIA Context section. RAG remains optional.

## Alternatives
- Cross-encoder reranking (requires model in memory)
- LLM judge (non-deterministic, costly)
- LangGraph orchestration (exceeds zero-dep constraint)

## Status
Implemented in Epic 14. 38 new tests, 276 total.
