# Epic 44 — Final Product UI & Demo Flow Hardening

## Summary
Frontend-only epic that consolidated the product UI from 7 to 10 views, added missing views (Discovery, Workflow, Export, Quality), enhanced existing views with ranked data and warnings, and added 17 API functions.

## Views Added
- **DiscoveryView** — sources, runs, candidates with promote
- **WorkflowView** + **WorkflowNodeTimeline** — runs list, node timeline
- **ExportDeliveryView** — checklist, export commands, limitations
- **QualityView** — dedicated quality report
- **OpportunityDetailPanel** — detailed opportunity score

## Views Enhanced
- **OpportunitiesView** — All + Ranked tabs
- **DossierView** — warnings for low coverage / unsupported claims
- **SetupReadinessView** — Playwright binary note, quality link

## Key Files
- frontend/src/App.tsx — navigation state
- frontend/src/api/types.ts — all new TypeScript types
- frontend/src/api/product.ts — 17 new functions
- docs/71_product_ui_hardening_design.md

## Validation
- `npm run build` passes (tsc + vite)
- `pytest tests/acceptance/` passes (11/11)
- `ruff check .` passes
- `python scripts/check_scope.py` passes
- `python scripts/check_docs_closure.py` passes
