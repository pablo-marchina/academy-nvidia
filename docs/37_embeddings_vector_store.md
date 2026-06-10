# Embeddings + Vector Store Retrieval

**Epic 13** | **Date**: 2026-06-09

## Objective

Evolve the Product RAG from lexical-only to **hybrid (lexical + semantic)** retrieval with fallback. Add embedding support, in-memory vector store, and multi-mode RAG evaluation.

## Architecture

```
src/rag/
├── embeddings.py           # EmbeddingProvider (abstract), MockEmbeddingProvider, SentenceTransformerProvider
├── vector_store.py         # InMemoryVectorStore with cosine similarity + metadata filters
├── semantic_retrieval.py   # semantic_retrieve() — embed query → vector search → contexts
├── hybrid_retrieval.py     # hybrid_retrieve() — RRF fusion of lexical + semantic results
├── schemas.py              # (unchanged — no new schemas needed)
├── retrieval.py            # (unchanged — ChunkIndex remains lexical fallback)
└── playbook_retriever.py   # (unchanged — Action Brief works without vector store)

src/evaluation/
├── rag_eval_schemas.py     # + RetrievalMode enum, ModeEvalResult, RagEvalComparison
└── rag_eval.py             # + run_mode_eval(), run_comparison_eval(), format_comparison_summary()
```

## Embedding Provider

Abstract base class with two implementations:

| Provider | Use case | Dependencies | Vector size |
|---|---|---|---|
| `MockEmbeddingProvider` | Tests / CI | None (pure Python) | Configurable (default 4) |
| `SentenceTransformerProvider` | Local development | `sentence-transformers` | 384 (all-MiniLM-L6-v2) |

The mock provider generates deterministic pseudo-embeddings using MD5 hash + sin/cos. Similar texts produce related vectors. No external calls, no model download.

## Vector Store

`InMemoryVectorStore` — local dict-backed store with:

- **Cosine similarity** search (pure Python, no external deps)
- **Metadata filters**: `product`, `gap_type`, `source_id`
- **CRUD**: `add_entry`, `add_entries`, `remove_entry`, `clear`, `get_entry`
- **Zero config**: no server, no Docker, no API keys

Designed as a drop-in that can be replaced by Qdrant in production (the `qdrant-client` package is already in `pyproject.toml`).

## Semantic Retrieval

1. Build query text from `RetrievalQuery` (gap_type → "high inference cost", technology, keywords)
2. Embed query text using `EmbeddingProvider`
3. Search vector store (with optional filters)
4. Return `RetrievedContext` list with provenance and relevance score

## Hybrid Retrieval

Fuses lexical (`ChunkIndex`) and semantic (`VectorStore`) results using **Reciprocal Rank Fusion (RRF)**:

```
RRF_score(chunk) = Σ 1/(k + rank_i)   for each list i where chunk appears
```

- `k = 60` (standard RRF constant)
- Deduplicates chunks appearing in both lists
- Falls back to pure lexical when vector store is empty
- Filters applied to semantic branch; lexical branch respects its own query logic

## Multi-Mode Evaluation

`run_comparison_eval()` runs golden queries through all three modes:

| Mode | Retrieval used | Empty vector store behavior |
|---|---|---|
| `LEXICAL` | `ChunkIndex.retrieve()` | Normal (no vector store needed) |
| `SEMANTIC` | `semantic_retrieve()` | Returns empty results |
| `HYBRID` | `hybrid_retrieve()` | Falls back to lexical |

**Regression detection**: flags any critical golden query that passes in lexical mode but fails in semantic or hybrid mode.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| In-memory vector store | No external dependencies for dev/test; Qdrant-ready for production |
| Mock embedding provider | Tests are deterministic, no model downloads, no API keys |
| RRF for hybrid fusion | Simple, robust, no parameter tuning |
| Filters applied before scoring | Consistent with lexical filtering semantics |
| Lexical remains unchanged | Zero risk to existing pipeline, brief, and evals |
| No schema changes to RagChunk | Embeddings stored in vector store, not in Pydantic models |

## Files Created

| File | Purpose |
|---|---|
| `src/rag/embeddings.py` | Embedding provider abstraction + implementations |
| `src/rag/vector_store.py` | In-memory vector store |
| `src/rag/semantic_retrieval.py` | Semantic retrieval function |
| `src/rag/hybrid_retrieval.py` | Hybrid retrieval with RRF fusion |
| `tests/unit/test_rag_embeddings.py` | 11 tests for embedding providers |
| `tests/unit/test_semantic_retrieval.py` | 15 tests for semantic retrieval |
| `tests/unit/test_hybrid_retrieval.py` | 14 tests for hybrid retrieval |
| `tests/unit/test_rag_eval_semantic.py` | 14 tests for multi-mode evaluation |

## Limitations

- `SentenceTransformerProvider` requires `sentence-transformers` package (not in dev deps by default)
- Mock embedding provider does not capture real semantic relationships
- Vector store is in-memory only (no persistence across sessions)
- No cross-encoder reranking (deferred to future epic)
- Corpus is still manually curated (no automated crawling)
