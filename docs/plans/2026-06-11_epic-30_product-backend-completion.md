# Plan: Epic 30 - Product Backend Completion

## Objective

Complete the product backend layer with Alembic migrations, PostgreSQL validation, startup PATCH, human review/status, opportunity ranking, and ExportRecord basics.

## Context Read

- `docs/54_final_product_backlog.md` — FPB-010 (review), FPB-011 (opportunities), FPB-012 (exports)
- `docs/55_product_backend_foundation.md` — deferred endpoints identified
- `docs/contracts/product_api_contract.md` — v1.0 contract to extend
- `docs/plans/2026-06-11_epic-29_product-backend-foundation.md` — foundation plan
- `README.md`, `ROADMAP.md`, `EVALS.md`, `AGENTS.md`, `DECISIONS.md`
- `.env.example`, `pyproject.toml`, `docker-compose.yml`, `Makefile`
- `src/database/` — 8 entities, `create_all`, no migrations
- `src/repositories/product.py` — ProductRepository
- `src/services/product/service.py` — ProductService
- `src/api/product_schemas.py` — schemas
- `src/api/product_routes.py` — 8 endpoints
- `tests/unit/` — product database, repositories, service tests
- `tests/integration/` — product API tests

## Scope

- Alembic migrations with SQLite + PostgreSQL support
- ReviewDecision and ExportRecord entity models
- PATCH /startups/{id} endpoint
- POST /analysis-runs/{id}/review and GET /analysis-runs/{id}/reviews
- GET /opportunities with filters, sorting, pagination
- POST /analysis-runs/{id}/exports and GET /exports/{id} (JSON/Markdown)
- Updated schemas, contracts, and documentation
- Unit and integration tests

## Out of Scope

- UI, auth, roles, PDF, CRM, job queue
- Scoring, RAG retrieval, Qdrant ingestion, recommendation changes
- Demo route removal or data/demo_runs deletion
- PostgreSQL as default, production deployment

## Files Created

- `alembic.ini`
- `migrations/env.py`
- `migrations/script.py.mako`
- `migrations/versions/e0d3e59b52e5_create_all_product_entities.py`
- `src/repositories/review.py`
- `src/repositories/export.py`
- `src/services/product/opportunity_service.py`
- `src/services/product/export_service.py`
- `tests/unit/test_alembic_migrations.py`
- `tests/unit/test_review_repository.py`
- `tests/unit/test_opportunity_service.py`
- `tests/unit/test_export_service.py`
- `tests/integration/test_product_patch_review_export.py`
- `tests/integration/test_postgres_migration.py`
- `docs/56_product_backend_completion.md`
- `docs/contracts/product_db_migrations.md`
- `docs/plans/2026-06-11_epic-30_product-backend-completion.md`

## Files Changed

- `pyproject.toml` — added alembic dependency
- `src/database/models.py` — added ReviewDecision, ExportRecord, rels on AnalysisRun
- `src/database/__init__.py` — exports new models
- `src/repositories/product.py` — added update_startup_fields()
- `src/services/product/service.py` — added update, review, opportunity, export methods
- `src/api/product_schemas.py` — added StartupUpdate, ReviewDecision*, Export*, Opportunity*, ErrorResponse
- `src/api/product_routes.py` — added 6 new endpoints
- `migrations/env.py` — prioritize config URL over env var
- `docs/contracts/product_api_contract.md` — v2.0 with new endpoints
- `DECISIONS.md` — 4 new decisions (030-033)
- `README.md` — migration commands, new endpoints
- `ROADMAP.md` — Epic 30 status
- `EVALS.md` — new test entries
- `.env.example` — PRODUCT_DB_TEST_URL
- `Makefile` — db-upgrade, db-downgrade, db-migrate, db-current, db-history

## Definition of Done

- [x] Alembic configurado
- [x] Migration inicial criada
- [x] SQLite upgrade head funcionando
- [x] PostgreSQL upgrade head validado (testes skippable)
- [x] PATCH /startups/{id} implementado
- [x] Review/status implementado (POST + GET)
- [x] GET /opportunities implementado
- [x] ExportRecord básico implementado
- [x] JSON/Markdown export funcionando
- [x] Contratos atualizados
- [x] Rotas demo preservadas
- [x] Fluxo produto não depende de data/demo_runs
- [x] Testes passam (505 passed, 29 skip/desel)
- [x] Nenhuma alteração em UI, scoring, RAG, Qdrant, recommendation

---

*Generated: 2026-06-12*
*Mode: Plan -> Artifact -> Build -> Review -> Commit*
