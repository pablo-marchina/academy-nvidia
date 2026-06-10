# Plan — Epic 15: Persistent Vector Store with Qdrant

**Date:** 2026-06-10
**Status:** Approved, implemented

## Objective
Add optional Qdrant-backed persistent vector store while preserving existing in-memory fallback and all quality gates.

## Scope
- `src/rag/qdrant_store.py` — Qdrant adapter (QdrantStore, QdrantConfig, QdrantConnectionError, build_qdrant_store)
- `src/rag/vector_store.py` — extracted VectorStore ABC, InMemoryVectorStore inherits from it
- `src/rag/semantic_retrieval.py`, `hybrid_retrieval.py`, `rag_pipeline.py` — type hints changed to VectorStore
- `src/evaluation/rag_eval.py` — type hints changed to VectorStore
- `tests/unit/test_qdrant_store.py` — 20 unit tests with mocked qdrant-client
- `tests/integration/test_qdrant_rag_pipeline.py` — 9 skippable integration tests
- `.env.example` — +RAG_VECTOR_BACKEND, QDRANT_COLLECTION, QDRANT_VECTOR_SIZE
- `docker-compose.yml` — +healthcheck on qdrant service
- `docs/39_qdrant_persistent_vector_store.md`
- `docs/contracts/rag_contract.md` — +QdrantStore API + payload schema
- `EVALS.md`, `README.md`, `ROADMAP.md`, `DECISIONS.md` — updated
- Obsidian vault — backfill

## Out of scope
No scraping, crawler, scheduler, LangGraph, interface, scoring, diagnosis, recommendation changes.

## Key decisions
- VectorStore ABC extracted from InMemoryVectorStore (backward compatible)
- QdrantStore lazy-connects on first operation (not in __init__)
- Payload includes version, content_hash, collected_at, document_type, provenance
- Unit tests mock qdrant_client.QdrantClient (no server needed)
- Integration tests skip when QDRANT_TEST_URL is not set
- Filter params extended to include version and document_type

## Validation
- pytest: 306 passed, 9 skipped
- ruff: all checks passed
- black: all files left unchanged
- mypy: Success: no issues found
