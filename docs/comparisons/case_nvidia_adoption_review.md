# Comparative adoption review: `caseNvidia` → `academy-nvidia`

**Reference repository:** `Lucas-Andrade-Silva/caseNvidia`  
**Target repository:** `pablo-marchina/academy-nvidia`  
**Review date:** 2026-08-02  
**Target branch:** `improve/dashboard-output-performance`

## Decision rule

A reference implementation is adopted only when it improves the target product while preserving these invariants:

1. one central production runtime pipeline;
2. persisted, auditable product artifacts;
3. no mock or fixture path presented as product output;
4. evidence-aware decisions and explicit degraded/blocked states;
5. no parallel architecture introduced only to reproduce a reference feature;
6. measurable improvement in decision utility, reliability, or runtime/UI cost.

The review therefore copies **capabilities and good design decisions**, not source code or architectural weaknesses.

## Executive conclusion

`academy-nvidia` is stronger in backend architecture, product persistence, corpus lifecycle governance, evidence controls, LangGraph runtime orchestration, scoring traceability, and final decision artifacts.

`caseNvidia` is stronger in aggregate presentation and interaction patterns: dashboard summaries, filtering, pagination, explicit UI feedback, request cancellation, progressive disclosure, and dedicated views for recommendation output.

The target repository remains the architectural base. The highest-value reference capabilities were adapted into its existing frontend, retrieval and CI paths rather than importing the reference stack or creating a second runtime.

## Adoption matrix

| Area | Reference advantage | Target baseline | Decision | Implementation / rationale |
|---|---|---|---|---|
| Aggregate dashboard | KPI cards, visual distributions, search, pagination, clearer empty/loading states | Basic table, raw runtime JSON, limited navigation | **Adopted and extended** | Rebuilt `RadarDashboardView` as a decision cockpit with KPIs, distributions, filters, sorting, pagination, tabs, skeleton loading, safe links, compact recommendations, and drill-down actions. |
| Frontend request reliability | `AbortController` timeouts and React Query cancellation | Direct `fetch` wrapper without timeout or concurrent-request reuse | **Adopted and hardened** | Added operation-aware timeouts, caller cancellation propagation, clear timeout/cancel errors, and in-flight GET deduplication in `frontend/src/api/client.ts`. |
| Frontend data caching | React Query cache and placeholder data | Component-local state | **Partially adopted** | Added safe in-flight GET deduplication without introducing a new state-management dependency. Persistent client caching was not added because stale runtime state requires endpoint-specific invalidation contracts. |
| Charts | Recharts-based visual summaries | No portfolio visualization | **Adapted without dependency** | Added accessible CSS distribution bars. This captures decision value while avoiding bundle growth and another dependency surface. |
| Recommendation portfolio | Dedicated page listing companies with recommendations | Recommendations accessible mainly inside company/run views | **Adopted through the Radar** | The Radar now exposes recommendation-ready counts, filtering, compact top recommendation, additional recommendation disclosure, and direct result navigation in one central decision table. |
| Structured recommendation output | Roadmap, quick wins, KPIs, pricing/competitive cards | Persisted activation recommendations, action brief, opportunity score, activation dossier, evidence bundle | **Target already stronger** | No parallel recommendation schema was added. Existing persisted artifacts are more auditable; the frontend now surfaces them more clearly. |
| Export / report output | PDF-oriented report generation | Persisted dossier/Markdown and export records | **Target already stronger** | No alternate report pipeline was imported. Output continues to originate from persisted product records rather than a second report-generation path. |
| Competitive analysis | Big-tech comparison workflow and UI | NVIDIA fit, gap diagnosis, mapping, recommendation, scoring, dossier | **Not imported as-is** | Useful as a possible separate product capability, but it is outside the current NVIDIA startup-opportunity decision objective and would expand scope without demonstrated case-value gain. |
| NVIDIA catalog breadth | Larger static catalog | Governed source registry with provenance, sync lifecycle, freshness and version metadata | **Do not copy blindly** | New NVIDIA sources must enter through the existing source-sync and corpus lifecycle. A larger ungoverned list can increase irrelevant retrieval and stale claims. |
| Retrieval | BGE-M3, BM25, fusion and Cohere reranking | Hybrid retrieval, GraphRAG/Qdrant paths, reranking controls and runtime technique registry | **Target retained and improved** | Improved the active lexical path: exact technology intent, gap/technology intersection, source diversity, taxonomy expansion, HTML cleaning and bounded chunking. No second RAG path was introduced. |
| RAG evaluation | Small RAGAS example set and external judge | Offline quality gates and benchmark result storage | **Target retained and repaired** | Fixed stale suite paths, added per-query diagnostics, separated mandatory coverage from additional valid sources, aligned the golden set with the governed corpus, and kept all gates strict. |
| RSS news discovery | Scheduled RSS collection with recency/keyword filters | Multi-source discovery and quantitative company gate | **Concept retained; code rejected** | Regex extraction from headlines can create false companies and duplicate identities. RSS should only be added later as a governed adapter whose candidates pass the existing company gate. |
| Scheduled updates | GitHub Actions scheduled discovery/enrichment | Runtime and CI workflows focused on product execution and evaluation | **Deferred** | Scheduling is valuable only when it invokes the central pipeline with reliable active adapters; it must never duplicate the runtime. |
| Repository hygiene | Conventional frontend build workflow | Strong backend governance, but no explicit tracked-runtime-artifact gate | **Adopted and strengthened** | Added a CI gate for caches, local databases, build output and generated runtime state, with an exact allowlist for deterministic lifecycle fixtures. Added the frontend production build to CI. |

