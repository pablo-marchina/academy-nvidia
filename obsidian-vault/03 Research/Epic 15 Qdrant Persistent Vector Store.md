# Epic 15 — Persistent Vector Store with Qdrant

**Date:** 2026-06-10
**Status:** Concluído

## Summary
Adicionou suporte opcional a Qdrant local como vector store persistente, mantendo fallback in-memory e lexical. Extraiu interface `VectorStore(ABC)` de `InMemoryVectorStore`, criou `QdrantStore(VectorStore)` com lazy connection, payload rico (11 campos com provenance), e filtros server-side. Todas as funções de retrieval agora aceitam `VectorStore` (polimórficas). Qdrant é opcional — RAG continua funcionando sem ele.

## Created
- `src/rag/qdrant_store.py` — QdrantStore, QdrantConfig, QdrantConnectionError, build_qdrant_store
- VectorStore ABC em `src/rag/vector_store.py`
- `tests/unit/test_qdrant_store.py` — 20 testes (mock, sem Qdrant)
- `tests/integration/test_qdrant_rag_pipeline.py` — 9 testes (skippable)
- `docs/39_qdrant_persistent_vector_store.md`

## Key Decisions
- Adapter pattern: VectorStore(ABC) + InMemoryVectorStore + QdrantStore
- Lazy connection: Qdrant não é conectado em __init__
- Payload: chunk_id, source_id, source_title, source_url, product, gap_types, version, content_hash, collected_at, document_type, provenance
- Filtros server-side: product, gap_type, source_id, version, document_type
- Unit tests mockam qdrant_client.QdrantClient

## Test Results
20 unit tests + 9 integration (skippable). 315 testes totais (306 pass, 9 skip).
