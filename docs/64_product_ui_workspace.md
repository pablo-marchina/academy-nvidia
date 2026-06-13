# Product UI Workspace

**Épico:** 37
**Versão:** 1.0
**Data:** 2026-06-11

## Propósito

Expor todo o ecossistema do NVIDIA Startup AI Radar (Product Backend, Capability & Configuration Registry, Claim Ledger, Activation Playbooks, Dossier, Product Quality, Structured Outputs) através de uma interface web utilizável, consumindo a Product API real como única fonte de verdade.

## Stack

- React 19 + Vite 7 + TypeScript 5.9
- Fetch nativo (sem axios, sem TanStack Query)
- Estado local no App.tsx (sem react-router-dom)
- CSS puro (sem Tailwind, sem CSS-in-JS)
- Playwright para E2E smoke tests (alvo separado)

## Princípios

1. **Backend é a fonte da verdade** — UI não duplica lógica de negócio.
2. **Setup-first UX** — Antes de usar o produto, usuário vê readiness. Configuração bloqueante impede core flow. Configuração opcional não bloqueia.
3. **Sem mock como fluxo principal** — Toda tela consome API real. Dados indisponíveis mostram "Not available".
4. **Zero dependências novas** — Apenas React, Vite, TypeScript, Playwright (já existentes).

## Arquitetura

### Navegação

Estado local no `App.tsx`:

```typescript
type ActiveView = "setup" | "capabilities" | "startups" | "opportunities" | "analysisRun" | "dossier";
```

Views compartilham estado via props do App (selectedStartupId, selectedAnalysisRunId).

### API Client

```
frontend/src/api/
  types.ts     — tipos TypeScript alinhados aos schemas Pydantic
  client.ts    — fetch genérico com tratamento de erro
  product.ts   — funções para cada endpoint product
```

Padrão: função assíncrona que retorna tipo tipado ou lança erro user-visible.

### Data Fetching

Hook local `useApi<T>` em cada view:

```typescript
function useApi<T>(fetcher: () => Promise<T>, deps: unknown[]) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // useEffect + refresh
}
```

## Views

### SetupReadinessView

**Endpoint:** `GET /product/readiness`
**Endpoints auxiliares:** `GET /product/setup-checklist`, `GET /product/configuration`

**Exibe:**
- Ready true/false (badge grande)
- Se not ready: blocking_missing_config com ações (copiar env var, link README)
- Optional missing config com comando de instalação
- Unavailable/degraded capabilities
- Setup checklist com progress bar
- User messages

**Ações:**
- Refresh readiness
- Navegar para capabilities
- Se ready: CTA para ir ao workspace

### CapabilitiesView

**Endpoint:** `GET /product/capabilities`

**Exibe:**
- Capabilities agrupadas por categoria
- Status visual (available/unavailable/not_configured/missing_dependency/degraded/disabled/experimental)
- Para cada capability: descrição, env vars, extras, setup instructions

### StartupListView + CreateStartupForm

**Endpoint:** `GET /startups`, `POST /startups`

- Tabela de startups com nome, setor, website, status, última análise
- Botão "New Startup" abre formulário inline
- Formulário com: name (required), website (required), sector (required)
- Botão "View" navega para detalhe

### StartupDetailPanel

**Endpoint:** `GET /startups/{id}`, `PATCH /startups/{id}`

- Dados da startup + evidências
- Botão "Edit" abre inline edit de name/sector/website
- Botão "Run Analysis" inicia POST `/startups/{id}/analysis-runs`
- AnalysisRunPanel mostra status da execução

### AnalysisRunDetailView

**Endpoint:** `GET /analysis-runs/{id}`
**Auxiliares:** claims, activation-recommendations, quality-summary

Seções:
1. Metadata (status, timestamps, pipeline_version, degraded/error)
2. Scores (4 cards)
3. Gaps (tabela)
4. NVIDIA Mappings (tabela)
5. Readiness Checks
6. Claims + Evidence Coverage
7. Activation Recommendations
8. Quality Summary
9. Action Brief link
10. Dossier link

### OpportunitiesView

**Endpoint:** `GET /opportunities`

- Tabela com startup_name, composite_score, recommended_motion, top_activation_playbook, evidence_coverage, unsupported_claim_count, export_readiness_score, review_readiness_score, dossier_available
- Filtros: none no MVP (apenas paginação)

### DossierView

**Endpoint:** `GET /analysis-runs/{id}/dossier`, `GET /analysis-runs/{id}/dossier/markdown`

- Renderiza Markdown em bloco
- Botão "Copy Markdown"
- Toggle "View Raw JSON"
- Botão "Regenerate" (POST ?force=true)

### QualitySummaryPanel

**Endpoint:** `GET /analysis-runs/{id}/quality-summary`

- Overall status PASS/WARN/FAIL
- Métricas pass/fail com thresholds
- export_readiness_score, review_readiness_score
- degraded_reason

### ReviewForm

**Endpoint:** `POST /analysis-runs/{id}/review`, `GET /analysis-runs/{id}/reviews`

- Select de decisão + reviewer + notes
- Lista de reviews anteriores

## Rotas (lógicas)

| Path lógico | View |
|---|---|
| `/` | SetupReadinessView (se não ready) ou redireciona |
| `/setup` | SetupReadinessView |
| `/capabilities` | CapabilitiesView |
| `/startups` | StartupListView |
| `/startups/:id` | StartupDetailPanel |
| `/analysis-runs/:id` | AnalysisRunDetailView |
| `/analysis-runs/:id/dossier` | DossierView |
| `/opportunities` | OpportunitiesView |

## Configuração Frontend

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_ENV=development  # opcional
```

A UI usa `import.meta.env.VITE_API_BASE_URL`. Fallback `http://localhost:8000`.

## Testes

- `npm run build` — build TypeScript + Vite
- Playwright E2E smoke separado (`make ui-e2e-product`)
  - Teste 1: Readiness carrega e mostra status
  - Teste 2: Criar startup, rodar análise, ver resultado
- Backend tests inalterados

## Limitações

- Routing via estado local (sem URLs profundas/bookmarks)
- Sem TanStack Query (cache/refetch manual)
- Sem testes unitários de componente (sem Vitest/Jest no projeto)
- Dossier Markdown renderizado como texto pré-formatado (sem parser MD avançado)