## Implemented changes

### Decision output and frontend

- Correct recommendation-ready counting based on persisted status or generated recommendations.
- Portfolio KPIs for available, analyzed, recommendation-ready, evidence coverage and runtime attention.
- Portfolio-state and opportunity-score distributions.
- Search over company, sector, gaps, recommended motion and NVIDIA technologies.
- Status/sector filters and sorting by score, evidence, sources or name.
- Client-side pagination, configurable rows and configurable discovery source limit.
- Compact technologies, gaps and recommendations with progressive audit disclosure.
- Separate readable views for discovery queue, blockers and rejected entities.
- Safe external links, direct startup/result navigation, responsive layout and accessible loading/focus states.

### Frontend performance and resilience

- In-flight GET deduplication prevents duplicate simultaneous reads.
- Read requests time out after 30 seconds; write/pipeline operations receive a 10-minute budget.
- Caller-provided cancellation signals propagate correctly.
- No new frontend runtime dependency was added.

### RAG output quality and performance

- HTML saved in corpus files is cleaned before indexing; scripts, styles and navigation noise are excluded.
- Unstructured documents are bounded to at most five chunks without discarding tail content.
- Gap + technology queries use intersection semantics.
- Exact product matches outrank incidental mentions in other product pages.
- Broad queries diversify results across sources instead of letting one long document consume the result budget.
- Keyword retrieval uses governed source taxonomy when clean page text uses narrower vocabulary.
- Golden evaluation distinguishes mandatory sources from additional relevant governed sources.
- Every offline run emits per-query source/rank/score diagnostics.

### CI and repository quality

- Frontend production build is mandatory in the main CI job.
- Generated/cache/local-state artifacts are rejected when tracked by Git.
- Deterministic corpus lifecycle fixtures are explicitly allowlisted.
- Offline evaluation no longer launches unused PostgreSQL/Qdrant services or installs optional GPU/RAGAS stacks for deterministic suites.
- Workflow concurrency cancels superseded runs and Python/npm caches are enabled.

## Validation status

Both required workflows pass on commit `362e131baa0de038f355ee5cdbafa085cfd7465d`:

- **CI / product-governance:** artifact gate, single-runtime/no-mock gates, focused backend tests, new RAG ingestion/retrieval tests and frontend production build all pass.
- **Offline Evaluation:** 326 tests pass across RAG retrieval (48), answer quality (9), gap diagnosis (74), scraping (25), source/evidence calibration (58), recommendation calibration (72) and RAGAS metric logic (40).
- RAG gates pass for critical hit/top-1, zero missing mandatory contexts, provenance and irrelevant-context limit.
- Per-query diagnostics are uploaded as a workflow artifact for future regressions.

## Remaining opportunities outside this PR

1. Add server-side Radar pagination/filtering when the active portfolio consistently exceeds the current 100-row read limit.
2. Add browser-level visual regression and interaction tests for the Radar decision workflow.
3. Prototype RSS only behind the existing identity validation and quantitative company gate, and retain it only if precision and incremental candidate yield improve.
4. Remove the remaining deprecated mock-embedding imports in older evaluation/pipeline modules.
