# Product Backend Foundation

**Epic:** 29
**Date:** 2026-06-11
**Status:** Implemented

## Objective

Provide the minimum transactional backend needed to operate NVIDIA Startup AI
Radar as a persistent product. The foundation stores startups, evidence,
analysis runs, structured pipeline outputs, versioned Action Briefs, and
explicit readiness/degraded states without changing scoring, diagnosis,
recommendation, RAG retrieval, or Qdrant ingestion.

## Architecture

```text
FastAPI product routes
        |
ProductService
        |
ProductRepository ---- SQLAlchemy ---- SQLite (default)
        |
Existing pipeline -> briefing
        |
Optional Product RAG ---------------- Qdrant
```

`src/database/` is the canonical transactional database package.
`src/repositories/` owns persistence operations. `src/services/product/`
adapts persisted records to the existing Pydantic pipeline contracts.

## Database Decision

The initial product database is SQLite:

```text
sqlite:///data/product/product.db
```

SQLite is sufficient for local product delivery, requires no extra service, and
supports isolated integration tests. SQLAlchemy models use portable column
types and relational constraints so `PRODUCT_DB_URL` can later point to
PostgreSQL without changing service or repository interfaces.

The existing `DATABASE_URL` remains a legacy/scaffold variable. Product code
uses `PRODUCT_DB_URL`.

## Transactional Entities

| Entity | Responsibility |
|---|---|
| Startup | Product identity and current profile |
| StartupEvidence | Traceable public evidence attached to a startup |
| AnalysisRun | Persisted lifecycle and pipeline snapshots |
| ScoreRecord | Defensibility, fit, readiness, and composite scores |
| GapDiagnosisRecord | Per-gap detection, confidence, evidence, and reasoning |
| NvidiaMappingRecord | Gap-to-technology mapping and recommendation projection |
| ActionBriefRecord | Versioned JSON and Markdown Action Brief |
| ProductReadinessCheck | Explicit dependency, quality, and degraded state |

`ReviewDecision` and `ExportRecord` remain P1 follow-up entities. Authentication,
roles, CRM, professional PDF export, and external job queues are not part of
this foundation.

## Constraints

- `Startup.normalized_name` is unique.
- Score is unique per `analysis_run_id + score_type`.
- Gap diagnosis is unique per `analysis_run_id + gap_type`.
- Action Brief is unique per `analysis_run_id + version`.
- Startup, run, status, and creation-time fields have operational indexes.

## AnalysisRun Lifecycle

```text
queued -> running -> completed
                  -> degraded
                  -> failed
```

The first implementation is synchronous, but it persists `queued` and
`running` before invoking the pipeline. A usable result with material missing
evidence or unavailable optional RAG dependencies ends as `degraded`. An
exception ends as `failed` with `error_message`; it does not return a sample or
demo fallback.

The run stores input/output snapshots, pipeline version, corpus version,
configuration snapshot, start/completion timestamps, error detail, and
degraded reason.

## Pipeline Boundary

The product service:

1. Loads Startup and StartupEvidence from SQLite.
2. Builds the existing `StartupProfile` and `Evidence` schemas.
3. Calls `run_full_pipeline()` unchanged.
4. Persists validated evidence, scores, gaps, mappings, and output snapshot.
5. Calls the existing Action Brief builder and persists JSON and Markdown.
6. Records readiness checks and final lifecycle status.

The product path does not read `data/demo_runs`. Demo endpoints and artifacts
remain available only for temporary compatibility.

## SQLite And Qdrant Boundary

SQLite stores transactional product records and references to retrieval
outputs. Qdrant continues to store embeddings, chunks, corpus documents, and
retrieval metadata. Embeddings and Qdrant payloads are not copied into SQLite.

Qdrant is optional by default. When requested but unavailable, the run records
`QDRANT_UNAVAILABLE` and is degraded. If `RAG_REQUIRED_FOR_PRODUCT=true`, the
run fails instead of silently continuing as if all dependencies were healthy.

## Degraded States

The product catalog defines:

- `QDRANT_UNAVAILABLE`
- `RAG_UNAVAILABLE`
- `CORPUS_STALE`
- `MISSING_EVIDENCE`
- `SCORE_INCOMPLETE`
- `EVAL_FAILED`
- `PRODUCT_DB_UNAVAILABLE`

Each definition includes severity, user-facing message, internal detail,
recommended action, and metadata. The current run integration actively emits
Qdrant, RAG, and missing-evidence checks. Corpus freshness, eval failure, and
score completeness are ready for later quality-gate wiring.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PRODUCT_DB_URL` | `sqlite:///data/product/product.db` | SQLAlchemy product database URL |
| `PRODUCT_DATA_DIR` | `data/product` | Product-local data directory |
| `APP_MODE` | `product` | Runtime mode exposed by product health |
| `ENABLE_PRODUCT_PERSISTENCE` | `true` | Enables product persistence |
| `RAG_REQUIRED_FOR_PRODUCT` | `false` | Makes RAG dependency failure blocking |
| `QDRANT_URL` | `http://localhost:6333` | Optional vector/RAG service |

Database URLs returned by health endpoints are sanitized.

## Product API

Implemented endpoints:

- `POST /startups`
- `GET /startups`
- `GET /startups/{id}`
- `POST /startups/{id}/analysis-runs`
- `GET /analysis-runs/{id}`
- `GET /analysis-runs/{id}/brief`
- `GET /health/product`
- `GET /health/dependencies`

Deferred endpoints:

- `PATCH /startups/{id}`
- `POST /analysis-runs/{id}/review`
- `GET /opportunities`
- `GET /exports/{id}`

See `docs/contracts/product_api_contract.md` for request, response, lifecycle,
and error guarantees.

## Known Limitations

- Analysis execution is synchronous; no external queue or worker exists.
- Schema creation uses `create_all`; versioned migrations are deferred.
- Product routes have no authentication or authorization.
- Review, opportunities, and export records are deferred.
- Qdrant health checks connectivity, not collection freshness or vector parity.
- Corpus stale, eval failed, and score incomplete definitions are not yet wired
  to automatic runtime checks.
- Existing demo endpoints remain registered for compatibility.
