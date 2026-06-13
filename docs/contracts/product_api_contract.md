# Product API Contract

**Module:** `src/api/product_routes.py`
**Version:** 2.1
**Date:** 2026-06-12

## Purpose

Expose persisted product resources without using demo artifacts as state. All
product operations use the transactional database configured by
`PRODUCT_DB_URL`.

## Resource Contracts

### Startup

`StartupCreate` requires `name`, `website`, and `sector`. It accepts profile
text, tags, and initial public evidence. Names are normalized by case-folding
and whitespace collapse; normalized names are unique.

`StartupUpdate` accepts optional fields: `name`, `website`, `country`,
`sector`, `description`, `product_summary`, `status`, `tags`. If `name` is
changed, `normalized_name` is recalculated. Evidence is not altered by PATCH.
Returns updated `StartupRead`.

`StartupRead` returns the persisted profile and evidence records. Evidence
preserves source URL, source type, confidence, evidence kind, quote, and
collection timestamp.

### AnalysisRun

`AnalysisRunCreate` accepts `use_rag`, `rag_backend`, `pipeline_version`, and an
optional `corpus_version`.

`AnalysisRunRead` returns lifecycle timestamps, error/degraded state, snapshots,
scores, gaps, NVIDIA mappings, readiness checks, and latest Action Brief ID.

Lifecycle values implemented in this build are `queued`, `running`,
`completed`, `degraded`, and `failed`. `reviewed` and `exported` are reserved
for later workflows.

### ActionBrief

`ActionBriefRead` returns a versioned persisted record containing both validated
JSON and rendered Markdown. Only one record per run is marked `is_latest`.

### ReviewDecision

`ReviewDecisionCreate` requires `decision` (one of: `approve`, `reject`,
`needs_more_evidence`, `monitor`, `contact`, `not_recommended`), `reviewer`,
optional `notes`, and optional `metadata`.

`ReviewDecisionRead` returns the review record with id, analysis_run_id,
decision, reviewer, notes, metadata, created_at, updated_at.

Reviews are append-only: multiple reviews can exist for a run. The latest
review (by created_at) is the current status. Reviews do not recalculate scores.

### Activation Dossier

`ActivationDossierRead` returns the complete dossier JSON for an analysis run,
including scores, gaps, NVIDIA mappings, activation recommendations, claims,
review decisions, readiness checks, uncertainties, and risks.

`ActivationDossierSummaryRead` is a lightweight projection containing
`created_at`, `version`, `risk_count`, and `unsupported_claim_count`.

Dossier generation is idempotent by default (returns existing latest dossier).
Use `?force=true` to regenerate with a new version. Dossiers are versioned
per analysis run (1, 2, 3…) and previous versions are preserved.

### Export

`ExportCreate` requires `export_type` (`json` or `markdown`).

`ExportRead` returns the export record metadata including id,
analysis_run_id, action_brief_id, dossier_id, export_type, status, storage_path,
content_hash, error_message, and timestamps. Status values: pending,
completed, failed. Content is generated from the persisted ActionBriefRecord,
not from demo artifacts.

### Opportunity

`OpportunityListItem` represents a startup's latest analysis run with key
scoring, gap, review, and dossier information for ranking.

`OpportunityListResponse` wraps items with total, offset, and limit pagination
metadata.

## Endpoints

| Method | Path | Success | Errors |
|---|---|---|---|---|
| POST | `/startups` | `201 StartupRead` | `409` duplicate name, `422` validation |
| GET | `/startups` | `200 list[StartupListItem]` | `422` invalid pagination |
| GET | `/startups/{id}` | `200 StartupRead` | `404` unknown startup |
| PATCH | `/startups/{id}` | `200 StartupRead` | `404`, `409` duplicate name, `422` |
| POST | `/startups/{id}/analysis-runs` | `201 AnalysisRunRead` | `404`, `422` |
| GET | `/analysis-runs/{id}` | `200 AnalysisRunRead` | `404` unknown run |
| GET | `/analysis-runs/{id}/brief` | `200 ActionBriefRead` | `404` |
| POST | `/analysis-runs/{id}/dossier` | `201 ActivationDossierRead` | `404`, `409` draft run |
| GET | `/analysis-runs/{id}/dossier` | `200 ActivationDossierRead` | `404` |
| GET | `/analysis-runs/{id}/dossier/markdown` | `200 ActivationDossierMarkdownRead` | `404` |
| POST | `/analysis-runs/{id}/review` | `201 ReviewDecisionRead` | `404`, `422` |
| GET | `/analysis-runs/{id}/reviews` | `200 list[ReviewDecisionRead]` | `404` |
| POST | `/analysis-runs/{id}/exports` | `201 ExportRead` | `404`, `422` |
| GET | `/opportunities` | `200 OpportunityListResponse` | `422` |
| GET | `/exports/{id}` | `200 ExportRead` | `404` |
| GET | `/health/product` | `200 ProductHealthRead` | controlled degraded response |
| GET | `/health/dependencies` | `200 DependencyHealthRead` | controlled status response |

Pipeline failures are persisted and returned as an `AnalysisRunRead` with
`status=failed` and `error_message`; they do not return demo fixtures.

## Health Contract

`GET /health/product` reports database connectivity, required table
availability, `APP_MODE`, `ENABLE_PRODUCT_PERSISTENCE`, and a sanitized database
URL.

`GET /health/dependencies` reports product DB, Qdrant, and RAG corpus as
separate dependencies with `configured`, `available`, `required`, `status`, and
detail fields.

## Persistence Invariants

1. Product routes never read `data/demo_runs`.
2. Qdrant is not used for transactional product records.
3. Every completed or degraded run has a persisted output snapshot.
4. Every pipeline exception produces a persisted failed run.
5. NVIDIA mappings remain traceable to an analysis run and diagnosed gap.
6. Action Brief JSON and Markdown are persisted together with a version.
7. Database URLs returned to clients do not expose passwords.

## Deferred Contract Surface

- authentication and role enforcement
- asynchronous run submission
- PDF export generation
