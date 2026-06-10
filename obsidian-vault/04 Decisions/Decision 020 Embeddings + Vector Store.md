# Decision 020 — Embeddings + Vector Store Retrieval

**Epic:** 13
**Date:** 2026-06-09

## Context
Product RAG (Epic 11) used only lexical retrieval. Semantic matching required embeddings and vector store without adding setup complexity (no Qdrant server, Docker, or API keys).

## Decision
- Create `EmbeddingProvider` abstract class with `MockEmbeddingProvider` (deterministic, hash-based) for tests and `SentenceTransformerProvider` (`all-MiniLM-L6-v2`) for production.
- `InMemoryVectorStore` with pure-Python cosine similarity and metadata filters.
- Hybrid retrieval via RRF (Reciprocal Rank Fusion).
- Multi-mode RAG evaluation (lexical vs semantic vs hybrid) with regression detection.

## Alternatives
- Qdrant server-side (requires Docker/setup)
- Chroma/FAISS (extra dependency)
- Cross-encoder reranking (too heavy for MVP)
- API-based embeddings (requires API key)

## Status
Implemented in Epic 13.
