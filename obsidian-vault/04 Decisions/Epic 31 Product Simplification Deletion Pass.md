---
tags: [decision, epic-31, architecture]
date: 2026-06-12
---

# Epic 31 — Product Simplification & Deletion Pass

## Decisão

Demo artifacts are not product sources. Product flow uses persisted entities configured by `PRODUCT_DB_URL`. Demo heritage artifacts were removed, archived, or isolated — reducing complexity and ensuring demo is not the main flow.

## O que foi feito

- **DELETE_NOW**: 17 generated artifacts removed (data/demo_runs/latest, data/nvidia_corpus test files, regression_reports, ingestion_reports)
- **ARCHIVE_HISTORY**: 26+ doc/plan files archived with header (not moved/deleted)
- **README restructuring**: Demo replaced as primary flow in docs, CLI, UI, and API sections
- **ROADMAP/DECISIONS update**: Epic 31 marked done; Decision 034 registered
- **Regression test**: `test_product_modules_do_not_reference_demo_runs` in `test_product_database.py`
- **.gitignore update**: 3 new rules for generated data

## O que NÃO foi removido (deferido para épico futuro)

- Demo API routes (`src/api/routes.py`), schemas, service — dependem de atualização de testes
- Demo CLI script (`scripts/run_startup_radar_demo.py`) — sem CLI produto ainda
- Frontend (`frontend/`) — sem UI produto ainda
- Demo integration tests (`tests/integration/test_api_demo.py`, `test_cli_demo.py`, `test_demo_acceptance.py`) — dependem dos endpoints demo
- Makefile demo targets — usados em workflows legados
