> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Declare RAG Optional Extra for Reproducible Qdrant 384 Ingestion

**Date:** 2026-06-10
**Status:** Approved for implementation
**Scope:** Short task under Epic 18 follow-up

## Objective

Declare `sentence-transformers` as an optional RAG dependency so clean
environments can install real local embedding support with:

```bash
pip install -e ".[rag]"
```

## Implementation

- Add a `rag` optional dependency extra in `pyproject.toml`.
- Keep `sentence-transformers` out of the core install because it is specific to
  embeddings/RAG.
- Document when to use the extra and how it relates to Qdrant ingestion.
- Add `RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2` and keep
  `QDRANT_VECTOR_SIZE=384` in `.env.example`.
- Improve the missing dependency error in `SentenceTransformerProvider` so it
  suggests `pip install -e ".[rag]"`.
- Add a unit test that simulates missing `sentence-transformers` without loading
  or downloading any model.

## Out of Scope

- No corpus reingestion.
- No Qdrant collection mutation.
- No model change.
- No retrieval, pipeline, scoring, diagnosis, recommendation, or Action Brief
  behavior changes.
- No external calls or model downloads in tests.

## Validation

- `git status`
- `git diff --stat`
- `pytest`
- `ruff check .`
- `black --check .`
- `mypy src`

