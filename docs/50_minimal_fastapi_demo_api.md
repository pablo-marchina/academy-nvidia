# Minimal FastAPI Demo API

> **ARCHIVED:** Historical design doc for Epic 25 (demo API). Product API now exists at `/startups`, `/analysis-runs`, `/opportunities`, `/exports`. Demo endpoints (`/brief`, `/brief/evaluate`, `/demo/artifacts`) are deprecated. This document is preserved for reference only.

**Epic 25** | **Date:** 2026-06-11

## Objective

Expose the existing CLI/pipeline logic via HTTP endpoints, enabling Swagger/OpenAPI demo, future frontend integration, and programmatic access without terminal dependency.

## Architecture

```
src/api/
├── __init__.py
├── main.py         # FastAPI app, CORS, lifespan, router
├── schemas.py      # Pydantic request/response models
├── routes.py       # Endpoint handlers (thin, delegate to service)
└── service.py      # Business logic reusing pipeline/briefing/eval
```

The service layer calls the same functions as `scripts/run_startup_radar_demo.py`:

- `run_full_pipeline()` from `src/pipeline/run_pipeline.py`
- `build_action_brief()` from `src/briefing/action_brief.py`
- `render_action_brief_markdown()` from `src/briefing/markdown_renderer.py`
- `evaluate_answer_quality()` from `src/evaluation/answer_quality_eval.py`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/version` | Project name, version, description |
| GET | `/rag/status` | RAG backend, collection, Qdrant availability |
| POST | `/brief` | Generate Startup Action Brief |
| POST | `/brief/evaluate` | Evaluate brief quality (PASS/WARN/FAIL) |
| GET | `/demo/artifacts` | List generated demo artifacts |

## Design Decisions

### Why not subprocess
The API calls pipeline functions directly instead of shelling out to the CLI script. This avoids process overhead, preserves type safety, and keeps error handling immediate.

### Qdrant offline resilience
`GET /rag/status` catches `QdrantConnectionError` and returns `qdrant_available: false` without crashing. `POST /brief` with Qdrant backend unavailable returns a warning and gracefully degrades.

### No auth, no frontend, no cloud
The API is explicitly local/dev only. No authentication, no Streamlit frontend, no cloud deployment.

### Path traversal protection
`GET /demo/artifacts` resolves the requested path against the allowed base directory (`data/demo_runs/`) and rejects any path that escapes outside it.

## Endpoint Details

### GET /health
```json
{"status": "ok"}
```

### GET /version
```json
{
  "name": "nvidia-startup-ai-radar",
  "version": "0.1.0",
  "description": "Foundation workspace for the NVIDIA Startup AI Radar project."
}
```

### GET /rag/status
```json
{
  "backend": "in_memory",
  "collection_name": "nvidia_corpus",
  "vector_size": 384,
  "qdrant_url": "http://localhost:6333",
  "qdrant_available": false,
  "error": "Cannot connect to Qdrant at http://localhost:6333: ..."
}
```

### POST /brief
Request:
```json
{
  "startup_name": "Nexus AI Labs",
  "profile": {"sector": "HealthTech", "description": "...", ...},
  "evidence": [{"claim": "...", "confidence": "high"}, ...],
  "source_url": "https://example.com",
  "use_rag": false,
  "rag_backend": "local",
  "offline": true,
  "run_answer_quality_eval": false
}
```
Response:
```json
{
  "run_id": "api_20260611_123456",
  "startup_name": "Nexus AI Labs",
  "brief_json": { "... full StartupActionBrief ..." },
  "brief_markdown": "# Startup Action Brief: Nexus AI Labs ...",
  "run_report": { "status": "completed", ... },
  "answer_quality_eval": null,
  "warnings": []
}
```

### POST /brief/evaluate
Request:
```json
{
  "startup_name": "Nexus AI Labs",
  "brief_json": { "... brief from POST /brief ..." }
}
```
Response:
```json
{
  "status": "PASS",
  "metrics": { "required_sections_present": true, ... },
  "gates": [...],
  "failure_reasons": [],
  "warnings": []
}
```

### GET /demo/artifacts
```json
{
  "artifacts": [
    {
      "filename": "startup_action_brief.json",
      "path": "latest/startup_action_brief.json",
      "size_bytes": 4289,
      "modified_at": "2026-06-11T10:30:00+00:00"
    }
  ],
  "total": 1
}
```

## Running

```bash
# Start API (production mode)
uvicorn src.api.main:app

# Start API with hot reload
uvicorn src.api.main:app --reload

# Or via Makefile
make api
make api-dev
```

## Testing

```bash
pytest tests/integration/test_api_demo.py -v
make api-test
```

## Contract Coverage

| Contract | API interaction |
|---|---|
| `pipeline_output_contract.md` | `POST /brief` calls `run_full_pipeline()` |
| `briefing_contract.md` | `POST /brief` calls `build_action_brief()` + `render_action_brief_markdown()` |
| `rag_contract.md` | `GET /rag/status` checks Qdrant status; `POST /brief` uses RAG if enabled |

## Known Limitations

- No authentication — local/dev only.
- No support for real LLM judge in evaluate endpoint.
- Pipeline runs synchronously — may block for several seconds.
- File-based `data/` structure expected; missing directories return empty lists.
- Qdrant status checks connectivity but not data freshness.
