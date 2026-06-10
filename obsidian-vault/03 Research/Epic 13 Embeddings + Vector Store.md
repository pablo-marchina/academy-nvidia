# Epic 13 — Embeddings + Vector Store Retrieval

**Date:** 2026-06-09
**Status:** Concluído

## Summary
Evoluiu o Product RAG de lexical-only para híbrido (lexical + semântico) com fallback. Adicionou suporte a embeddings, vector store in-memory, e avaliação multi-modo.

## Created
- `src/rag/embeddings.py` — EmbeddingProvider abstrato, MockEmbeddingProvider (testes), SentenceTransformerProvider (produção)
- `src/rag/vector_store.py` — InMemoryVectorStore com cosine similarity e filtros por product/gap_type/source_id
- `src/rag/semantic_retrieval.py` — semantic_retrieve() com query embedding + vector search
- `src/rag/hybrid_retrieval.py` — hybrid_retrieve() com RRF fusion e fallback lexical
- 52 novos testes (11 embeddings, 15 semantic, 12 hybrid, 14 multi-mode eval)

## Key Decisions
- Vector store in-memory (sem dependências externas para testes)
- Mock embeddings determinísticos (hash-based, sem download de modelo)
- RRF para fusão híbrida (simples, robusta, sem calibração)
- Avaliação compara 3 modos (lexical, semantic, hybrid) e detecta regressões

## Dependencies
- `qdrant-client` já instalado (não usado — preparado para produção)
- `sentence-transformers` (opcional, para embeddings reais)

## Test Results
236 testes totais (188 anteriores + 48 novos), todos passando.
