# Epic 44 — Product UI Hardening

## Decision: Consolidate to 10 Product Views Without Adding Intelligence

### Context
The product frontend had 7 views with gaps in the product story (no discovery, no workflow, no export delivery). Quality was embedded in Setup with no dedicated view.

### Decision
- Expand to 10 views: Setup, Capabilities, Discovery, Startups, Startup Detail, Analysis Run, Dossier, Opportunities, Workflow, Export Delivery, Quality
- No React Router — keep local state navigation in App.tsx
- Add 17 new API functions to product.ts (discovery, workflow, opportunity-score, export, quality)
- 6 new components, 5 enhanced components
- No new backend endpoints

### Rationale
- All needed endpoints already exist in backend — UI was the missing layer
- Local state navigation avoids adding a dependency (react-router-dom) for a linear flow
- Quality view separated from Setup to follow the product story

### Risks
- No frontend unit tests — only Playwright E2E smoke tests
- No deep-linking or browser back/forward support
