> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Epic 25 — Minimal FastAPI Demo API

**Date:** 2026-06-11
**Status:** Approved / In Progress

## Objective

Create a minimal FastAPI API that exposes the existing CLI/pipeline logic via HTTP endpoints, enabling Swagger/OpenAPI demo, future frontend integration, and programmatic access without terminal dependency.

## Scope

### Create
- `src/api/__init__.py`
- `src/api/main.py` — FastAPI app with lifespan, CORS, router
- `src/api/schemas.py` — Pydantic request/response models
- `src/api/routes.py` — endpoint handlers (thin, delegate to service)
- `src/api/service.py` — business logic reusing pipeline/briefing/eval
- `tests/integration/test_api_demo.py` — integration tests
- `docs/50_minimal_fastapi_demo_api.md` — design doc

### Update
- `src/main.py` — re-export app from `src/api/main.py`
- `README.md` — API section with how to run
- `ROADMAP.md` — mark Epic 25 complete
- `Makefile` — add api, api-dev, api-test targets
- `EVALS.md` — add API test line
- `DECISIONS.md` — register architectural decision
- `docs/plans/2026-06-11_epic-25_minimal-fastapi-demo-api.md` (this plan)
- `obsidian-vault/` — backfill (decision + research note)

### Not changed
- No changes to `src/pipeline/`, `src/briefing/`, `src/rag/`, `src/evaluation/`, `src/scoring/`, `src/diagnosis/`, `src/recommendation/`
- No new dependencies (FastAPI/Uvicorn already declared)
- No frontend, no auth, no cloud deploy, no Dockerfile

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /version | Project version |
| GET | /rag/status | RAG/Qdrant configuration & availability |
| POST | /brief | Generate Startup Action Brief |
| POST | /brief/evaluate | Evaluate brief quality (PASS/WARN/FAIL) |
| GET | /demo/artifacts | List generated demo artifacts |

## Architecture

```
HTTP request → routes.py (thin handler) → service.py (reuses pipeline/briefing/eval modules)
```

Service layer calls the same functions as the CLI:
- `run_full_pipeline()` from `src/pipeline/run_pipeline.py`
- `build_action_brief()` from `src/briefing/action_brief.py`
- `render_action_brief_markdown()` from `src/briefing/markdown_renderer.py`
- `evaluate_answer_quality()` from `src/evaluation/answer_quality_eval.py`

## Qdrant Offline Handling

- `GET /rag/status` catches `QdrantConnectionError` and returns `qdrant_available: false`
- `POST /brief` with Qdrant backend unavailable returns warning, falls back gracefully
- API never crashes due to Qdrant being offline

## Acceptance Criteria

- [ ] API starts with `uvicorn src.api.main:app`
- [ ] Swagger at `GET /docs`
- [ ] All 6 endpoints return correct schemas
- [ ] Tests pass with `pytest tests/integration/test_api_demo.py`
- [ ] `make api`, `make api-dev`, `make api-test` work
- [ ] README shows how to run
- [ ] No central logic duplicated
- [ ] ruff/black/mypy pass

