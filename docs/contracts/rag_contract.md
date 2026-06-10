# RAG Module Contract

**Module**: `src/rag/`
**Last updated**: 2026-06-10
**Epic**: 11 — Product RAG / Playbook Retrieval; 13 — Embeddings + Vector Store Retrieval; 14 — Reranking + Context Packing; 14.1 — Pipeline Integration; 15 — Persistent Vector Store with Qdrant

## Scope

Provide deterministic lexical retrieval and **optional semantic/hybrid retrieval** of NVIDIA documentation snippets to enrich Startup Action Briefs. The module defines ingestion (Markdown → chunks), indexing (in-memory by gap_type and product), lexical retrieval (scoring), **semantic retrieval (embedding + vector store)**, hybrid retrieval (RRF fusion), **deterministic reranking**, **context packing** (dedup, gap/tech limits, provenance filtering), playbook orchestration, and **optional Qdrant persistent vector store**.

## Public API

### `src.rag.ingestion`

| Function | Signature | Returns |
|---|---|---|
| `load_sources()` | `() -> dict[str, RagSource]` | Source metadata from `sources.yaml` |
| `load_markdown_document(path)` | `(Path) -> RagDocument | None` | Single Markdown file as document |
| `chunk_document(doc, sources)` | `(RagDocument, dict[str, RagSource]) -> list[RagChunk]` | Split by `##` headings, merge metadata |
| `load_and_chunk_corpus()` | `() -> list[RagChunk]` | Full corpus ingestion pipeline |

### `src.rag.retrieval`

| Class / Function | Signature | Returns |
|---|---|---|
| `ChunkIndex(chunks)` | `(list[RagChunk] | None)` | In-memory index with `by_gap` and `by_tech` |
| `.retrieve(query, top_k=3)` | `(RetrievalQuery, int) -> list[RetrievedContext]` | Scored results |
| `.retrieve_by_gap_type(gap_type, top_k=3)` | `(str, int) -> list[RetrievedContext]` | Shorthand for gap-only query |
| `.retrieve_by_technology(technology, top_k=3)` | `(str, int) -> list[RetrievedContext]` | Shorthand for tech-only query |
| `build_default_index()` | `() -> ChunkIndex` | Index from default corpus path |

### `src.rag.embeddings`

| Class / Function | Signature | Returns |
|---|---|---|
| `EmbeddingProvider` | Abstract base class | `embed(text)`, `embed_batch(texts)` |
| `MockEmbeddingProvider(vector_size=4)` | Deterministic, hash-based | `list[float]` |
| `SentenceTransformerProvider(model_name)` | Local model (sentence-transformers) | `list[float]` |

### `src.rag.vector_store`

| Class / Function | Signature | Returns |
|---|---|---|
| `InMemoryVectorStore()` | Local dict-backed store | CRUD + search |
| `.add_entry(entry)` | `(VectorEntry)` | None |
| `.search(query_embedding, top_k, product, gap_type, source_id)` | `(list[float], int, ...)` | `list[VectorEntry]` |
| `VectorEntry` | Dataclass with chunk_id, source_id, title, content, product, gap_types, url, embedding | — |
| `VectorStore` | Abstract base class inherited by `InMemoryVectorStore` and `QdrantStore` | — |

### `src.rag.qdrant_store` (Epic 15)

| Class / Function | Signature | Returns |
|---|---|---|
| `QdrantStore(config)` | `(QdrantConfig\|None)` | Persistent vector store via qdrant-client |
| `.add_entry(entry)` | `(VectorEntry)` | Upserts a Qdrant point with full payload |
| `.search(query_embedding, top_k, product, gap_type, source_id, version, document_type)` | `(list[float], int, ...)` | `list[VectorEntry]` with server-side filtering |
| `QdrantConfig(url, api_key, collection_name, vector_size, timeout)` | Dataclass | Connection and collection settings |
| `build_qdrant_store(url, collection_name, vector_size, api_key, timeout)` | Factory | Returns a `QdrantStore` from explicit params or env defaults |
| `QdrantConnectionError` | Exception | Raised when Qdrant is unreachable |

### `src.rag.semantic_retrieval`

| Function | Signature | Returns |
|---|---|---|
| `semantic_retrieve(query, embedding_model, vector_store, top_k, filters)` | `(RetrievalQuery, EmbeddingProvider, InMemoryVectorStore, int, ...)` | `list[RetrievedContext]` |

### `src.rag.hybrid_retrieval`

| Function | Signature | Returns |
|---|---|---|
| `hybrid_retrieve(query, chunk_index, embedding_model, vector_store, top_k, filters)` | `(RetrievalQuery, ChunkIndex, EmbeddingProvider, InMemoryVectorStore, int, ...)` | `list[RetrievedContext]` (RRF fusion) |

### `src.rag.playbook_retriever`

