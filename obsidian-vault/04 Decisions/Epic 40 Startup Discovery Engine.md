# Epic 40 — Startup Discovery Engine

**Decision:** Build multi-source startup discovery engine with manual seed and URL list importers, AI-native signal detection, dedup, and promotion to Startup records.

**Context:** The product needed a way to identify AI-native Brazilian startups from multiple sources (manual lists, URL lists, accelerators, incubators) without scraping agressivo. Discovery results must feed into the existing pipeline flow (Startup -> AnalysisRun -> Claims -> Playbook -> Dossier -> Quality -> Opportunities).

**Rationale:** Source-agnostic design lets us start with manual seed (zero external dependencies) and add automated sources later. Signal detection is keyword-based (no LLM, no API cost). Dedup by normalized_name + domain prevents duplicate Startups.

**Key components:**
- `src/config/discovery_sources.json` — 6 source definitions
- `src/discovery/source_registry.py` — loader with cache
- `src/discovery/signals.py` — 30+ keyword patterns, confidence calc
- `src/discovery/dedup.py` — normalize_name, extract_domain, dedup checks
- `src/repositories/discovery.py` — DiscoveryRun + Candidate CRUD
- `src/discovery/service.py` — manual seed, URL list, promote, dedup
- `src/api/product_routes.py` — 9 discovery endpoints

**Status:** Implementado.

**Related:** Decision 046 (this decision in DECISIONS.md)
