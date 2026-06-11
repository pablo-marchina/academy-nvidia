# Minimal Demo UI

**Epic 26** | **Date:** 2026-06-11

## Objective

Provide a minimal local web UI for evaluators who need to demo NVIDIA Startup AI
Radar without terminal commands or direct Swagger usage. The UI consumes the
existing FastAPI demo API and does not duplicate core product logic.

## Architecture

```
frontend/ (Vite + React + TypeScript)
  -> fetch client
  -> FastAPI demo API
  -> existing pipeline, briefing, RAG status, and answer quality eval
```

The frontend is local/dev only. It has no authentication, no deploy path, no
database, no design system, and no new product rules.

## Files

```
frontend/
  index.html
  package.json
  vite.config.ts
  tsconfig.json
  .env.example
  src/
    App.tsx
    api/client.ts
    sampleStartupInput.ts
    components/
      StartupInputForm.tsx
      BriefViewer.tsx
      ScoreCards.tsx
      GapTechnologyTable.tsx
      EvidencePanel.tsx
      RagStatusBadge.tsx
      EvalStatusPanel.tsx
    styles.css
```

## API Contract

The API base URL is configured through:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

Client helpers:

| Helper | Endpoint | Purpose |
|--------|----------|---------|
| `getHealth()` | `GET /health` | Check API availability |
| `getRagStatus()` | `GET /rag/status` | Show RAG/Qdrant status |
| `createBrief()` | `POST /brief` | Generate Startup Action Brief |
| `evaluateBrief()` | `POST /brief/evaluate` | Run optional answer quality eval |
| `listDemoArtifacts()` | `GET /demo/artifacts` | Show artifact count/status |

## Demo Flow

1. Start API with `make api-dev`.
2. Start UI with `make ui-dev`.
3. Open the Vite URL, usually `http://127.0.0.1:5173`.
4. Click `Load example`.
5. Keep offline mode enabled for the simplest local path.
6. Click `Generate Startup Action Brief`.
7. Review scorecards, gaps, NVIDIA technologies, evidence, warnings,
   uncertainties, and Markdown output.
8. Click `Evaluate brief` to run optional answer quality evaluation.

## Error Handling

- API offline: displayed as a runtime error; input remains editable.
- Qdrant offline: displayed as warning/status, not a blocking failure.
- Invalid JSON: handled before any API call.
- Brief generation failure: API error is shown in the input panel.
- Evaluation failure: API error is shown in the evaluation panel.

## Validation

```bash
cd frontend
npm install
npm run build
```

Repo-level checks remain:

```bash
pytest
ruff check .
black --check .
mypy src
```

## Known Limitations

- Local/dev only.
- No authentication or deploy workflow.
- No frontend unit test stack yet; the v1 validation is TypeScript build plus
  manual smoke test.
- Markdown is displayed as text; structured fields are rendered separately.
- The UI does not persist generated briefs outside API/runtime behavior.

## Non-Changes

- No scoring changes.
- No diagnosis changes.
- No recommendation changes.
- No `recommended_motion` changes.
- No RAG retrieval changes.
- No Qdrant ingestion changes.
- No answer quality metric changes.
- No scraping or LLM calls.
