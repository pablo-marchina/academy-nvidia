# Minimal FastAPI Demo API

**Decision:** Criar API FastAPI mínima em `src/api/`, sem autenticação, sem frontend, sem deploy cloud, reaproveitando lógica da CLI/pipeline existente.

**Date:** 2026-06-11

## Context

O CLI demo (Epic 24) demonstra o sistema localmente, mas stakeholders e integradores precisam de interface HTTP programática. FastAPI/Uvicorn já estavam declarados em `pyproject.toml`. Havia um `src/main.py` mínimo com apenas `GET /health`.

## Decision

- `src/api/main.py` — FastAPI app com CORS, lifespan, router incluso
- `src/api/schemas.py` — Pydantic request/response
- `src/api/routes.py` — 6 endpoints (thin, delegam para service)
- `src/api/service.py` — chama `run_full_pipeline()`, `build_action_brief()`, `evaluate_answer_quality()` diretamente
- `src/main.py` re-exporta app de `src/api/main.py` (backward compat)
- Qdrant offline: capturado via `QdrantConnectionError`, nunca crasha a API
- Path traversal: `GET /demo/artifacts` valida que path resolved está dentro de `data/demo_runs/`

## Status

Implementado no Epic 25.
