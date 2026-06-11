# Epic 25 — Minimal FastAPI Demo API

**Date:** 2026-06-11

## Summary

API FastAPI mínima que expõe pipeline, brief e answer quality evaluation via HTTP. Swagger em `/docs`. Seis endpoints. Zero duplicação de lógica central.

## What was built

- `src/api/` — main.py, schemas.py, routes.py, service.py
- `tests/integration/test_api_demo.py` — 9 testes de integração
- `docs/50_minimal_fastapi_demo_api.md` — design doc
- `src/main.py` atualizado para re-exportar app

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /version | Project version |
| GET | /rag/status | RAG/Qdrant status |
| POST | /brief | Generate brief |
| POST | /brief/evaluate | Evaluate brief quality |
| GET | /demo/artifacts | List demo artifacts |

## Design principle

API não duplica lógica. Chama `run_full_pipeline()`, `build_action_brief()`, `render_action_brief_markdown()` e `evaluate_answer_quality()` diretamente — mesmas funções da CLI.
