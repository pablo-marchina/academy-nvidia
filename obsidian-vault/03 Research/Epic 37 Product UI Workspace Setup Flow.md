# Epic 37 — Product UI Workspace & Setup Flow

## Resumo
Primeira UI funcional do produto, consumindo a Product API real. Substitui a demo UI como entrada principal.

## Componentes criados (11)
- `SetupReadinessView` — readiness, configuração, checklist, progresso
- `CapabilitiesView` — capacidades agrupadas com badges de status
- `StartupListView` + `CreateStartupForm` — listar/criar startups
- `StartupDetailPanel` + `EditStartupBasicForm` — detalhe + edição + run analysis
- `AnalysisRunDetailView` — scores, gaps, mappings, claims, readiness, quality, actions
- `OpportunitiesView` — tabela ranqueada com paginação offset/limit
- `DossierView` — Markdown + JSON raw + copy + regenerate
- `QualitySummaryPanel` — métricas pass/fail com thresholds
- `ReviewForm` — submit + list reviews de analysis run

## Infra
- `api/types.ts` — ~30 interfaces TypeScript alinhadas aos schemas Pydantic
- `api/client.ts` — fetch genérico + tipos demo legados
- `api/product.ts` — funções para todos os endpoints product
- `App.tsx` — routing por estado local com navegação via abas
- `styles.css` — ~600 linhas de estilos da Product UI

## Decisões
- State-based routing (sem react-router-dom)
- Native fetch (sem TanStack Query)
- E2E separado do validate
- Backend não foi alterado (CORS já permissivo)

## Build
`npm run build` — 0 erros, 0 warnings (tsc + vite build)
