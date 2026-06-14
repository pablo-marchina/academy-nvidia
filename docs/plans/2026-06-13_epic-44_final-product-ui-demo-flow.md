# Epic 44 — Final Product UI & Demo Flow Hardening

## Objective
Consolidate 10 product views, demo flow, and documentation for NVIDIA Startup AI Radar without adding new intelligence.

## Context Read
- `docs/64_product_ui_workspace.md` — current UI architecture, stack, views, API client design
- `docs/plans/2026-06-13_epic-43_opportunity-score-pipeline-ranking.md` — plan template style
- `frontend/src/App.tsx` — current navigation with 7 views and local state
- `frontend/src/api/types.ts` — existing TypeScript types
- `frontend/src/api/product.ts` — existing API functions
- `tests/fixtures/product_golden_path/startup.json` — test fixture for data

## Relevant Files

### Create (7)
- `frontend/src/components/QualityView.tsx`
- `frontend/src/components/DiscoveryView.tsx`
- `frontend/src/components/WorkflowView.tsx`
- `frontend/src/components/WorkflowNodeTimeline.tsx`
- `frontend/src/components/ExportDeliveryView.tsx`
- `frontend/src/components/OpportunityDetailPanel.tsx`
- `docs/71_product_ui_hardening_design.md`

### Modify (7)
- `frontend/src/api/types.ts` — add DiscoveryRun, WorkflowRun, WorkflowNode, RankedOpportunity, ExportPayload, ExportResult, DiscoveryCandidate
- `frontend/src/api/product.ts` — add 12+ API functions for discovery, workflow, opportunity-score, export, quality
- `frontend/src/App.tsx` — navigation for 10 views, additional state
- `frontend/src/components/OpportunitiesView.tsx` — ranked data support
- `frontend/src/components/DossierView.tsx` — warnings for missing evidence
- `frontend/src/components/SetupReadinessView.tsx` — Playwright binary note

## Scope
- 10 product views functional with navigation (Setup, Capabilities, Discovery, Startups, Startup Detail, Analysis Run, Dossier, Opportunities, Workflow, Export Delivery, Quality)
- New components for Discovery, Workflow, Export Delivery, Quality, Opportunity Detail
- API client expansion for 5 new endpoint groups
- Documentation: design doc for hardening decisions
- Graceful handling of empty/error/501 states
- Backend is already complete — no backend changes

## Out of Scope
- No new intelligence, scoring, RAG, Discovery, LangGraph changes
- No MCP, TOON/JTON, auth/roles, PDF export
- No React Router (keep local state in App.tsx)
- No data/demo_runs dependency — use existing test fixture
- No hiding limitations
- No Playwright E2E in validate-fast (separate target)
- No Vitest/Jest/component tests

## Proposed Implementation

1. **Types** — `frontend/src/api/types.ts`: add DiscoveryRun, DiscoveryCandidate, WorkflowRun, WorkflowNode, RankedOpportunity, ExportPayload, ExportResult interfaces
2. **API client** — `frontend/src/api/product.ts`: add functions for discovery (start/status/results/promote), workflow (create/get/nodes/retry), opportunity-score (ranked/detail), export (action-brief/download), quality (report)
3. **QualityView** — `frontend/src/components/QualityView.tsx`: dedicated view for quality report, separated from Setup
4. **DiscoveryView** — `frontend/src/components/DiscoveryView.tsx`: discovery runs list, candidates list, filters, promote to startup
5. **WorkflowView + WorkflowNodeTimeline** — `frontend/src/components/WorkflowView.tsx` + `WorkflowNodeTimeline.tsx`: create run, node timeline (read-only), retry
6. **ExportDeliveryView** — `frontend/src/components/ExportDeliveryView.tsx`: checklist, copy commands, download, limitations
7. **OpportunityDetailPanel** — `frontend/src/components/OpportunityDetailPanel.tsx`: detail panel for ranked opportunities
8. **OpportunitiesView enhancement** — `frontend/src/components/OpportunitiesView.tsx`: ranked data columns, link to detail panel
9. **DossierView enhancement** — `frontend/src/components/DossierView.tsx`: warnings for missing evidence / degraded quality
10. **SetupReadinessView enhancement** — `frontend/src/components/SetupReadinessView.tsx`: Playwright browser binary note
11. **App.tsx navigation** — `frontend/src/App.tsx`: expand ActiveView type, add routes/state for 10 views
12. **Design doc** — `docs/71_product_ui_hardening_design.md`: document hardening decisions
13. **Validation** — run full validation suite

## Tests/Validations
- `npm run lint` — no errors
- `npm run typecheck` — no errors
- `npm run build` — no errors
- `pytest tests/acceptance` — passes
- `npx playwright test` — passes
- `python scripts/check_scope.py` — passes
- `python scripts/check_docs_closure.py` — passes

## Risks

| Risk | Mitigation |
|------|-----------|
| Playwright E2E may fail if webServer is slow | Increase timeout in playwright config |
| Backend endpoint may return 501 for discovery/workflow if deps missing | Graceful UI for 501 with user-friendly message |
| CSS conflicts with new components | Reuse existing CSS classes from current components |

## Definition of Done

- [x] 10 views functional with navigation
- [x] All new components created
- [x] No new intelligence added
- [x] No backend changes needed
- [x] Backward compatible — existing views unchanged
- [x] Lint/typecheck/build pass
- [x] Acceptance tests pass
- [x] E2E tests pass
- [x] Documentation updated

## End-of-Epic Closure Checklist

- [ ] `pytest` passa sem erros.
- [ ] `ruff check .` passa sem erros.
- [ ] `black --check .` passa sem erros.
- [ ] `mypy src` passa sem erros.
- [ ] `README.md` atualizado com Current Capabilities e Known Limitations.
- [ ] `ROADMAP.md` atualizado com status real do épico.
- [ ] `DECISIONS.md` atualizado com decisoes arquiteturais do épico.
- [ ] `EVALS.md` atualizado com baseline de testes e cobertura.
- [ ] `ERROR_LOG.md` revisado e atualizado se houve erros.
- [ ] `docs/` — documentacao relevante atualizada ou criada.
- [ ] `obsidian-vault/` — backfill realizado (decisao, resumo, limitações).
- [ ] Nenhuma dependencia nova foi adicionada sem justificativa.
- [ ] Nenhuma feature fantasma foi documentada.

---

*Gerado em: 2026-06-13*
*Modo: Plan → Artifact → Build → Review → Commit*
