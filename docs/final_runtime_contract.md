# Final Runtime Contract

## Product Mode Requirements

`APP_MODE=product` requires real configuration and explicit failures:

- PostgreSQL via `PRODUCT_DB_URL`
- Qdrant via `QDRANT_URL` and `QDRANT_COLLECTION`
- Real embeddings via `RAG_EMBEDDING_MODEL`
- `RAG_VECTOR_BACKEND=qdrant`
- `RAG_REQUIRED_FOR_PRODUCT=true`
- LangGraph orchestration enabled and available for the final workflow path
- No demo data, mock data, fake API, in-memory vector store, or silent fallback

Tests and local research may use fixtures, mock embeddings, SQLite, and local
substitutes only when the mode and path are explicit. They cannot satisfy final
runtime readiness.

## Required Runtime Evidence

Runtime components must appear in:

- `final_case_evidence/runtime_bill_of_materials.csv`
- `final_case_evidence/decision_ledger.csv`
- `final_case_evidence/benchmark_manifest.json`
- `final_case_evidence/repository_purpose_manifest.csv`

Any productive score, threshold, weight, limit, or gate must have calibration
metadata or an explicit `TBD_BY_*` placeholder that blocks production promotion.
