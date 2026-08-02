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

The target repository should remain the architectural base. The highest-value reference capabilities were adapted into its existing frontend and CI rather than importing the reference stack.

## Adoption matrix

| Area | Reference advantage | Target baseline | Decision | Implementation / rationale |
|---|---|---|---|---|
| Aggregate dashboard | KPI cards, visual distributions, search, pagination, clearer empty/loading states | Basic table, raw runtime JSON, limited navigation | **Adopted and extended** | Rebuilt `RadarDashboardView` as a decision cockpit with KPIs, distributions, filters, sorting, pagination, tabs, skeleton loading, safe links, compact recommendations, and drill-down actions. |
| Frontend request reliability | `AbortController` timeouts and React Query cancellation | Direct `fetch` wrapper without timeout or concurrent-request reuse | **Adopted and hardened** | Added operation-aware timeouts, caller cancellation propagation, clear timeout/cancel errors, and in-flight GET deduplication in `frontend/src/api/client.ts`. |
| Frontend data caching | React Query cache and placeholder data | Component-local state | **Partially adopted** | Added safe in-flight GET deduplication without introducing a new state-management dependency. Persistent client caching was not added because stale runtime state would need endpoint-specific invalidation contracts. |
| Charts | Recharts-based visual summaries | No portfolio visualization | **Adapted without dependency** | Added accessible CSS distribution bars. This captures decision value while avoiding bundle growth and another dependency surface. |
| Recommendation portfolio | Dedicated page listing companies with recommendations | Recommendations accessible mainly inside company/run views | **Adopted through the Radar** | The Radar now exposes recommendation-ready counts, filtering, compact top recommendation, additional recommendation disclosure, and direct result navigation in one central decision table. |
| Structured recommendation output | Roadmap, quick wins, KPIs, pricing/competitive cards | Persisted activation recommendations, action brief, opportunity score, activation dossier, evidence bundle | **Target already stronger** | No parallel recommendation schema was added. Existing persisted artifacts are more auditable; the frontend now surfaces them more clearly. |
| Export / report output | PDF-oriented report generation | Persisted dossier/Markdown and export records | **Target already stronger** | No alternate report pipeline was imported. Output must continue to originate from persisted product records rather than a second report-generation path. |
| Competitive analysis | Big-tech comparison workflow and UI | NVIDIA fit, gap diagnosis, mapping, recommendation, scoring, dossier | **Not imported as-is** | Useful as a separate future product capability, but it is not required by the current NVIDIA startup-opportunity decision objective and would expand scope without evidence that it improves the case score. |
| NVIDIA catalog breadth | Static catalog describing roughly 53 services and many URLs | Governed source registry with provenance, sync lifecycle, freshness and version metadata | **Do not copy blindly** | New NVIDIA sources should enter through the existing source-sync and corpus lifecycle. A larger ungoverned static list could increase irrelevant retrieval and stale claims. |
| Retrieval | BGE-M3, BM25, fusion and Cohere reranking | Hybrid retrieval, GraphRAG/Qdrant paths, reranking controls and runtime technique registry | **Target already stronger or equivalent** | No second RAG path was introduced. Retrieval changes must improve the existing evaluation gates before activation. |
| RAG evaluation | RAGAS script with a small example set and external judge | Stricter offline retrieval tests and benchmark result storage | **Not copied** | The reference RAGAS implementation uses only a few examples and external model/embedding dependencies. The target evaluation is more suitable for CI, although its stale suite registry and current RAG quality failures require separate remediation. |
| RSS news discovery | Scheduled RSS collection with recency/keyword filters | Multi-source discovery and quantitative company gate | **Concept retained; code rejected** | Regex extraction from headlines can create false companies and duplicate identities. RSS should be integrated later as a governed discovery adapter whose candidates pass the existing company gate, not as a parallel ingestion path. |
| Scheduled updates | GitHub Actions scheduled discovery/enrichment | Runtime and CI workflows focused on product execution and evaluation | **Deferred** | Scheduling is valuable only after the active discovery adapters produce reliable candidates and secrets/configuration are defined. It should invoke the central pipeline, never duplicate it. |
| Repository hygiene | Conventional frontend build workflow | Strong backend governance, but no explicit tracked-runtime-artifact gate | **Adopted and strengthened** | Added a CI gate for caches, local databases, build output and generated runtime state, with an exact allowlist for deterministic lifecycle fixtures. Added the frontend production build to CI. |

## Implemented changes

### Decision output

- Correct recommendation-ready counting based on persisted status or generated recommendations.
- Portfolio KPIs for available, analyzed, recommendation-ready, evidence coverage and runtime attention.
- Portfolio-state and opportunity-score distributions.
- Search over company, sector, gaps, recommended motion and NVIDIA technologies.
- Status and sector filtering.
- Sorting by score, evidence coverage, source count and name.
- Compact, prioritized NVIDIA technologies and gaps.
- Top recommendation plus progressive disclosure for additional recommendations.
- Separate, readable views for discovery queue, blockers and rejected entities.
- Full raw payload retained behind expandable audit details.

### Frontend performance and resilience

- Client-side pagination avoids rendering the full portfolio table at once.
- Configurable page size and discovery source limit.
- In-flight GET deduplication prevents duplicate simultaneous reads of the same endpoint.
- Read requests time out after 30 seconds; write/pipeline operations receive a 10-minute budget.
- Caller-provided cancellation signals propagate correctly.
- No new frontend runtime dependency was added.

### CI and repository quality

- Frontend production build is mandatory in the main CI job.
- Generated/cache/local-state artifacts are rejected when tracked by Git.
- Deterministic corpus lifecycle fixtures are explicitly allowlisted rather than weakening the rule for whole directories.

## Validation status

- The `CI / product-governance` workflow passes the artifact gate, runtime governance gates, focused tests and frontend production build.
- The separate Offline Evaluation workflow currently exposes pre-existing evaluation debt:
  - RAG quality gates fail for critical top-1 retrieval, missing known-query contexts and excessive irrelevant results.
  - Six suites registered in `src/evaluation/eval_runner.py` point to test files that are absent from the repository.
- Those failures were not bypassed or converted into warnings. They are intentionally documented as a separate backend/evaluation remediation stream.

## Recommended next comparison-derived work

1. Repair the evaluation suite registry so every advertised suite maps to a real, maintained test set.
2. Improve the existing RAG until the current retrieval quality gates pass; do not replace the gates with the reference repository's smaller example set.
3. Add server-side Radar pagination/filtering when the active portfolio consistently exceeds the current 100-row retrieval limit.
4. Prototype RSS as a discovery adapter behind the existing identity validation and quantitative company gate, then retain it only if precision and incremental candidate yield beat current sources.
5. Add browser-level visual regression and interaction tests for the Radar decision workflow.
