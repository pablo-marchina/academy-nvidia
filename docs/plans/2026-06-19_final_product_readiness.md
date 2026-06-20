# Final Product Readiness

**Date:** 2026-06-19  
**Branch:** `codex/final-product-readiness`  
**Goal:** make the repository a strict local-production product with clean source
control, reproducible installs, live documentation, and explicit blockers for
any non-production dependency, mock, demo, stale corpus, or uncalibrated
decision.

## Target State

- Product mode requires PostgreSQL, Qdrant, real RAG embeddings, populated and
  fresh NVIDIA corpus, LangGraph orchestration, and production-approved
  quantitative decisions.
- Demo routes, demo scripts, demo examples, sample-first UI paths, and generated
  runtime artifacts are removed from the production path.
- SQLite, in-memory vector stores, mock embeddings, sample data, and synthetic
  calibration are allowed only in explicit tests or historical fixtures.
- All public product outputs preserve evidence, RAG support, confidence,
  business impact, implementation complexity, next best action, and clear
  fact/inference/hypothesis separation where applicable.
- `validate-full`, product acceptance, frontend build, Playwright E2E, scope
  checks, documentation checks, and no-demo checks are reproducible from a clean
  checkout.

## Implementation Sequence

1. Clean repository hygiene and dependency reproducibility:
   - untrack generated/runtime artifacts such as `frontend/node_modules`,
     `data/product/*.db`, `*.tsbuildinfo`, caches, and pytest temp directories;
   - harden `.gitignore`;
   - create a frontend lockfile and switch frontend install docs/Makefile to
     reproducible install commands.
2. Enforce strict product readiness:
   - require PostgreSQL in `APP_MODE=product`;
   - require Qdrant URL/collection, `RAG_VECTOR_BACKEND=qdrant`, real embedding
     model, non-empty/fresh corpus, and LangGraph availability;
   - remove silent fallback for critical production dependencies while keeping
     explicit test/development modes.
3. Remove demo surfaces:
   - detach `/brief`, `/brief/evaluate`, and `/demo/artifacts` from the main
     FastAPI app;
   - remove demo CLI and sample-first frontend paths;
   - update tests and guards so product flow cannot read demo fixtures.
4. Enforce quantitative production gates:
   - block production decisions when calibration registry records are
     uncalibrated, synthetic-only, placeholder, or `production_allowed=false`;
   - register or remove untracked magic values;
   - fix scoring weight normalization.
5. Refresh RAG/corpus path:
   - keep only production corpus files in the active corpus directory;
   - run freshness audit and Qdrant ingestion paths;
   - validate RAG retrieval through Qdrant.
6. Consolidate live documentation:
   - update contracts, README, ROADMAP, EVALS, final architecture, final
     evaluation, and final acceptance evidence;
   - archive or remove contradictory historical/demo docs.
7. Validate:
   - run Python lint/format/typecheck/tests with local basetemp;
   - run frontend install/build/E2E;
   - run product acceptance with Postgres and Qdrant;
   - run no-demo, scope, docs closure, and magic-value checks.

## Acceptance Criteria

- `GET /product/readiness` returns `ready=false` with actionable blockers unless
  every production dependency and calibration requirement is satisfied.
- Product API exposes only persisted product resources in the main app.
- No tracked `node_modules`, local DB, cache, generated build metadata, or
  pytest temp artifacts remain.
- No live documentation describes Qdrant, RAG, PostgreSQL, or LangGraph as
  optional in product mode.
- Tests and docs clearly distinguish production, development, and fixture-only
  behavior.

