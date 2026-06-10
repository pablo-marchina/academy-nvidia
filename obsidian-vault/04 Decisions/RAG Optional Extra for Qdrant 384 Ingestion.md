# RAG Optional Extra for Qdrant 384 Ingestion

**Date:** 2026-06-10

## Decision

Declare `sentence-transformers` in the optional `rag` extra instead of the core
project dependencies.

## Rationale

- Real RAG embeddings are specific to semantic retrieval and Qdrant ingestion.
- The core pipeline should remain installable without heavy embedding runtime
  dependencies.
- The default model, `sentence-transformers/all-MiniLM-L6-v2`, produces
  384-dimensional vectors.
- Qdrant collections ingested with that model must use `QDRANT_VECTOR_SIZE=384`.

## Validation

Clean RAG environments should install with:

```bash
pip install -e ".[rag]"
```

Tests must continue to avoid model downloads by using mock embeddings or by
simulating missing dependencies.
