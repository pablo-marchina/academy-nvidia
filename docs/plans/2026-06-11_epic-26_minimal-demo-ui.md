> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Plan: Epic 26 - Minimal Demo UI

## Objective

Create a minimal local/demo UI for NVIDIA Startup AI Radar so evaluators can run
the existing FastAPI demo flow without terminal or Swagger. The UI consumes the
already implemented API endpoints and does not duplicate product logic.

## Context Read

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `Makefile`
- `docs/50_minimal_fastapi_demo_api.md`
- `docs/16_briefing_template.md`
- `docs/contracts/briefing_contract.md`
- `docs/contracts/pipeline_output_contract.md`
- `src/api/`
- `scripts/run_startup_radar_demo.py`
- `examples/demo/sample_startup_input.json`
- `obsidian-vault/`

## Relevant Files

- New frontend package under `frontend/`
- API client at `frontend/src/api/client.ts`
- React app and components under `frontend/src/`
- Documentation in `docs/51_minimal_demo_ui.md`
- Operational docs in `README.md`, `ROADMAP.md`, `Makefile`, and Obsidian

## Scope

- Create a Vite + React + TypeScript local UI.
- Add a JSON startup input editor with a load-example button.
- Call `GET /health`, `GET /rag/status`, `POST /brief`,
  `POST /brief/evaluate`, and `GET /demo/artifacts`.
- Render the generated Startup Action Brief, scorecards, gaps, NVIDIA
  technologies, evidence, warnings, uncertainties, RAG status, and optional
  answer quality evaluation.
- Add Makefile targets for installing, developing, building, and running the
  full local demo.
- Update project documentation and Obsidian notes.

## Out of Scope

- No authentication.
- No deploy.
- No new database.
- No design system.
- No API changes unless a truly minimal fix is needed.
- No changes to scoring, diagnosis, recommendation, `recommended_motion`,
  RAG retrieval, Qdrant ingestion, answer quality metrics, scraping, or LLM calls.

## Proposed Implementation

1. Scaffold `frontend/` with Vite, React, TypeScript, CSS, and env example.
2. Implement `frontend/src/api/client.ts` with typed helpers for the five API
   endpoints.
3. Implement local React state in `App`, parsing JSON input, loading the sample
   payload, submitting brief generation, evaluating the brief, and polling
   health/RAG/artifacts once on load.
4. Implement focused components: `StartupInputForm`, `RagStatusBadge`,
   `ScoreCards`, `GapTechnologyTable`, `EvidencePanel`, `BriefViewer`, and
   `EvalStatusPanel`.
5. Add Makefile targets: `ui-install`, `ui-dev`, `ui-build`, and `demo-full`.
6. Document how to run API + UI and record the demo UI decision in Obsidian.
7. Run `npm install`, `npm run build`, `pytest`, `ruff check .`,
   `black --check .`, and `mypy src`.

## Files to Create/Change

### Create

- `frontend/package.json` - frontend scripts and dependencies
- `frontend/index.html` - Vite entry page
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/tsconfig.node.json` - Vite config typing
- `frontend/vite.config.ts` - Vite React config
- `frontend/.env.example` - API base URL default
- `frontend/src/main.tsx` - React entry
- `frontend/src/App.tsx` - app orchestration
- `frontend/src/api/client.ts` - HTTP client
- `frontend/src/components/*.tsx` - UI components
- `frontend/src/sampleStartupInput.ts` - local fictional demo payload
- `frontend/src/styles.css` - simple local styles
- `docs/51_minimal_demo_ui.md` - design/usage doc
- `obsidian-vault/03 Research/Epic 26 Minimal Demo UI.md`
- `obsidian-vault/04 Decisions/Epic 26 Minimal Demo UI.md`

### Change

- `README.md` - UI run instructions and capability/limitation notes
- `ROADMAP.md` - Epic 26 status
- `Makefile` - UI targets
- `obsidian-vault/Known Limitations.md` - local UI limitations

## Tests/Validations

- `npm install` in `frontend/`
- `npm run build` in `frontend/`
- `pytest`
- `ruff check .`
- `black --check .`
- `mypy src`
- Manual smoke path: `make api-dev`, `make ui-dev`, load sample, generate brief,
  inspect RAG status, and run evaluation.

## Risks

| Risk | Mitigation |
|------|------------|
| API offline blocks the demo | UI shows a clear API offline error and keeps input intact |
| Qdrant offline looks like a failure | UI treats it as warning/status only |
| Pipeline is synchronous and slow | UI uses loading state and disables duplicate submit |
| Brief shape evolves | Types keep nested payloads permissive and optional |
| Frontend toolchain adds surface area | Use only Vite, React, TypeScript, no UI/test framework |

## Definition of Done

- [ ] UI runs locally.
- [ ] UI consumes the minimal API.
- [ ] UI generates and displays a brief.
- [ ] UI shows scorecards, gaps, evidence, warnings, uncertainties, and RAG status.
- [ ] UI allows optional brief evaluation.
- [ ] `npm run build` passes.
- [ ] Python validation commands pass or failures are reported.
- [ ] Docs and Obsidian are updated.

---

*Generated on: 2026-06-11*
*Mode: Plan -> Artifact -> Build -> Review -> Commit*

