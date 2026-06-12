# Product Backend Completion

**Epic:** 30
**Date:** 2026-06-12
**Status:** Implemented

## Objective

Complete the product backend layer before advancing to UI, auth, PDF export, or CRM. Builds on the Product Backend Foundation (Epic 29) by adding formal Alembic migrations, PostgreSQL validation, startup PATCH, human review/status, opportunity ranking, and ExportRecord basics.

## What Was Implemented

1. **Alembic migrations** — versioned schema management with SQLite and PostgreSQL support
2. **PostgreSQL validation** — skippable integration tests for PG compatibility
3. **SQLite/Postgres compatibility** — portable types, batch mode for SQLite
4. **PATCH /startups/{id}** — partial update with normalized_name recalculation
5. **Review/status** — `POST /analysis-runs/{id}/review` and `GET /analysis-runs/{id}/reviews`
6. **Opportunities ranking** — `GET /opportunities` with filters, sorting, pagination
7. **ExportRecord** — `POST /analysis-runs/{id}/exports` and `GET /exports/{id}` for JSON/Markdown

## Architecture

```
Alembic
  |
  v
SQLAlchemy models (10 entities) ---- SQLite (default)
  |                                       |
  |--- review_decisions                  PostgreSQL (tested)
  |--- export_records
  |
Repositories:
  ProductRepository -- update_startup_fields
  ReviewDecisionRepository
  ExportRepository

Services:
  ProductService    -- orchestration (update, review, export)
  OpportunityService -- ranking and filtering
  ExportService     -- JSON/Markdown generation

FastAPI product routes (12 endpoints)
```

## New Entities

### ReviewDecision
- `id`, `analysis_run_id` (FK), `decision`, `reviewer`, `notes`, `metadata_json`
- Decisions: `approve`, `reject`, `needs_more_evidence`, `monitor`, `contact`, `not_recommended`
- Append-only: multiple reviews per run preserved; latest by `created_at`

### ExportRecord
- `id`, `analysis_run_id` (FK), `action_brief_id` (FK), `export_type`, `status`, `storage_path`, `content_hash`, `error_message`
- Types: `json`, `markdown`; `pdf_reserved` for future
- Path: relative to `PRODUCT_DATA_DIR/exports/`

## New Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| PATCH | `/startups/{id}` | Partial startup update |
| POST | `/analysis-runs/{id}/review` | Record human review decision |
| GET | `/analysis-runs/{id}/reviews` | List reviews for a run |
| GET | `/opportunities` | Ranked opportunities with filters |
| POST | `/analysis-runs/{id}/exports` | Generate JSON/Markdown export |
| GET | `/exports/{id}` | Retrieve export metadata |

## Migrations

Initial migration `0001_create_all_product_entities.py` creates all 10 product tables and indexes. Supports both SQLite (batch mode) and PostgreSQL.

## Decisions

- Alembic for versioned schema management
- `render_as_batch=True` in SQLite mode for ALTER TABLE compatibility
- Review is append-only; doesn't alter scores
- Opportunities use only the latest completed/degraded run per startup
- Export uses `ActionBriefRecord` (persisted), not `data/demo_runs`
- PostgreSQL validated via skippable integration tests
