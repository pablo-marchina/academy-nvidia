# Epic 51: Full Local Product Proof PASS

## Summary

Turn `prove-final-product --full` from an environment-blocked proof into a full local product proof that can pass when Docker, PostgreSQL, Qdrant, real RAG ingestion, and product-like acceptance are available.

## Key Changes

- Auto-start local PostgreSQL and Qdrant with `docker compose up -d postgres qdrant` during full proof.
- Preserve local volumes and collections by default; destructive reset is only available through an explicit flag.
- Wait for PostgreSQL and Qdrant readiness before running migrations, ingestion, and acceptance.
- Run Alembic against PostgreSQL and verify current/head migration state plus a minimal SQL roundtrip.
- Ingest the local NVIDIA corpus into Qdrant with real 384-dimensional embeddings, skip existing chunks by default, and validate sample retrieval.
- Replace product-like acceptance based on pytest monkeypatches with a product-env acceptance script that exercises the real API path.
- Keep honest fallback semantics: blocked Docker, missing embeddings, unavailable services, or blocked ports produce `BLOCKED_BY_ENVIRONMENT`, not `PASS`.

## Public Interfaces

- `make prove-final-product` remains the main command.
- `make local-services-up` starts local PostgreSQL and Qdrant for inspection and reuse.
- `scripts/real_service_proof.py` gains `--auto-start-services`, `--no-auto-start-services`, `--ingest-corpus`, `--wait-timeout-seconds`, and `--reset-qdrant`.
- `scripts/ingest_nvidia_corpus.py` gains explicit Qdrant URL/API key, embedding model, vector size, skip-existing, and report path options.

## Test Plan

- Unit tests cover Docker blocked/start behavior, wait loops, reset safety, status aggregation, ingestion CLI defaults, and acceptance report shape.
- Focused validation runs the final gate scripts, benchmark runner, real-service proof tests, ingestion tests, lint, formatting, and mypy.
- Full proof is run locally; current environment may still report `BLOCKED_BY_ENVIRONMENT` if Docker/Qdrant/Postgres are unavailable.

## Assumptions

- Containers are left running by default.
- Local data is preserved by default.
- No secrets are committed.
- Runtime promotion remains limited to candidates with benchmark/proof evidence.
