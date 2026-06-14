# End-to-End Product Acceptance

**Epic:** 38
**Versão:** 1.0
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

## Release Checklist

- [ ] DB migrated (`alembic upgrade head`)
- [ ] Readiness checked (`GET /product/readiness`)
- [ ] Capabilities visible (`GET /product/capabilities`)
- [ ] Required config complete
- [ ] Optional features documented
- [ ] Backend unit tests pass (`pytest -m "not integration"`)
- [ ] Backend acceptance tests pass (`pytest -m acceptance`)
- [ ] Frontend build passes (`npm run build`)
- [ ] Frontend lint passes (if configured)
- [ ] UI E2E smoke passes (`make ui-e2e-product` — separate target)
- [ ] No `data/demo_runs` dependency
- [ ] Dossier generated and retrievable
- [ ] Quality run generated
- [ ] Opportunities visible
- [ ] All 10 Product UI views functional (Setup, Capabilities, Discovery, Startups, Opportunities, Workflow, Export, Quality)
- [ ] Known limitations updated
- [ ] Documentation updated (README, ROADMAP, EVALS)

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
