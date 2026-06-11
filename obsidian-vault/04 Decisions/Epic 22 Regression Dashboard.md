# Epic 22 Regression Dashboard

**Decision:** Consolidate corpus maintenance quality into a local Markdown/JSON
dashboard and use it as the GitHub Actions summary/gate.

## Context

Epic 21 created scheduled corpus maintenance and artifact reports, but there was
no single view for comparing ingestion, freshness, RAG evals, golden evals, and
Action Brief checks across runs.

## Decision

Create `scripts/build_regression_dashboard.py` as a read-only report consolidator.
The script emits `data/regression_reports/latest_dashboard.md` and
`latest_dashboard.json`. GitHub Actions publishes the Markdown to Job Summary,
uploads both files as artifacts, and fails only when the consolidated status is
`FAIL`.

## Consequences

- Operators get one local and CI-visible regression view.
- WARN conditions remain visible but do not block scheduled maintenance.
- FAIL conditions block the workflow after summary/artifact publication.
- No product logic is changed.

## Non-goals

- No frontend.
- No external publication.
- No new retrieval, scoring, diagnosis, recommendation, Qdrant ingestion, or
  Action Brief logic.
