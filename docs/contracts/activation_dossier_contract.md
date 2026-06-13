# Activation Dossier Contract

**Module:** `src/services/product/dossier_service.py`
**Repository:** `src/repositories/dossier.py`
**Version:** 1.0
**Date:** 2026-06-12

## Purpose

Provide a deterministic, versioned snapshot of all product intelligence for an
`AnalysisRun` — combining scores, gaps, NVIDIA mappings, activation
recommendations, claims, reviews, and readiness checks into a single JSON +
Markdown artifact.

## What It Promises

1. **Idempotent generation** — `build_dossier_for_analysis_run(run_id)` returns
   existing latest dossier if one exists. `force_new_version=True` always
   creates a new version.

2. **Deterministic content** — Every field in the dossier is projected from
   persisted records. No LLM calls, no embeddings, no random sources.

3. **Versioning** — Each analysis run has versions starting at 1. Only the
   latest dossier per run is marked `is_latest`. Previous versions are
   preserved.

4. **Honest about missing data** — If a persisted record type is missing
   (e.g. no activation recommendations, no review), the corresponding dossier
   section contains empty/null data, and an uncertainty entry is added.

5. **Risk-first readiness** — Readiness check violations (low coverage,
   unsupported claims, missing playbook match, missing review, incomplete
   scores) are recorded as `risks` in the dossier. They do NOT block dossier
   generation.

6. **Markdown rendering** — `get_dossier_markdown(run_id)` returns a complete
   Markdown string with all 11 template sections. Never fails for invalid
   data — missing fields render as "Not available" or "Missing".

7. **Dossier summary** — A lightweight `ActivationDossierSummaryRead`
   (created_at, version, risk_count, unsupported_claim_count) is available
   for inclusion in analysis run and opportunity responses.

## What It Does NOT Promise

1. **No LLM extraction** — Dossier never calls an LLM to generate or summarize
   content.

2. **No auto-update on review** — Dossier is not automatically regenerated
   when a review decision is submitted. Caller must POST with
   `force_new_version=true`.

3. **No exports** — Dossier does not generate files or manage export records.
   Future `ExportRecord` may reference `dossier_id`.

4. **No PDF** — Dossier Markdown is plain text. PDF rendering is out of scope.

5. **No RAG context** — Dossier excludes RAG retrieval results. It focuses on
   structured product records only.

## Schema

### ActivationDossierRecord (database)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID (PK) | |
| `analysis_run_id` | UUID (FK → analysis_runs, NOT NULL) | |
| `version` | Integer (NOT NULL) | Starts at 1 per run |
| `dossier_json` | JSON (NOT NULL) | Full dossier content |
| `dossier_markdown` | Text (NOT NULL) | Markdown rendering |
| `is_latest` | Boolean (NOT NULL, default True) | Only one `True` per run |
| `created_at` | DateTime (NOT NULL) | |

**Unique constraint:** `(analysis_run_id, version)`

**Indexes:** `analysis_run_id`, `(analysis_run_id, is_latest)`, `(analysis_run_id, version DESC)`

### Repository Methods

- `create_dossier(record) -> ActivationDossierRecord`
- `get_latest_for_analysis_run(run_id) -> ActivationDossierRecord | None`
- `get_by_id(dossier_id) -> ActivationDossierRecord | None`
- `list_for_analysis_run(run_id) -> list[ActivationDossierRecord]`
- `next_version_for_analysis_run(run_id) -> int`
- `mark_previous_not_latest(run_id) -> None`
- `delete_for_analysis_run(run_id) -> None`

### Service Methods

- `build_dossier_for_analysis_run(run_id, force_new_version=False) -> ActivationDossierRecord`
- `get_latest_dossier(run_id) -> ActivationDossierRecord | None`
- `regenerate_dossier(run_id) -> ActivationDossierRecord`
- `get_dossier_markdown(run_id) -> str | None`
- `get_dossier_summary(run_id) -> ActivationDossierSummaryRead | None`

## Degraded States (in dossier)

| Code | Condition | Trigger |
|------|-----------|---------|
| `DOSSIER_LOW_EVIDENCE_COVERAGE` | evidence_coverage < 20% | Readiness check |
| `DOSSIER_UNSUPPORTED_CRITICAL_CLAIMS` | unsupported_claim_count > 0 | Readiness check |
| `DOSSIER_NO_ACTIVATION_PLAYBOOK` | no matched activation playbook | Readiness check |
| `DOSSIER_MISSING_REVIEW` | no human review recorded | Readiness check |
| `DOSSIER_INCOMPLETE_SCORES` | any score is None | Readiness check |

## API Contract

See `product_api_contract.md` for full endpoint definitions.

| Method | Path | Request | Success | Errors |
|--------|------|---------|---------|--------|
| POST | `/analysis-runs/{id}/dossier` | `?force=true\|false` | `201 ActivationDossierRead` | 404, 409 (draft run) |
| GET | `/analysis-runs/{id}/dossier` | — | `200 ActivationDossierRead` | 404 |
| GET | `/analysis-runs/{id}/dossier/markdown` | — | `200 ActivationDossierMarkdownRead` | 404 |
