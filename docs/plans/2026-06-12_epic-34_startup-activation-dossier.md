# Plan: Epic 34 — Startup Activation Dossier

**Date:** 2026-06-12
**Status:** Executed

## Goal

Build the Startup Activation Dossier as the persistent, versioned artifact that
consolidates all product intelligence per AnalysisRun — scores, gaps, NVIDIA
mappings, activation recommendations, claims, reviews, readiness checks, and
human verdict — into a single deterministic JSON + Markdown output.

## Scope

### In
- New table `activation_dossier_records` (FK → analysis_runs, versioned)
- Alembic migration 0004
- `ActivationDossierRepository` (CRUD, versioning, delete-for-run)
- Pydantic schemas: `ActivationDossierRead`, `ActivationDossierGenerateResponse`,
  `ActivationDossierMarkdownRead`, `ActivationDossierSummaryRead`
- `ActivationDossierService` with `build_dossier_for_analysis_run`,
  `get_latest_dossier`, `regenerate_dossier`, `get_dossier_markdown`,
  `get_dossier_summary`
- Deterministic JSON dossier projecting: startup, scores, gaps, mappings,
  activation playbooks, claims, reviews, readiness checks
- Deterministic Markdown renderer (11 template sections)
- 3 API endpoints: POST (generate), GET (latest json), GET /markdown
- Dossier summary injected into `AnalysisRunRead` and `OpportunityListItem`
- 5 degraded-state codes for dossier readiness
- Unit tests for repository (7) and service (10)
- Integration tests for API (8)

### Out
- No new LLM calls
- No UI, PDF, Ragas, DeepEval, Instructor, MCP, TOON, JTON
- No RAG retrieval, Qdrant ingestion, scoring, recommendation central changes
- Export integration deferred (existing ExportRecord can point to dossier_id later)
- Updating dossier after human review deferred (v2)

## Contract changes
- `product_api_contract.md` — add dossier endpoints, update invariants
- `activation_dossier_contract.md` — new

## Files changed/created
- `src/database/models.py` — +ActivationDossierRecord
- `migrations/versions/c3d4e5f6a7b8_create_activation_dossier_records.py`
- `src/repositories/dossier.py` — new
- `src/services/product/dossier_service.py` — new
- `src/api/product_schemas.py` — 4 new schemas + AnalysisRunRead/OpportunityListItem updates
- `src/api/product_routes.py` — 3 endpoints + injection helpers
- `src/services/product/degraded.py` — 5 new codes
- `tests/unit/test_dossier_repository.py` — 7 tests
- `tests/unit/test_dossier_service.py` — 10 tests
- `tests/integration/test_dossier_api.py` — 8 tests
