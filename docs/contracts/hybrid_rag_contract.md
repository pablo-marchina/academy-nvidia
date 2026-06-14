# Contract: Hybrid RAG + Reranking Hardening (Epic 42)

## Overview

Adds deterministic query planning, BM25 sparse retrieval, RRF/weighted fusion,
cross-encoder reranking, citation packaging, and integration helpers for
Claim Ledger / Dossier / Product Quality — without modifying existing pipeline,
Qdrant, or scoring modules.

## Module: `src/rag/schemas.py` (extended)

### Enums

- `RetrievalMode` — `DENSE_ONLY`, `SPARSE_ONLY`, `HYBRID`, `HYBRID_WITH_RERANK`, `LEXICAL`, `SEMANTIC`

### Schemas

- `RagEvidenceChunk` — chunk_id, source_title, source_url, section, text, score_dense, score_sparse, score_fused, score_rerank, retrieval_mode, corpus_version, metadata_json
- `QueryPlan` — primary_query, keyword_query, technology_filters, target_doc_categories, must_have_terms, optional_terms, metadata_filters
- `RagEvidenceChunkList` — chunks, retrieval_mode, total_raw, total_returned, fallback_reason, degraded

### Invariants

- scores ∈ [0.0, 1.0]
- retrieval_mode is a valid RetrievalMode value
- degraded=True iff a fallback was triggered

## Module: `src/rag/query_planner.py`

### Function: `build_query_plan(sector, product_summary, detected_gaps, claim_types, desired_technologies) -> QueryPlan`

- Deterministic: same inputs → same plan
- No LLM calls
- primary_query from technologies + gaps (OR-joined)
- keyword_query from product_summary tokens (max 8, no stopwords)
- must_have_terms from technologies, gaps, and claim_types
- metadata_filters from target_doc_categories

## Module: `src/rag/sparse_retrieval.py`

### Class: `SparseRetriever`

- Constructor: `SparseRetriever(index: ChunkIndex, k1=1.5, b=0.75)`
- Pre-computes IDF and document lengths on init
- `is_ready` property returns True if IDF map is non-empty
- `retrieve(query: RetrievalQuery, top_k=3) -> list[RetrievedContext]`

### Invariants

- Lifecycle filters: respects include_deprecated/include_expired
- Relevance scores clamped to [0.0, 1.0]
- Empty index or query → empty list

## Module: `src/rag/fusion.py`

### Functions

- `reciprocal_rank_fusion(dense, sparse, top_k=5, dense_weight=0.5, sparse_weight=0.5) -> list[RagEvidenceChunk]`
- `weighted_score_fusion(dense, sparse, top_k=5, dense_weight=0.5, sparse_weight=0.5) -> list[RagEvidenceChunk]`
- `deduplicate_chunks(chunks) -> list[RagEvidenceChunk]`

### Invariants

- score_fused ∈ [0.0, 1.0] (normalized)
- Dedup by chunk_id (first occurrence wins)
- Empty lists → empty result
- score_fused populated on returned chunks

## Module: `src/rag/reranker.py`

### Classes

- `Reranker` — abstract base with `rerank(query: str, chunks, top_k) -> list[RagEvidenceChunk]`
- `NoOpReranker` — returns chunks sorted by score_fused desc, respects top_k
- `OptionalCrossEncoderReranker` — lazy-loads CrossEncoder; falls back to NoOp if unavailable

### Factory: `build_reranker(provider="none") -> Reranker`

### Invariants

- NoOpReranker never fails
- CrossEncoder load failure → silent fallback to NoOp (logging only)
- Invalid provider → NoOpReranker

## Module: `src/rag/hybrid_retriever.py`

### Class: `HybridRagRetriever`

- Constructor: `HybridRagRetriever(chunk_index, embedding_model=None, vector_store=None, reranker=None, sparse_retriever=None, dense_weight=0.5, sparse_weight=0.5, retrieval_mode="dense_only")`
- `resolved_mode` property — effective mode after fallback
- `retrieve(query_plan=None, mode=None, top_k=5) -> RagEvidenceChunkList`

### Fallback chain

- HYBRID_WITH_RERANK → HYBRID → DENSE_ONLY
- HYBRID → DENSE_ONLY (if sparse unavailable)
- SPARSE_ONLY → DENSE_ONLY (if sparse unavailable)
- degraded=True + fallback_reason on any fallback

## Module: `src/rag/citation.py`

### Class: `CitationPackage`

- `citations_json` — list of structured citation dicts
- `evidence_refs_json` — list for Claim Ledger evidence_refs_json
- `source_coverage_summary` — total_chunks, unique_sources, with_url, source_coverage, retrieval_mode, degraded, fallback_reason

### Factory: `build_rag_citation_package(result) -> CitationPackage`

## Module: `src/rag/evidence_refs.py`

### Functions

- `evidence_refs_from_chunks(chunks) -> list[dict]`
- `evidence_refs_from_result(result) -> list[dict]`
- `citation_section_for_dossier(result, max_chunks=5) -> dict`

## Product Quality Integration

### New metrics (in `src/quality/constants.py`)
- rag_retrieval_success, rag_degraded_mode, rag_fallback_count, rag_source_coverage, rag_avg_dense_score, rag_avg_sparse_score, rag_avg_fused_score

### Evaluator (in `src/quality/evaluators/rag_quality.py`)
- `evaluate_rag_retrieval(result: RagEvidenceChunkList) -> dict[str, Any]`

## Dependencies

- `sentence-transformers` (optional, for CrossEncoder) — already an extra
- No new required dependencies

## Not Covered (out of contract scope)

- LLM query planner
- Ragas evaluation integration
- Cohere/API reranker
- Changes to existing pipeline, Qdrant, LangGraph, scoring, diagnosis, recommendation, Action Brief