| Class / Function | Signature | Returns |
|---|---|---|
| `PlaybookRetriever(index)` | `(ChunkIndex)` | Orchestration wrapper |
| `.retrieve_for_gaps(...)` | `(diagnosed_gaps, nvidia_technology_candidates, recommendations, top_k_per_query=3) -> list[PlaybookRetrievalResult]` | One result per gap+tech combination |
| `.retrieve_for_brief(...)` | `(diagnosed_gaps, nvidia_technology_candidates, recommendations) -> list[dict]` | Simplified dicts for Brief template |

### `src.rag.reranking` (Epic 14)

| Function | Signature | Returns |
|---|---|---|
| `rerank_contexts(contexts, query, config)` | `(list[RetrievedContext], RetrievalQuery, RerankingConfig\|None) -> list[RetrievedContext]` | Deterministic composite score (gap/tech boost + provenance penalty + duplicate penalty) |

### `src.rag.context_packing` (Epic 14)

| Function | Signature | Returns |
|---|---|---|
| `pack_contexts(contexts, query, config)` | `(list[RetrievedContext], RetrievalQuery, PackingConfig\|None) -> PackingResult` | Dedup, classify by gap/tech, apply per-gap/per-tech/global limits, compute metrics |
| `build_supporting_contexts(packing_result)` | `(PackingResult) -> list[SupportingNvidiaContext]` | Group PackedContext by (gap, tech) for Action Brief |

### `src.rag.rag_pipeline` (Epic 14.1)

| Function | Signature | Returns |
|---|---|---|
| `run_rag_pipeline(gap_diagnosis, ...)` | `(GapDiagnosisResult, ChunkIndex\|None, EmbeddingProvider\|None, InMemoryVectorStore\|None, RerankingConfig\|None, PackingConfig\|None) -> RagPipelineOutput` | Orchestrates hybrid retrieval → reranking → context packing for the main pipeline |

## Schemas

All defined in `src/rag/schemas.py` using Pydantic v2.

- `RagSource`: metadata for a corpus source (source_id, title, url, product, gap_types)
- `RagDocument`: raw document to chunk (source_id, title, raw_text)
- `RagChunk`: a single chunk with full provenance (chunk_id, source_id, title, content, product, gap_types, url)
- `RetrievalQuery`: query parameters (technology, gap_type, keywords)
- `RetrievedContext`: scored result (chunk_id, source_id, title, content, product, gap_types, url, relevance_score)
- `PlaybookRetrievalResult`: grouped result per gap+tech combination (query, gap_type, technology, contexts, missing_context)
- `RerankingConfig`: reranking weights (boost_gap_match=0.3, boost_technology_match=0.2, penalty_no_provenance=-0.5, penalty_duplicate=-0.3, penalty_irrelevant=-0.2, boost_known_source=0.1)
- `PackedContext`: retrieved context with rerank_score, matched_gap, matched_technology
- `DroppedContext`: chunk_id + reason for dropped contexts
- `PackingConfig`: packing limits (max_total=5, max_per_technology=2, max_per_gap=3)
- `PackingResult`: packed + dropped contexts + metrics (provenance_coverage, gap_coverage, technology_coverage, context_budget_used, noise_reduction_score)
- `SupportingNvidiaContext`: grouped by gap_type + technology for Action Brief consumption
- `RagPipelineOutput`: pipeline-level RAG output with packing_result, retrieval_mode, missing_context, rag_quality_summary

## Invariants

1. Every `RetrievedContext` must carry `source_id` and `url` when available (provenance).
2. `retrieve()` with an empty/unknown query returns `[]` and `missing_context=True`.
3. Action Brief must function normally without RAG context.
4. Relevance score is always `0.0 <= score <= 1.0` (rounded to 2 decimals).
5. No external API calls, no scraping — embeddings use local models (sentence-transformers or mock). No API keys required for development/testing.
6. Semantic retrieval falls back to empty list when vector store is empty.
7. Hybrid retrieval falls back to pure lexical when vector store is empty.
8. Metadata filters (product, gap_type, source_id) are supported in semantic and hybrid retrieval.
9. Reranking is deterministic — no LLM, no external calls. Score is clamped to [0,1].
10. Context packing deduplicates by chunk_id, applies per-gap (max 3), per-tech (max 2), and global (max 5) limits. All limits configurable via `PackingConfig`.
11. Packed contexts carry provenance: `source_id` and `url` are preserved. Dropped contexts record the reason.
12. Action Brief remains optional w.r.t. RAG — `build_action_brief()` accepts `packing_result=None` and works without packed contexts.
13. RAG is integrated as Step 11 in `run_full_pipeline()` — receives `gap_diagnosis`, returns `RagPipelineOutput` with packing_result or missing_context.
14. `run_rag_pipeline()` handles all failure modes gracefully: empty index, no diagnosed gaps, empty retrieval, missing vector_store.
15. QdrantStore is optional — all retrieval functions accept `VectorStore` (ABC) so `InMemoryVectorStore` and `QdrantStore` are interchangeable.
16. QdrantStore connects lazily — `__init__` does not connect to Qdrant.
17. QdrantStore payload preserves provenance: `source_url`, `source_title`, `chunk_id`, `source_id`, `product`, `gap_types`, `version`, `content_hash`, `collected_at`, `document_type`.
18. QdrantStore supports server-side filters: `product`, `gap_type`, `source_id`, `version`, `document_type`.

