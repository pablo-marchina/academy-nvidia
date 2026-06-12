# Product Simplification & Deletion Pass

**Epic:** 31
**Date:** 2026-06-12
**Status:** Executed

---

## 1. Objective

Remove, archive, or isolate demo heritage artifacts after the product backend is complete (Epics 29-30), reducing complexity and ensuring demo is not the main flow.

## 2. Files Deleted (DELETE_NOW)

| File | Reason |
|------|--------|
| `data/demo_runs/latest/demo_run_report.json` | Generated demo artifact |
| `data/demo_runs/latest/startup_action_brief.json` | Generated demo artifact |
| `data/demo_runs/latest/startup_action_brief.md` | Generated demo artifact |
| `data/nvidia_corpus/archive_test.md` | Test artifact in corpus |
| `data/nvidia_corpus/nim_test.md` | Test artifact in corpus |
| `data/nvidia_corpus/temp_test_source.md` | Temp file in corpus |
| `data/regression_reports/latest_dashboard.json` | Generated report |
| `data/regression_reports/latest_dashboard.md` | Generated report |
| `data/regression_reports/answer_quality_eval_junit.xml` | Generated report |
| `data/regression_reports/answer_quality_llm_judge_report.json` | Generated report |
| `data/regression_reports/answer_quality_llm_judge_report.md` | Generated report |
| `data/ingestion_reports/freshness_after_qdrant_384_reingestion.md` | Generated report |
| `data/ingestion_reports/freshness_audit_after_reingestion.md` | Generated report |
| `data/ingestion_reports/lifecycle_dry_run.json` | Generated report |
| `data/ingestion_reports/lifecycle_reingestion_idempotence.json` | Generated report |
| `data/ingestion_reports/lifecycle_reingestion.json` | Generated report |
| `data/ingestion_reports/qdrant_384_dry_run.json` | Generated report |
| `data/ingestion_reports/qdrant_384_reingestion.json` | Generated report |

**.gitignore updated:** `data/demo_runs/latest/`, `data/regression_reports/*` (except .gitkeep), `data/ingestion_reports/` added.

## 3. Files Archived (ARCHIVE_HISTORY)

All files marked with `> **ARCHIVED:**` header. Not moved or deleted.

### Demo docs
- `docs/08_demo_script.md`
- `docs/49_cli_demo_end_to_end.md`
- `docs/50_minimal_fastapi_demo_api.md`
- `docs/51_minimal_demo_ui.md`
- `docs/52_demo_acceptance.md`
- `examples/demo/README.md`

### Historical/superseded docs
- `docs/00_case_plan.md`
- `docs/05_rag_design.md`
- `docs/26_architecture_utilization_audit.md`

### Historical plans (21 files in `docs/plans/`)
All plan files except `PLAN_TEMPLATE.md` and Epics 28-31.

## 4. Files Kept as Fixtures/Golden (KEEP_AS_FIXTURE_OR_GOLDEN)

| File | Reason |
|------|--------|
| `examples/demo/sample_startup_input.json` | Used by integration tests and CLI |
| `examples/golden/` (9 files) | Golden eval harness (38 tests) |
| `examples/rag_eval/` (2 files) | RAG eval golden queries |
| `examples/answer_quality/` (2 files) | Answer quality eval fixtures |
| `examples/validation/` (5 files) | Output validation fixtures |

## 5. Files Kept as Live Docs (KEEP_AS_LIVE_DOC)

- README.md, ROADMAP.md, EVALS.md, AGENTS.md, DECISIONS.md
- docs/10 through 17 (product rules)
- docs/27, 28, 35-48, 52, 53, 54, 55, 56
- docs/contracts/* (10 files)
- data/nvidia_corpus/sources.yaml, source_allowlist.yaml

## 6. Items Not Removed (REPLACE_BEFORE_DELETE)

| Item | Reason |
|------|--------|
| `scripts/run_startup_radar_demo.py` | No product CLI replacement yet |
| `frontend/` | No product UI yet |
| `src/main.py` | Re-exports from api.main; checked: no external imports |

## 7. Items Not Removed (DELETE_AFTER_TEST_UPDATE — deferred)

| Item | Blocking dependency |
|------|---------------------|
| `src/api/routes.py` | Integration tests use /brief, /brief/evaluate, /demo/artifacts |
| `src/api/schemas.py` | Used by routes.py |
| `src/api/service.py` | Used by routes.py |
| `tests/integration/test_api_demo.py` | 9 tests referencing demo endpoints |
| `tests/integration/test_cli_demo.py` | 6 tests referencing demo script |
| `tests/integration/test_demo_acceptance.py` | 5 tests referencing demo API |
| `tests/e2e/test_demo_ui.spec.ts` | Depends on frontend |
| Makefile targets (demo-cli, demo-acceptance, etc.) | Used by legacy workflows |

## 8. README Changes

- Objective section: removed reference to archived `docs/00_case_plan.md`, added reference to `docs/57`
- High-Level Architecture: removed reference to archived docs
- "Running the CLI Demo" section: replaced with "Legacy Demo CLI" short note
- "Running the Minimal Demo UI" section: replaced with "Legacy Demo UI" short note
- "Running the API" section: reorganized into "Product endpoints (primary flow)" and "Legacy demo endpoints (deprecated)"
- Product API tests: updated to reference product integration tests
- Makefile targets: removed `demo-acceptance`, `demo-full-check`, `ui-e2e` from list

## 9. ROADMAP Changes

- Epic 31 updated from "planejado" to "concluído" with execution checklist
- Added placeholder for Epics 32-34 (Evidence & Claim Ledger, Product UI, Activation Playbooks)

## 10. DECISIONS.md Changes

- Added **Decision 034 — Demo Artifacts Are Not Product Sources**

## 11. Regression Test Added

Test `test_product_modules_do_not_reference_demo_runs` in `tests/unit/test_product_database.py`:
- Scans all Python files under `src/database/`, `src/repositories/`, `src/services/product/`, `src/api/product_routes.py`, `src/api/product_schemas.py`
- Asserts none contain the string `demo_runs`
- Provides clear failure message with file path if violation found

## 12. Obsidian Vault Changes

- `obsidian-vault/04 Decisions/Epic 31 Product Simplification Deletion Pass.md` — decision note
- `obsidian-vault/03 Research/Epic 31 Product Simplification Deletion Pass.md` — research note
- Epic notes in 03 Research and 04 Decisions tagged #archived

## 13. Validations Executed

- pytest -m "not integration" (unit tests only)
- ruff check .
- black --check .
- mypy src
- python scripts/check_scope.py
- alembic upgrade head (SQLite)

## 14. Known Limitations / Deferred

- Demo API routes (`/brief`, `/brief/evaluate`, `/demo/artifacts`) remain in `src/api/routes.py`
- Demo integration tests remain in `tests/integration/`
- CLI demo script (`scripts/run_startup_radar_demo.py`) unchanged
- Frontend (`frontend/`) unchanged
- These are classified as DELETE_AFTER_TEST_UPDATE or REPLACE_BEFORE_DELETE
- A future epic should remove them after product test coverage is sufficient

## 15. Key Decision

Demo artifacts are not product sources. Product flow uses persisted product entities and contracts.
