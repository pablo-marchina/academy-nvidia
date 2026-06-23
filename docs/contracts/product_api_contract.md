# Product API Contract

**Module:** `src/api/product_routes.py`
**Version:** 2.2
**Date:** 2026-06-13

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

### Analysis Evidence Bundle

`AnalysisEvidenceBundleRead` is the evidence-first read model for an analysis
run. It aggregates persisted claims, evidence coverage, activation
recommendations, latest dossier, readiness/degraded checks, missing evidence,
contradictions, RAG support status, trust/freshness metadata, lineage, and
non-promoted activation alternatives in one response.

The bundle never recalculates scoring, retrieval, LLM output, recommendations,
or dossier content. Missing RAG/Qdrant support, weak claims, unsupported claims,
and absent dossier/recommendations are exposed explicitly instead of being
treated as success.

### ActionBrief

`PersistedActionBriefRead` returned by `GET /analysis-runs/{id}/brief` is the
canonical product-consumer read model for the user-facing Action Brief. It
serializes the already persisted quantitative `ActionBriefRecord.brief_json`
together with `AnalysisRun.output_snapshot_json["brief_metrics"]`; it must not
recalculate brief generation, ranking, RAG, scoring, scraping, LLM output, or
recommendations.

The canonical brief response preserves: `run_id`, `startup_id`, `generated_at`,
`brief_status`, `executive_summary_quantitative`, `recommendation_summary`,
`top_recommendations`, `evidence_summary`, `rag_summary`, `gap_summary`,
`scoring_summary`, `risk_summary`, `blockers`, `next_best_actions`,
`audit_trail`, `quality_gate_snapshot`, `calibration_snapshot`, `brief_metrics`,
and `schema_version`. Blocked briefs are returned as persisted, including
blockers and audit trail. Missing briefs return `404`.

`ActionBriefRead` may still appear embedded in run detail responses as the
versioned persistence envelope containing validated JSON and rendered Markdown.
It is not the canonical consumer payload for the user-facing Action Brief.

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

`GET /analysis-runs/{id}/brief/export/json` returns the canonical persisted
Action Brief wrapped with `export_metadata` (`export_id`, `run_id`,
`exported_at`, `export_format=json`,
`source=persisted_analysis_run_action_brief`, `schema_version`). The export
does not include tracebacks, secrets, environment variables, tokens, rendered
Markdown, or internal fields outside the canonical brief schema.

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
| GET | `/analysis-runs/{id}/evidence-bundle` | `200 AnalysisEvidenceBundleRead` | `404` unknown run |
| GET | `/analysis-runs/{id}/brief` | `200 PersistedActionBriefRead` | `404` |
| GET | `/analysis-runs/{id}/brief/export/json` | `200 ActionBriefJsonExportRead` | `404` |
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

### Product Capability & Configuration (Epic 36.1)

`ProductCapabilityRead` exposes each registered capability with `capability_id`,
`name`, `description`, `category`, `required`, `status`, `status_reason`,
`required_env_vars`, `optional_env_vars`, `required_extras`, `required_services`,
`setup_instructions`, `failure_mode`, `user_visible`, `documentation_ref`.

`ProductConfigurationItemRead` exposes each configuration item with `key`,
`description`, `required`, `secret`, `default`, `current_value`, `is_set`.

`ProductSetupChecklistRead` aggregates configuration items into a checklist
with `items`, `total`, `completed`, `pending`.

`ProductReadinessRead` provides a comprehensive readiness overview:
`ready`, `blocking_missing_config`, `optional_missing_config`,
`unavailable_capabilities`, `degraded_capabilities`, `setup_checklist`,
`user_messages`.

| Method | Path | Success | Errors |
|---|---|---|---|
| GET | `/product/capabilities` | `200 list[ProductCapabilityRead]` | — |
| GET | `/product/configuration` | `200 list[ProductConfigurationItemRead]` | — |
| GET | `/product/setup-checklist` | `200 ProductSetupChecklistRead` | — |
| GET | `/product/readiness` | `200 ProductReadinessRead` | — |

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
