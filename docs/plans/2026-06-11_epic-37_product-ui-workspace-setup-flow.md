# EPIC 37 — Product UI Workspace & Setup Flow

**Data:** 2026-06-11
**Status:** Aprovado
**Prioridade:** P0
**Dependências:** Epic 29 (Product Backend), Epic 30 (Product API), Epic 32 (Claim Ledger), Epic 33 (Activation Playbooks), Epic 34 (Dossier), Epic 36 (Structured Outputs), Epic 36.1 (Capability/Config Registry)

## Objetivo

Criar a primeira Product UI Workspace realmente utilizável, consumindo a Product API real, com foco em setup/readiness, capabilities, startup management, analysis run execution, opportunities, dossier/quality visualization.

## Stack

React 19 + Vite 7 + TypeScript 5.9. Fetch nativo. Estado local. CSS puro.

## Decisões Bloqueantes (resolvidas)

1. **Routing:** Estado local no App.tsx. Sem react-router-dom.
2. **Playwright E2E:** Alvo separado (`make ui-e2e-product`). Não incluído no `make validate`.
3. **Edição de startup:** Apenas campos básicos (name, sector, website).

## Fora de Escopo

- Auth/roles/PDF/editor/drag-drop/charts/MCP/TOON/JTON
- react-router-dom / TanStack Query
- Mock como fluxo principal
- Alterações em scoring, RAG, Qdrant, recommendation central
- Lógica de negócio duplicada no frontend

## Entregáveis

### Documentação
- `docs/plans/2026-06-11_epic-37_product-ui-workspace-setup-flow.md`
- `docs/64_product_ui_workspace.md`
- `README.md` atualizado
- `ROADMAP.md` atualizado
- `DECISIONS.md` atualizado
- `obsidian-vault/` nota curta

### Código Frontend
- `frontend/src/api/types.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/product.ts`
- `frontend/src/App.tsx` (reescrito)
- `frontend/src/styles.css` (estendido)
- Views: SetupReadiness, Capabilities, Startup list/create/edit/detail, AnalysisRun, Opportunities, Dossier, Quality, Review
- `frontend/.env.example` (VITE_APP_ENV opcional)

### Testes
- Playwright E2E smoke separado

## Views

| View | Componente | Endpoint(s) |
|---|---|---|
| Setup/Readiness | `SetupReadinessView` | `GET /product/readiness`, `/setup-checklist`, `/configuration` |
| Capabilities | `CapabilitiesView` | `GET /product/capabilities` |
| Startups | `StartupListView` + `CreateStartupForm` | `GET /startups`, `POST /startups` |
| Startup Detail | `StartupDetailPanel` + `EditStartupBasicForm` + `AnalysisRunPanel` | `GET /startups/{id}`, `PATCH /startups/{id}`, `POST /startups/{id}/analysis-runs` |
| Analysis Run | `AnalysisRunDetailView` | `GET /analysis-runs/{id}`, claims, activation-recommendations, quality-summary |
| Opportunities | `OpportunitiesView` | `GET /opportunities` |
| Dossier | `DossierView` | `GET /analysis-runs/{id}/dossier`, `/dossier/markdown` |
| Quality | `QualitySummaryPanel` (inline) | `GET /analysis-runs/{id}/quality-summary` |
| Review | `ReviewForm` (inline) | `POST /analysis-runs/{id}/review`, `PATCH .../claims/{id}/review` |

## Validação Final

- `npm run build` passa
- Backend: `pytest` (unit), `ruff`, `black`, `mypy`
- `python scripts/check_scope.py`
- `python scripts/check_docs_closure.py`
