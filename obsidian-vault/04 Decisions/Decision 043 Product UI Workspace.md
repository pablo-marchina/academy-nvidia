# Decision 043 — Product UI Workspace (Epic 37)

## Context
The project needed a first usable web UI consuming the Product API (readiness, capabilities, startup management, analysis execution, dossier visualization, opportunities table, review/quality). The existing demo UI was disconnected from the Product backend.

## Decision
- **Stack:** React 19 + Vite 7 + TypeScript 5.9 (confirmed by user, no new deps)
- **Routing:** State-based in `App.tsx` (no react-router-dom)
- **API Client:** Native `fetch` with typed wrappers (no TanStack Query)
- **No mock as main flow** — UI consumes real Product API
- **Edit startup:** Only name/sector/website (not a CRM)
- **E2E:** Separado (`make ui-e2e-product`), não no `make validate`

## Views (7)
1. Setup/Readiness — readiness status + blocking/optional config + checklist + progress
2. Capabilities — grouped by category with status badges
3. Startup List — table + create inline form
4. Startup Detail — detail + edit + run analysis
5. Analysis Run — scores, gaps, mappings, claims, readiness, quality, actions
6. Opportunities — ranked table with pagination
7. Dossier — Markdown + JSON raw + copy + regenerate

## Rationale
State-based routing simpler for 7 views. No dependency cost. Real API first avoids maintaining parallel mock logic.

## Status
Implementado no Epic 37. Build passou (0 erros, 0 warnings).
