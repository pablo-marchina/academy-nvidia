# Plan: Epic 29 - Product Backend Foundation

## Objective

Implement the minimum transactional backend foundation for NVIDIA Startup AI
Radar to operate on persisted product records instead of demo artifacts. The
build uses SQLite first, keeps Qdrant limited to vector search/RAG, preserves
the current deterministic pipeline, and exposes a small product API.

## Context Read

- `docs/54_final_product_backlog.md`
- `docs/plans/2026-06-11_epic-28_documentation-mining-final-product-backlog.md`
- `README.md`, `ROADMAP.md`, `EVALS.md`, `AGENTS.md`, `DECISIONS.md`
- `docs/contracts/`
- `docs/14_evidence_policy.md`, `docs/16_briefing_template.md`
- `docs/40_ci_cd_quality_gates.md`
- `docs/50_minimal_fastapi_demo_api.md`, `docs/51_minimal_demo_ui.md`
- `src/api/`, `src/database/`, `src/pipeline/`, `src/briefing/`
- `src/scoring/`, `src/diagnosis/`, `src/recommendation/`, `src/rag/`
- `src/evaluation/`, `tests/`, `.env.example`, `pyproject.toml`, `Makefile`

`docs/19_definition_of_done.md` and `docs/23_eval_gates.md` do not exist. Their
live equivalents are `docs/contracts/end_of_epic_contract.md`, `EVALS.md`, and
`docs/40_ci_cd_quality_gates.md`.

## Scope

- SQLAlchemy product database runtime with SQLite default and configurable URL.
- Transactional product models, constraints, indexes, and repositories.
- Product service that persists pipeline results and explicit degraded states.
- Product Pydantic schemas and minimum FastAPI routes.
- Unit, integration, lifecycle, and demo-independence regression tests.
- Product backend design, API contract, decisions, roadmap, eval, and Obsidian updates.

## Out of Scope

- Changes to scoring, diagnosis, recommendation, RAG retrieval, or Qdrant ingestion.
- UI changes, authentication, roles, CRM, PDF export, or external job queues.
- Deletion of demo routes, `data/demo_runs`, examples, or demo artifacts.
- Complete review, opportunities, or export workflows.

## Proposed Implementation

1. Implement portable SQLAlchemy models and a configurable session runtime.
2. Add repositories for startups, evidence, runs, outputs, briefs, and readiness checks.
3. Add a product service that adapts persisted records to the existing pipeline.
4. Add product API schemas and routes while preserving demo endpoints.
5. Add isolated SQLite tests and API integration tests.
6. Document the architecture, contract, SQLite-first decision, and remaining P1 work.
7. Run diff review and all applicable repository validation commands.

## Files to Create/Change

### Create

- `src/repositories/` - transactional persistence operations.
- `src/services/product/` - product orchestration and health checks.
- `src/api/product_schemas.py` - public product API schemas.
- `src/api/product_routes.py` - public product endpoints.
- `tests/unit/test_product_database.py`
- `tests/unit/test_product_repositories.py`
- `tests/integration/test_product_api.py`
- `docs/55_product_backend_foundation.md`
- `docs/contracts/product_api_contract.md`
- Obsidian Epic 29 summary and decision notes.

### Change

- `src/database/models.py`, `src/database/session.py`
- `src/api/main.py`
- `.env.example`, `README.md`, `ROADMAP.md`, `EVALS.md`, `DECISIONS.md`

## Tests/Validations

- Product database initialization with temporary SQLite.
- Repository CRUD, constraints, lifecycle, brief versioning, and readiness checks.
- Product API creation, listing, run execution, brief retrieval, and health.
- Regression assertion that product modules do not reference `data/demo_runs`.
- `pytest -m "not integration"`, full `pytest`, ruff, black, mypy.
- `python scripts/check_scope.py` and `python scripts/check_docs_closure.py`.

## Risks

| Risk | Mitigation |
|---|---|
| Database logic couples to the pipeline | Keep conversion and persistence in product service adapters |
| SQLite behavior blocks Postgres migration | Use SQLAlchemy portable types and constraints |
| Qdrant state is duplicated | Persist only retrieval references and dependency state in SQLite |
| Optional dependency failure is hidden | Persist ProductReadinessCheck and set run to degraded |
| Demo compatibility breaks | Register a separate router and leave existing routes unchanged |

## Definition of Done

- [x] SQLite product DB initializes from `PRODUCT_DB_URL`.
- [x] Product entities and repositories work with isolated tests.
- [x] Startup and AnalysisRun lifecycle records persist.
- [x] Pipeline output, evidence, scores, gaps, mappings, and brief persist.
- [x] Degraded states are explicit and queryable.
- [x] Minimum product routes and health endpoints work.
- [x] Product flow has no dependency on `data/demo_runs`.
- [x] Product API contract and architecture documentation are current.
- [x] Quality and documentation checks pass or blockers are recorded.

---

*Generated: 2026-06-11*
*Mode: Plan -> Artifact -> Build -> Review -> Commit*