## Error Handling

- Missing `sources.yaml`: returns empty dict, no crash.
- Missing corpus directory or files: returns empty list, no crash.
- Unknown source_id in `chunk_document`: chunk uses `doc.title` as product, empty `gap_types`.
- Missing source for a chunk during retrieval: `missing_context=True` in `PlaybookRetrievalResult`.
- Empty vector store: `semantic_retrieve()` returns `[]`; `hybrid_retrieve()` falls back to lexical.
- Missing embedding model: `SentenceTransformerProvider` raises `ImportError` if `sentence-transformers` is not installed.

## Dependencies

- **Internal**: `src.rag` (no other internal module depends on RAG)
- **External**: `PyYAML` (already present, 6.0.3); `sentence-transformers` (optional, for real embeddings); `qdrant-client` (already in `pyproject.toml`, optional for Qdrant)

## RAG Evaluation

Added in Epic 12 — offline evaluation of retrieval quality via golden queries.
Extended in Epic 13 — multi-mode comparison (lexical, semantic, hybrid).
Extended in Epic 14 — HYBRID_RERANKED and HYBRID_RERANKED_PACKED modes with 8 new metrics.

- `src/evaluation/rag_eval_schemas.py` — schemas for evaluation (RagEvalCase, RagRetrievalMetrics, RagEvalResult, RagQualityGateResult, **RetrievalMode, ModeEvalResult, RagEvalComparison**)
- `src/evaluation/rag_eval.py` — `run_rag_eval()`, `run_mode_eval()`, `run_comparison_eval()`, `run_quality_gates()`, `format_eval_summary()`, **`format_comparison_summary()`**
- `examples/rag_eval/golden_queries.json` — 16 golden queries covering all gaps + negative cases
- `examples/rag_eval/expected_contexts.json` — expected chunk IDs per query

Evaluation is deterministic when using `MockEmbeddingProvider`. No LLM judge, no external calls.

## Test Coverage

- `tests/unit/test_rag_ingestion.py` — 4 tests
- `tests/unit/test_rag_retrieval.py` — 6 tests
- `tests/unit/test_playbook_retriever.py` — 5 tests
- `tests/unit/test_rag_eval.py` — 20 tests
- `tests/unit/test_rag_embeddings.py` — 11 tests (Epic 13)
- `tests/unit/test_semantic_retrieval.py` — 15 tests (Epic 13)
- `tests/unit/test_hybrid_retrieval.py` — 12 tests (Epic 13)
- `tests/unit/test_rag_eval_semantic.py` — 14 tests (Epic 13)
- `tests/unit/test_rag_reranking.py` — 9 tests (Epic 14)
- `tests/unit/test_context_packing.py` — 13 tests (Epic 14)
- `tests/unit/test_rag_eval_reranking.py` — 11 tests (Epic 14)
- `tests/unit/test_action_brief_rag_context.py` — 5 tests (Epic 14)
- `tests/unit/test_pipeline_rag.py` — 10 tests (Epic 14.1)
- `tests/unit/test_qdrant_store.py` — 20 tests (Epic 15)
- `tests/integration/test_qdrant_rag_pipeline.py` — 9 tests (Epic 15, skippable)
- `tests/unit/test_ingest_nvidia_corpus.py` — 17 tests (Epic 18)
- `tests/integration/test_qdrant_corpus_ingestion.py` — 3 tests (Epic 18, skippable)

## Ingestion Script (Epic 18)

`scripts/ingest_nvidia_corpus.py` — automated pipeline for populating Qdrant from the
local corpus at `data/nvidia_corpus/`. See `docs/42_automated_qdrant_corpus_ingestion.md`
for full documentation.

### Integration contract
1. `RagSource` now carries `version` and `document_type` (defaults: "1.0", "nvidia_corpus")
2. `RagChunk` now carries `version`, `document_type`, `content_hash` (backward-compatible)
3. `VectorEntry` now carries `version`, `document_type`, `content_hash`, `chunk_hash`, `ingestion_run_id` (backward-compatible, all optional with defaults)
4. `_entry_to_point` uses `entry.version`/`entry.document_type` if set, falls back to defaults
5. `_point_to_entry` restores all new fields from Qdrant payload
6. `QdrantStore._ensure_collection()` now also calls `_ensure_payload_indexes()` which creates keyword indexes for: product, gap_types, source_id, version, document_type, content_hash
7. The ingestion script never makes external calls, never scrapes, never downloads
