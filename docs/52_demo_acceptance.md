# Demo Acceptance & E2E Smoke Tests

**Epic 27** | **Date:** 2026-06-11

## Objective

Validate that the local demo works end to end in a repeatable way, without
adding product features or changing scoring, diagnosis, recommendation, RAG
retrieval, Qdrant ingestion, or Action Brief logic.

## Automated Acceptance

Run the full demo acceptance suite:

```bash
make demo-acceptance
```

This command runs:

1. API acceptance tests in `tests/integration/test_demo_acceptance.py`
2. Frontend TypeScript/Vite build via `make ui-build`
3. Playwright UI smoke tests via `make ui-e2e`

The smoke path is offline by default. Qdrant is allowed to be unavailable and
must surface as status/warning rather than a crash.

## API Acceptance Coverage

`tests/integration/test_demo_acceptance.py` verifies:

- `GET /health` returns 200 and `{"status": "ok"}`
- `GET /rag/status` returns 200 without requiring Qdrant
- `POST /brief` accepts `examples/demo/sample_startup_input.json`
- `POST /brief` returns `brief_json`, `brief_markdown`, scores,
  `recommended_motion`, gaps, evidence, warnings, and `run_report`
- `POST /brief/evaluate` returns `PASS`, `WARN`, or `FAIL`
- `GET /demo/artifacts` rejects path traversal attempts

## UI Smoke Coverage

`tests/e2e/test_demo_ui.spec.ts` verifies:

- UI opens through Vite
- API status appears
- Qdrant offline appears as a non-blocking status
- `Load example` populates the fictional startup sample
- `Generate Startup Action Brief` calls the API and renders the brief
- Scorecards, gaps, evidence, and Markdown output appear
- `Evaluate brief` returns a visible `PASS`, `WARN`, or `FAIL`
- API offline is shown as a readable error

Playwright keeps trace, screenshot, and video artifacts only on failure.

## Commands

```bash
make api-test          # API demo + acceptance integration tests
make ui-build          # TypeScript + Vite build
make ui-e2e            # Playwright smoke test
make demo-acceptance   # API acceptance + UI build + E2E
make demo-full-check   # Alias for full demo acceptance
```

## Manual Fallback Checklist

Use this only when Playwright browsers are not installed in the local
environment.

1. Run `make api-dev`.
2. In another terminal, run `make ui-dev`.
3. Open `http://127.0.0.1:5173`.
4. Confirm API status is online.
5. Confirm Qdrant offline is warning/status, not a crash.
6. Click `Load example`.
7. Click `Generate Startup Action Brief`.
8. Confirm `Nexus AI Labs` appears in the brief.
9. Confirm scorecards, gaps, NVIDIA technologies, evidence, warnings or empty
   warning state, and Markdown output appear.
10. Click `Evaluate brief` and confirm `PASS`, `WARN`, or `FAIL`.

## Non-Changes

- No scoring changes
- No diagnosis changes
- No recommendation changes
- No `recommended_motion` changes
- No RAG retrieval changes
- No Qdrant ingestion changes
- No Action Brief generation changes
- No LLM calls
