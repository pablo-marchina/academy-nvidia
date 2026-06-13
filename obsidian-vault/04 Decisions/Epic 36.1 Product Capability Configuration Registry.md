# Epic 36.1 — Product Capability & Configuration Registry

**Decision:** Create capability registry (25+ capabilities) and configuration registry (17+ env vars) with ProductReadinessService and 4 API endpoints.

**Context:** The product had no central registry for what features exist, which are enabled/configured, what env vars are required, what optional deps are missing, or whether the product is ready to use.

**Rationale:** No-DB design keeps it simple — env vars + importlib are sufficient for v1. Per-call computation guarantees status is always current.

**Key components:**
- `src/services/product/capability_registry.py` — 25+ capability definitions
- `src/services/product/config_registry.py` — 17+ config items
- `src/services/product/readiness_service.py` — Readiness aggregation service
- 4 API endpoints: `GET /product/capabilities`, `/configuration`, `/setup-checklist`, `/readiness`
- 5 new Pydantic schemas in `src/api/product_schemas.py`

**Status:** Implementado.

**Related:** Decision 042 in DECISIONS.md
