# Product UI Hardening Design (Epic 44)

## Goal

Consolidate the product frontend into 10 complete views that tell the full product story: discovery → analysis → scoring → dossier → workflow → export. No new intelligence, no new backend endpoints, no React Router.

## Design Principles

1. **No new API endpoints** — all endpoints already exist in `src/api/product_routes.py` and `src/api/workflow_routes.py`.
2. **Local state navigation** — App.tsx uses `useState<ActiveView>` instead of React Router.
3. **Graceful empty/error states** — every view handles loading/error/empty consistently.
4. **Backward compatible** — existing views (Setup, Capabilities, Startups, StartupDetail, AnalysisRun, Dossier) remain unchanged.
5. **Product story** — the nav flow tells the narrative: Setup → Capabilities → Discovery → Startups → Analysis → Opportunities → Workflow → Export.

## View Architecture

```
App.tsx (state machine)
├── Setup (enhanced: Playwright note, Quality link)
├── Capabilities (unchanged)
├── Discovery (new)
├── Startups (unchanged)
├── StartupDetail (unchanged)
├── AnalysisRun (unchanged)
├── Dossier (enhanced: warnings)
├── Opportunities (enhanced: All + Ranked tabs)
├── Workflow (new)
├── ExportDelivery (new)
└── Quality (new, separate from Setup)
```

## Data Flow

- All components call `requestJson` via `frontend/src/api/product.ts`
- No local storage, no state sharing between views
- Navigation callbacks (selectStartup, selectRun, promoteToStartup) update App.tsx state and switch view

## New API Functions (17 total)

### Discovery (7)
- `listDiscoverySources()` → GET /discovery/sources
- `discoverManualSeed(body)` → POST /discovery/manual-seed
- `discoverUrlList(body)` → POST /discovery/url-list
- `listDiscoveryRuns(offset, limit, status)` → GET /discovery/runs
- `getDiscoveryRun(runId)` → GET /discovery/runs/{id}
- `listDiscoveryCandidates(offset, limit, params)` → GET /discovery/candidates
- `getDiscoveryCandidate(candidateId)` → GET /discovery/candidates/{id}
- `promoteDiscoveryCandidate(candidateId)` → POST /discovery/candidates/{id}/promote

### Workflow (5)
- `createWorkflowRun(body)` → POST /workflows/product-runs
- `listWorkflowRuns(offset, limit, status, startupId)` → GET /workflows/product-runs
- `getWorkflowRun(workflowId)` → GET /workflows/product-runs/{id}
- `listWorkflowNodeRuns(workflowId, offset, limit)` → GET /workflows/product-runs/{id}/nodes
- `getWorkflowForAnalysisRun(analysisRunId)` → GET /analysis-runs/{id}/workflow

### Opportunity Score (3)
- `getOpportunityScore(analysisRunId)` → GET /analysis-runs/{id}/opportunity-score
- `computeOpportunityScore(analysisRunId)` → POST /analysis-runs/{id}/opportunity-score
- `listRankedOpportunities(offset, limit, filters)` → GET /opportunities/ranked

### Export (2)
- `createExport(analysisRunId, exportType)` → POST /analysis-runs/{id}/exports
- `getExport(exportId)` → GET /exports/{id}

### Quality (1)
- `getQualityReport()` → GET /product/quality-report

## Testing Strategy

- Build validation: `npm run build` (tsc + vite)
- Acceptance: `pytest tests/acceptance/` (unchanged)
- E2E: `npx playwright test` (existing 6 tests cover main flow; new discovery/workflow/export views would need future expansion)

## Known Limitations

- No React Router (no deep-linking)
- Discovery candidates limited to first 100
- Workflow view is read-only
- Export view provides commands, not direct execution
- No frontend unit tests
