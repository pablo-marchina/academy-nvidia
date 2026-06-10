# RAG Module Contract

**Module**: `src/rag/`
**Last updated**: 2026-06-09
**Epic**: 11 — Product RAG / Playbook Retrieval; 13 — Embeddings + Vector Store Retrieval

## Scope

Provide deterministic lexical retrieval and **optional semantic/hybrid retrieval** of NVIDIA documentation snippets to enrich Startup Action Briefs. The module defines ingestion (Markdown → chunks), indexing (in-memory by gap_type and product), lexical retrieval (scoring), **semantic retrieval (embedding + vector store)**, hybrid retrieval (RRF fusion), and playbook orchestration.

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

## Schemas

All defined in `src/rag/schemas.py` using Pydantic v2.

- `RagSource`: metadata for a corpus source (source_id, title, url, product, gap_types)
- `RagDocument`: raw document to chunk (source_id, title, raw_text)
- `RagChunk`: a single chunk with full provenance (chunk_id, source_id, title, content, product, gap_types, url)
- `RetrievalQuery`: query parameters (technology, gap_type, keywords)
- `RetrievedContext`: scored result (chunk_id, source_id, title, content, product, gap_types, url, relevance_score)
- `PlaybookRetrievalResult`: grouped result per gap+tech combination (query, gap_type, technology, contexts, missing_context)

## Invariants

1. Every `RetrievedContext` must carry `source_id` and `url` when available (provenance).
2. `retrieve()` with an empty/unknown query returns `[]` and `missing_context=True`.
3. Action Brief must function normally without RAG context.
4. Relevance score is always `0.0 <= score <= 1.0` (rounded to 2 decimals).
5. No external API calls, no scraping — embeddings use local models (sentence-transformers or mock). No API keys required for development/testing.
6. Semantic retrieval falls back to empty list when vector store is empty.
7. Hybrid retrieval falls back to pure lexical when vector store is empty.
8. Metadata filters (product, gap_type, source_id) are supported in semantic and hybrid retrieval.

## Error Handling

- Missing `sources.yaml`: returns empty dict, no crash.
- Missing corpus directory or files: returns empty list, no crash.
- Unknown source_id in `chunk_document`: chunk uses `doc.title` as product, empty `gap_types`.
- Missing source for a chunk during retrieval: `missing_context=True` in `PlaybookRetrievalResult`.
- Empty vector store: `semantic_retrieve()` returns `[]`; `hybrid_retrieve()` falls back to lexical.
- Missing embedding model: `SentenceTransformerProvider` raises `ImportError` if `sentence-transformers` is not installed.

## Dependencies

- **Internal**: `src.rag` (no other internal module depends on RAG)
- **External**: `PyYAML` (already present, 6.0.3); `sentence-transformers` (optional, for real embeddings)

## RAG Evaluation

Added in Epic 12 — offline evaluation of retrieval quality via golden queries.
Extended in Epic 13 — multi-mode comparison (lexical, semantic, hybrid).

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
