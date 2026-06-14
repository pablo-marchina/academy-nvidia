# End-to-End Product Acceptance

**Epic:** 38 (atualizado Epic 45)
**Versão:** 1.1
**Data:** 2026-06-13

## Propósito

Validar que o NVIDIA Startup AI Radar funciona ponta a ponta como uma solução utilizável, do setup até a geração de dossier, quality run e oportunidades. Este documento define:

- Product Golden Path (fluxo principal de aceitação)
- Fixture de aceitação
- Backend acceptance tests
- Frontend smoke e E2E checks
- Release checklist

## Product Golden Path

### Fluxo

1. **Setup** — `GET /product/readiness` retorna `ready=true`
2. **Capabilities** — `GET /product/capabilities` retorna >= 25 capabilities
3. **Create startup** — `POST /startups` com fixture golden → 201
4. **List startups** — `GET /startups` inclui a nova startup
5. **Patch startup** — `PATCH /startups/{id}` altera setor → 200
6. **Create analysis run** — `POST /startups/{id}/analysis-runs` → 201
7. **Get analysis run** — `GET /analysis-runs/{id}` → scores, gaps, mappings
8. **Get claims** — `GET /analysis-runs/{id}/claims` → total > 0
9. **Get evidence coverage** — `GET /analysis-runs/{id}/evidence-coverage` → summary
10. **Generate activation recommendations** — `POST .../activation-recommendations/generate` → 201
11. **List activation recommendations** — `GET .../activation-recommendations` → items > 0
12. **Create dossier** — `POST /analysis-runs/{id}/dossier` → 201, version 1
13. **Get dossier** — `GET /analysis-runs/{id}/dossier` → 200, is_latest
14. **Create quality run** — `POST /analysis-runs/{id}/quality-runs` → 201, metrics > 0
15. **Get quality summary** — `GET /analysis-runs/{id}/quality-summary` → overall_status
16. **List opportunities** — `GET /opportunities` → items > 0
17. **Create export** — `POST /analysis-runs/{id}/exports` → 201, completed

### Invariantes

- Nenhum step depende de `data/demo_runs`
- Optional services ausentes (Qdrant, RAG) geram degraded state, não crash
- Dossier é gerado deterministicamente sem LLM
- Quality run não bloqueia core flow

## Playwright Policy

(Added in Epic 45)

1. **Playwright E2E is separate** from core validation targets.
2. **Browser binaries are not installed automatically** — manual command: `npx playwright install`.
3. **Playwright does not block `make validate`** — absence of browsers never breaks `validate-fast`.
4. **`make ui-e2e-product` is extra evidence**, not a delivery gate.
5. If browsers are unavailable, E2E tests are skipped gracefully.

## Sample Input Policy

(Added in Epic 45)

1. **Sample inputs are controlled test/demo data only** — never used as automatic fallback.
2. **Samples are NOT stored in `data/demo_runs/`** (directory removed in Epic 31).
3. **Approved locations:** `sample_inputs/` (manual demo), `tests/fixtures/` (automated tests), `docs/examples/` (documentation).
4. **The product flow uses DB/API real** — samples are never loaded automatically.
5. See `sample_inputs/README.md` for full documentation.

## Release Checklist

### Preparation
- [ ] Backend env configured (`cp .env.example .env`)
- [ ] DB migrations applied (`alembic upgrade head`)
- [ ] Product readiness checked (`GET /product/readiness` → `ready=true`)

### Validation
- [ ] Backend tests passed (`make validate-fast`)
- [ ] Frontend build passed (`make validate-frontend`)
- [ ] Docs closure passed (`make validate-docs`)
- [ ] Scope check passed (`python scripts/check_scope.py`)
- [ ] Acceptance path executed (`make acceptance`)

### Evidence
- [ ] No `data/demo_runs` dependency (`python scripts/check_no_demo_dependency.py`)
- [ ] Known limitations updated (see README)
- [ ] Screenshots captured (see `docs/screenshots/INSTRUCTIONS.md`)
- [ ] Demo script reviewed (see README — Demo Script section)
- [ ] Final evaluation report updated (`docs/74_final_evaluation_report.md`)
- [ ] Architecture summary updated (`docs/73_final_architecture_summary.md`)

### Optional (non-blocking)
- [ ] E2E smoke tests passed (`make ui-e2e-product`)
- [ ] Full pre-release gate (`make prepare-release`)
- [ ] Obsidian vault backfill

## Known Limitations

### Optional features
- **RAG** — requires `pip install -e ".[rag]"` and `RAG_EMBEDDING_MODEL` config. Analysis runs with `use_rag=true` without config will be degraded.
- **Qdrant** — requires Docker + `QDRANT_URL`. Falls back to in-memory vector store.
- **LLM Judge / Instructor** — requires `pip install -e ".[llm-judge]"` + `ENABLE_INSTRUCTOR_TRIAL=true`. Not configured by default.

### Not implemented
- Authentication / authorization
- PDF export
- MCP protocol
- TOON/JTON structured output formats
- Multi-tenancy
- CI matrix for Windows/macOS
- Cross-encoder reranking
- Crawler-based NVIDIA corpus ingestion

### Experimental
- Product UI is v1 — state-based routing, no react-router-dom, no TanStack Query, vanilla CSS, no frontend unit tests
- 10 views consolidated (Setup, Capabilities, Discovery, Startups, Opportunities, Workflow, Export, Quality) — no React Router
- Discovery view is read-only for candidates (promote creates startup); workflow view is read-only (no create from UI)
- Structured Output Reliability Layer (Epic 36) — Instructor trial optional

### Acceptance test limitations
- Acceptance tests use SQLite (not PostgreSQL) by default
- Integration tests with Qdrant are marked skippable
- Playwright E2E requires backend running (webServer configured in playwright.config.ts)
