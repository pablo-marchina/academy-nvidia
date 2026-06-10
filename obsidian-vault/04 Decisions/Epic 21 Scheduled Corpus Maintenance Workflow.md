# Epic 21 Scheduled Corpus Maintenance Workflow

**Decision:** Corpus maintenance automation must be safe by default and require
explicit manual input before mutating Qdrant or promoting sources.

## Context

The project already had source sync, freshness audit, Qdrant ingestion, RAG evals,
and golden evals, but they were separate manual commands. That made maintenance
harder to repeat and increased the risk of missing a quality gate.

## Decision

Create a local orchestrator and GitHub Actions workflow with safe defaults:

- `run_sync=true`
- `run_ingestion=false`
- `run_evals=true`
- `promote_sources=false`
- `recreate_collection=false`
- `fail_on_stale=false`
- `fail_on_expired=true`

Scheduled runs must never promote sources or run real ingestion.

## Consequences

- Corpus checks become repeatable and artifact-backed.
- Real Qdrant mutation still requires an explicit operator choice.
- Human review remains required before promoted corpus changes are committed.
- No crawler, retrieval, embedding, scoring, diagnosis, recommendation, briefing,
  or motion logic changes were introduced.
