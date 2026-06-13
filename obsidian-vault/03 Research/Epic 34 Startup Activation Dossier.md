# Epic 34 — Startup Activation Dossier

**Status:** Concluído

## Resumo

Build do Startup Activation Dossier como artifact versionado que consolida todo o intelligence de um AnalysisRun (scores, gaps, mappings, activation, claims, reviews, readiness) em JSON + Markdown determinístico.

## Entregas

- `ActivationDossierRecord` model + Alembic migration 0004
- `ActivationDossierRepository` (CRUD, versioning, get_latest)
- `ActivationDossierService` (build, get, regenerate, markdown, summary)
- 3 API endpoints (POST generate, GET dossier, GET markdown)
- 5 degraded-state codes for dossier readiness
- 17 unit tests + 8 integration tests
- Docs: plan, module doc (60), contract
