# Final Product Backlog - Documentation Mining

**Epic:** 28 - Documentation Mining & Final Product Backlog Consolidation  
**Date:** 2026-06-11  
**Mode:** Documentation and audit only. No functional code changes.

## 1. Executive Summary

The project has a strong deterministic analysis core: extraction, evidence
validation, AI-native classification, scoring, gap diagnosis, NVIDIA mapping,
recommendation, Action Brief generation, Product RAG, quality gates, and local
demo surfaces. The main product gap is not analytical logic; it is product mode.

Today the usable flow is still demo-shaped: CLI and API accept one startup at a
time, generate embedded or local files, default to samples/offline paths, and do
not persist startups, analysis runs, evidence, scores, gaps, mappings, briefs,
reviews, or exports as durable entities. The final product should promote the
implemented pipeline into a persisted, auditable opportunity intelligence
system.

Immediate recommendation: run a new technical epic for Product Backend
Foundation: persistence model, product API contracts, run lifecycle, explicit
dependency health/degraded states, and removal of demo endpoints from the main
product path.

## 2. Product Direction

All future work should optimize for a final product ready for use, not for a
demo path. Demo assets may remain only when they serve as fixtures, golden
datasets, smoke tests, or minimal usage examples.

Product mode means:

- Startups are persisted entities.
- Analysis runs are persisted, traceable, and repeatable.
- Evidence, scores, gaps, NVIDIA mappings, Action Briefs, reviews, exports, and
  readiness checks are stored as first-class records.
- UI and API operate on real product entities, not a fixed local sample.
- Qdrant and Postgres are configured dependencies with explicit health and
  degraded states.
- Fallbacks are visible and auditable, not hidden product behavior.
- Documentation is live, consolidated, and minimal.

## 3. Current Implemented Capabilities

- Deterministic pipeline in `src/pipeline/run_pipeline.py` integrating
  extraction, classification, evidence validation, scoring, gap diagnosis,
  NVIDIA mapping, recommendation, output consolidation, and optional RAG.
- Structured Action Brief generation in `src/briefing/` with Markdown and JSON
  output, evidence, missing evidence, uncertainties, NVIDIA context, and
  recommendation traceability.
- Product RAG core in `src/rag/` with corpus ingestion, lexical/semantic/hybrid
  retrieval, deterministic reranking, context packing, lifecycle filtering, and
  optional Qdrant adapter.
- Evaluation and quality layers in `src/evaluation/`, `tests/evals/`, and
  `scripts/build_regression_dashboard.py`.
- Local FastAPI demo API in `src/api/`, CLI demo in
  `scripts/run_startup_radar_demo.py`, and Vite/React demo UI in `frontend/`.
- Development governance through `AGENTS.md`, contracts in `docs/contracts/`,
  validation scripts, scope checks, and documented closure rules.

## 4. Product Gaps

- No persisted product entities for startups, evidence, analysis runs, scores,
  gaps, mappings, Action Briefs, reviews, exports, or readiness checks.
- API routes are demo-shaped (`/brief`, `/brief/evaluate`, `/demo/artifacts`)
  instead of product-shaped startup/run/review/export endpoints.
- UI is oriented around a fixed sample JSON and direct brief generation, not a
  persisted workflow over real startups and analysis history.
- No authentication, authorization, user roles, product deployment story, or
  production operational model.
- No human review/status workflow, despite review/status being required for a
  real decision process.
- Qdrant and Postgres are present in dependencies/config, but Postgres is not
  connected to the product flow and Qdrant is treated as optional/local in the
  main demo path.
- Local reports and demo outputs are useful for development but are not durable
  product records.

## 5. Demo-like or Fragile Areas

- `examples/demo/sample_startup_input.json` and
  `frontend/src/sampleStartupInput.ts` are useful fixtures but cannot remain the
  main product input.
- `data/demo_runs/latest/` stores generated outputs as local files; product mode
  needs versioned Action Brief records and export records.
- `GET /demo/artifacts` exposes demo run files; product mode needs
  `GET /exports/{id}` or equivalent.
- `POST /brief` and `POST /brief/evaluate` operate directly on request payloads;
  product mode needs startup and analysis-run resources.
- `offline` and local mock paths are excellent for tests but should be explicit
  test/dev modes, not the default product behavior.
- Regression dashboards and ingestion reports are development/ops artifacts;
  product dashboards must read product records and quality states.

## 6. Superseded / Contradictory Docs

| Document | Old statement | Current observed state | Decision | Required correction | Priority |
|---|---|---|---|---|---|
| `README.md` | "Gap Diagnosis module exists but is not yet called by the pipeline" | `src/pipeline/run_pipeline.py` calls `diagnose_gaps()`, builds NVIDIA mappings, and calls `build_recommendations()` | Correct live doc | Remove stale limitation and state that Gap Diagnosis and Recommendation are integrated | P0 |
| `obsidian-vault/02 Project Control/Known Limitations.md` | "Gap Diagnosis existe mas nao esta integrado ao pipeline" and "NVIDIA Mapping existe mas nao esta integrado ao pipeline" | Pipeline includes both as normal steps | Archive/correct later | Do not use this note as current truth; update during documentation pruning | P1 |
| `obsidian-vault/02 Project Control/Known Limitations.md` | "Sem Docker Compose" and "Sem CI/CD" | `docker-compose.yml` and CI/validation docs exist | Archive/correct later | Treat as historical/stale limitation note | P2 |
| `README.md` | "Vector store is in-memory only" | `src/rag/qdrant_store.py` implements optional QdrantStore and `docker-compose.yml` includes Qdrant | Correct live doc | Reword to "in-memory default; Qdrant adapter available" | P1 |
| `docs/35_product_rag_design.md` | Limitations include no reranking, no automated crawling, simple keyword scoring | Later docs and code add reranking/context packing, source sync, semantic/hybrid retrieval | Superseded by later docs/contracts | Mark as historical design unless merged into RAG contract | P2 |
| `docs/26_architecture_utilization_audit.md` | Recommends integrating gap diagnosis after recommendation is ready | Epic 9.1 integrated diagnosis and recommendation into pipeline | Archive history | Preserve as audit history, not active backlog | P2 |

## 7. Consolidated Product Backlog

In the `Origem` column, the first path is the primary origin and any remaining
paths are additional origins used for consolidation.

### P0 - Required for a Usable Product

| ID | Item | Origem | Categoria | Decisao | Prioridade | Dependencias | Risco se ignorado | Proximo menor passo |
|---|---|---|---|---|---|---|---|---|
| FPB-001 | Product persistence model | `pyproject.toml`, `.env.example`, `docker-compose.yml`, `src/database/` | PRODUCT_BACKLOG | IMPLEMENT | P0 | Postgres/SQLAlchemy, existing Pydantic schemas | Product remains a stateless demo with no history or audit trail | Define SQLAlchemy/Pydantic contracts for Startup, Evidence, AnalysisRun, scores, gaps, mappings, briefs, reviews, exports |
| FPB-002 | Product API resource model | `src/api/routes.py`, `docs/50_minimal_fastapi_demo_api.md` | REPLACE | REPLACE | P0 | FPB-001 | Integrators depend on `/brief` demo payloads instead of stable product resources | Draft API contract for `/startups`, `/analysis-runs`, `/opportunities`, `/exports` |
| FPB-003 | Persisted analysis run lifecycle | `src/pipeline/run_pipeline.py`, `docs/contracts/pipeline_output_contract.md` | PRODUCT_BACKLOG | IMPLEMENT | P0 | FPB-001, FPB-002 | Runs cannot be reproduced, compared, reviewed, or audited | Add run states and persisted input/output envelope to product backlog/API contract |
| FPB-004 | Evidence preservation as product record | `docs/14_evidence_policy.md`, `docs/contracts/evidence_contract.md`, `src/validation/` | PRODUCT_BACKLOG | IMPLEMENT | P0 | FPB-001 | Startup claims lose traceability after request time | Model StartupEvidence with source URL, quote, kind, confidence, collected_at, and validation status |
| FPB-005 | Versioned Action Brief records | `src/briefing/`, `docs/16_briefing_template.md`, `docs/contracts/briefing_contract.md` | PRODUCT_BACKLOG | IMPLEMENT | P0 | FPB-001, FPB-003 | Briefs remain transient Markdown/JSON, not auditable deliverables | Define ActionBriefRecord linked to AnalysisRun with schema version and rendered artifacts |
| FPB-006 | Explicit degraded dependency state | `src/api/service.py`, `src/rag/qdrant_store.py`, `README.md` | IMPLEMENTED_NEEDS_HARDENING | HARDEN | P0 | Qdrant/Postgres health checks | Hidden fallback can mask missing RAG/persistence and produce misleading product confidence | Define health/degraded semantics and warnings for Qdrant, corpus, DB, and optional embedding provider |
| FPB-007 | Product documentation source of truth | `docs/`, `docs/plans/`, `obsidian-vault/` | CONTRACT_OR_TEST | CONTRACT_OR_TEST | P0 | This backlog document | Agents may continue using obsolete plans/demo docs as active requirements | Make `docs/54_final_product_backlog.md`, README, ROADMAP, EVALS, and contracts the live guidance set |
| FPB-008 | Correct stale live documentation | `README.md`, `obsidian-vault/02 Project Control/Known Limitations.md` | CONTRACT_OR_TEST | CONTRACT_OR_TEST | P0 | FPB-007 | Users and agents may think integrated modules are still missing | Correct README now; schedule Obsidian limitation pruning |

### P1 - Required for a Strong Final Case

| ID | Item | Origem | Categoria | Decisao | Prioridade | Dependencias | Risco se ignorado | Proximo menor passo |
|---|---|---|---|---|---|---|---|---|
| FPB-009 | Product UI over real data | `frontend/src/App.tsx`, `docs/51_minimal_demo_ui.md` | REPLACE | REPLACE | P1 | FPB-001, FPB-002 | UI remains a local sample runner rather than a product workspace | Specify list/detail/run/brief/review screens tied to product endpoints |
| FPB-010 | Human review and status workflow | `ROADMAP.md`, `docs/09_user_workflow.md`, `AGENTS.md` | PRODUCT_BACKLOG | IMPLEMENT | P1 | FPB-001, FPB-003 | Recommendations look final without human validation or decision status | Define ReviewDecision states and `/analysis-runs/{id}/review` contract |
| FPB-011 | Opportunity list/ranking over persisted startups | `src/scoring/composite_ranking.py`, `docs/09_user_workflow.md` | PRODUCT_BACKLOG | IMPLEMENT | P1 | FPB-001, FPB-003 | Product cannot support portfolio-level prioritization | Define `GET /opportunities` from latest valid analysis runs |
| FPB-012 | Professional export records | `docs/09_user_workflow.md`, `scripts/run_startup_radar_demo.py` | PRODUCT_BACKLOG | IMPLEMENT | P1 | FPB-005 | Outputs remain local files, hard to share or audit | Define ExportRecord and product export route; defer PDF implementation |
| FPB-013 | Product auth and operator roles | `docs/50_minimal_fastapi_demo_api.md`, `docs/51_minimal_demo_ui.md` | PRODUCT_BACKLOG | IMPLEMENT | P1 | Product API foundation | Product cannot be used safely beyond local trusted demos | Define minimal role model and auth boundary in next API contract |
| FPB-014 | Product-ready API schemas and error policy | `src/api/schemas.py`, `docs/contracts/` | CONTRACT_OR_TEST | CONTRACT_OR_TEST | P1 | FPB-002 | API behavior will drift without schemas and failure contracts | Add product API contract before implementation |
| FPB-015 | Qdrant corpus freshness surfaced to product output | `docs/44_corpus_freshness_versioning_policy.md`, `README.md`, `scripts/audit_nvidia_corpus_freshness.py` | IMPLEMENTED_NEEDS_HARDENING | HARDEN | P1 | RAG corpus audit, Action Brief warnings | Stale RAG context may influence briefs without user-visible freshness status | Add backlog item for product warning/status, then contract/test it |
| FPB-016 | Real startup source collection beyond one URL | `README.md`, `docs/15_scraping_policy.md`, `scripts/sync_nvidia_sources.py` | PRODUCT_BACKLOG | IMPLEMENT | P1 | Source policy, persistence | Product cannot support real discovery at useful scale | Define non-aggressive source intake policy and persisted source model |
| FPB-017 | Demo API and `/demo/artifacts` replacement | `src/api/routes.py`, `src/api/service.py`, `data/demo_runs/latest/` | REPLACE | REPLACE | P1 | FPB-001, FPB-012 | Demo file browser becomes accidental product surface | Replace with product export/artifact records and archive demo route |

### P2 - Robustness, Quality, and Operations

| ID | Item | Origem | Categoria | Decisao | Prioridade | Dependencias | Risco se ignorado | Proximo menor passo |
|---|---|---|---|---|---|---|---|---|
| FPB-018 | Deterministic analytical pipeline core | `src/pipeline/`, `src/scoring/`, `src/recommendation/` | IMPLEMENTED_KEEP | KEEP | P2 | Existing contracts/tests | Reimplementation would add risk without product value | Keep as core service invoked by persisted run orchestration |
| FPB-019 | Action Brief builder and renderer | `src/briefing/`, `docs/contracts/briefing_contract.md` | IMPLEMENTED_KEEP | KEEP | P2 | PipelineResult | Losing brief contract weakens executive output | Keep and wrap with persisted ActionBriefRecord |
| FPB-020 | Product RAG core and corpus lifecycle tooling | `src/rag/`, `docs/contracts/rag_contract.md`, `scripts/ingest_nvidia_corpus.py` | IMPLEMENTED_KEEP | KEEP | P2 | Corpus, optional Qdrant | Product loses grounded NVIDIA technology context | Keep, but make dependency state explicit in product mode |
| FPB-021 | Evaluation and regression quality gates | `EVALS.md`, `tests/evals/`, `scripts/build_regression_dashboard.py` | IMPLEMENTED_KEEP | KEEP | P2 | Test fixtures/reports | Regressions in pipeline/brief/RAG become harder to catch | Keep as development and release gates |
| FPB-022 | Config/settings coverage | `EVALS.md`, `src/config/settings.py` | CONTRACT_OR_TEST | CONTRACT_OR_TEST | P2 | Existing settings | Environment bugs can break product deployment | Add settings tests in a later hardening epic |
| FPB-023 | Frontend test depth | `docs/51_minimal_demo_ui.md`, `tests/e2e/test_demo_ui.spec.ts` | IMPLEMENTED_NEEDS_HARDENING | HARDEN | P2 | Product UI design | UI regressions beyond smoke path may slip | Add product UI unit/component tests after product UI shape is defined |
| FPB-024 | Multi-platform CI confidence | `README.md`, `docs/40_ci_cd_quality_gates.md` | IMPLEMENTED_NEEDS_HARDENING | HARDEN | P2 | CI workflow | Windows/macOS issues remain invisible | Add CI matrix only after product foundation stabilizes |
| FPB-025 | Output validation for product API responses | `src/validation/output_validation.py`, `EVALS.md` | CONTRACT_OR_TEST | CONTRACT_OR_TEST | P2 | Product API schemas | Product responses may miss warnings, evidence, or uncertainty | Extend validators after product response schemas exist |
| FPB-026 | Document pruning quality gate | `docs/27_developer_rag_design.md`, `docs/54_final_product_backlog.md` | CONTRACT_OR_TEST | CONTRACT_OR_TEST | P2 | Documentation pruning | Obsolete docs can re-enter active context | Add a docs-pruning check or checklist after pruning epic |

### P3 - Optional or Post-delivery

| ID | Item | Origem | Categoria | Decisao | Prioridade | Dependencias | Risco se ignorado | Proximo menor passo |
|---|---|---|---|---|---|---|---|---|
| FPB-027 | Cross-encoder reranking | `ROADMAP.md`, `docs/38_rag_reranking_context_packing.md` | PRODUCT_BACKLOG | IMPLEMENT | P3 | Real retrieval baseline and eval data | Deterministic reranking may be less semantically precise | Revisit after product data produces real retrieval feedback |
| FPB-028 | Real LLM judge provider | `docs/48_optional_llm_judge.md`, `src/evaluation/llm_judge_adapter.py` | PRODUCT_BACKLOG | IMPLEMENT | P3 | Governance, API keys, cost policy | Semantic answer quality remains pattern-based | Add only with explicit provider/cost/security plan |
| FPB-029 | LangGraph multi-agent orchestration | `DECISIONS.md`, `src/agents/`, `ROADMAP.md` | PRODUCT_BACKLOG | IMPLEMENT | P3 | Product run model | Current deterministic pipeline lacks multi-agent runtime, but still functions | Reassess after persisted run lifecycle and review workflow |
| FPB-030 | Historical plan archive | `docs/plans/`, `obsidian-vault/03 Research/` | ARCHIVE | ARCHIVE | P3 | Documentation pruning | Historical plans may confuse agents if treated as current scope | Move or mark old plans as history after live docs are consolidated |
| FPB-031 | Demo generated outputs | `data/demo_runs/latest/` | DELETE | DELETE | P3 | Product exports in FPB-012 | Local outputs can be mistaken for product records | Delete after product export records and fixtures are in place |
| FPB-032 | Temporary/test corpus files | `data/nvidia_corpus/archive_test.md`, `nim_test.md`, `temp_test_source.md` | DELETE | DELETE | P3 | Corpus test fixtures audit | Test artifacts can pollute product corpus | Confirm tests do not depend on them, then delete or move to fixtures |
| FPB-033 | Demo-only docs after consolidation | `docs/08_demo_script.md`, `docs/49_cli_demo_end_to_end.md`, `docs/50_minimal_fastapi_demo_api.md`, `docs/51_minimal_demo_ui.md`, `docs/52_demo_acceptance.md` | ARCHIVE | ARCHIVE | P3 | Product docs replacement | Demo instructions remain overrepresented in product docs | Archive once product API/UI/exports docs exist |
| FPB-034 | Validation example fixtures | `examples/validation/` | IMPLEMENTED_KEEP | KEEP | P3 | Output validation tests | Removing fixtures would weaken validators | Keep as test fixtures, not product docs |

## 8. Final Documentation Policy

The final product must not carry every historical document as active guidance.
It should carry only live, consolidated documentation needed for use,
maintenance, evaluation, and delivery.

Allowed final documentation roles:

- `KEEP_AS_LIVE_DOC`: remains an active source of truth.
- `MERGE_INTO_LIVE_DOC`: useful content should be folded into a live doc.
- `CONVERT_TO_BACKLOG`: useful ideas become backlog items, not live docs.
- `CONVERT_TO_TEST_OR_CONTRACT`: rules become schemas, contracts, tests, evals,
  or quality gates.
- `ARCHIVE_HISTORY`: preserved as history only.
- `DELETE_AFTER_CONSOLIDATION`: remove after useful content is captured.

Live docs should be limited to README, ROADMAP, EVALS, AGENTS, DECISIONS,
contracts, product architecture/operation docs, and this consolidated backlog
until superseded by implementation-specific product docs.

## 9. Documentation Pruning Table

| Document | Current role | Final documentation decision | Reason | Target live doc or action | Priority |
|---|---|---|---|---|---|
| `README.md` | User/developer entry point | KEEP_AS_LIVE_DOC | Must describe current product capabilities and limitations | Keep short; point to `docs/54_final_product_backlog.md` | P0 |
| `ROADMAP.md` | Delivery status | KEEP_AS_LIVE_DOC | Tracks epic status and next product epic | Add Epic 28 and product foundation next | P0 |
| `EVALS.md` | Quality baseline | KEEP_AS_LIVE_DOC | Active testing and quality gate source | Add Epic 28 documentary validation note | P1 |
| `AGENTS.md` | Agent operating rules | KEEP_AS_LIVE_DOC | Required workspace policy | No change unless future contradiction appears | P1 |
| `DECISIONS.md` | Architecture/process decisions | KEEP_AS_LIVE_DOC | Active decision log | Keep; avoid adding outside this scope | P1 |
| `docs/54_final_product_backlog.md` | Product backlog source | KEEP_AS_LIVE_DOC | New source of truth for productization | Keep until backlog is implemented or superseded | P0 |
| `docs/contracts/*.md` | Module contracts | KEEP_AS_LIVE_DOC | Active contract guidance | Keep and extend for product API/entities later | P0 |
| `docs/00_case_plan.md` | Original case/MVP plan | ARCHIVE_HISTORY | Valuable historical case, but demo/MVP oriented | Preserve as history; do not guide current scope | P2 |
| `docs/00_project_brief.md`, `docs/01_problem_definition.md` | Early product framing | MERGE_INTO_LIVE_DOC | Useful concise framing | Fold stable product purpose into README/future product overview | P2 |
| `docs/02_architecture.md` | Early architecture | MERGE_INTO_LIVE_DOC | Superseded by implemented modules and contracts | Merge into future product architecture doc | P1 |
| `docs/03_data_contracts.md` | Early data contracts | MERGE_INTO_LIVE_DOC | Superseded by Pydantic schemas/contracts | Merge relevant fields into product entity contract | P1 |
| `docs/04_agent_specs.md` | Planned agents | CONVERT_TO_BACKLOG | Agents are not product-critical yet | Keep as source for later LangGraph epic | P3 |
| `docs/05_rag_design.md` | Early RAG design | ARCHIVE_HISTORY | Superseded by `docs/35-39` and RAG contract | Archive after RAG contract remains current | P2 |
| `docs/06_recommendation_logic.md` | Recommendation behavior | MERGE_INTO_LIVE_DOC | Still valuable but should be contract-backed | Merge with recommendation contract as needed | P2 |
| `docs/07_evaluation_plan.md` | Early eval plan | MERGE_INTO_LIVE_DOC | Superseded by EVALS | Fold any still-useful criteria into EVALS | P2 |
| `docs/08_demo_script.md` | Demo script | ARCHIVE_HISTORY | Demo no longer main direction | Archive after product docs exist | P3 |
| `docs/09_user_workflow.md` | Desired workflow | CONVERT_TO_BACKLOG | Contains export/share/reanalysis/ranking ideas | Use as source for product API/UI roadmap | P1 |
| `docs/10-17_*.md` | Product rules/templates/policies | KEEP_AS_LIVE_DOC | Maturity, scoring, gap, mapping, evidence, scraping, brief, rubric are product rules | Keep or merge into contracts during docs pruning | P1 |
| `docs/25-28_*.md` | Workspace governance | MERGE_INTO_LIVE_DOC | Useful but overlaps AGENTS/README | Keep short or merge into AGENTS/README later | P2 |
| `docs/35-48_*.md` | RAG/eval/ops design docs | KEEP_AS_LIVE_DOC | Active technical maintenance docs, with some superseded sections | Keep, but update superseded limitations during pruning | P1 |
| `docs/49-52_demo*.md` | Demo docs | ARCHIVE_HISTORY | Demo-specific, not final product docs | Archive after product API/UI docs exist | P3 |
| `docs/52_workspace_clarification_gate.md`, `docs/53_workspace_output_validation_gate.md` | Workspace quality gates | KEEP_AS_LIVE_DOC | Active agent/process rules | Keep with AGENTS | P2 |
| `docs/plans/*` except Epic 28 | Historical plan artifacts | ARCHIVE_HISTORY | Plans record history, not active product truth | Keep in archive/history role | P3 |
| `obsidian-vault/03 Research/*`, `04 Decisions/*` | Research/decision mirror | ARCHIVE_HISTORY | Useful context, not production source of truth | Keep as lab/history; product docs live in repo | P3 |
| `obsidian-vault/02 Project Control/Known Limitations.md` | Limitations note | MERGE_INTO_LIVE_DOC | Contains stale contradictions | Merge corrected limitations into README/future docs, then archive | P1 |
| `examples/golden/`, `examples/rag_eval/`, `examples/answer_quality/` | Test fixtures/golden data | KEEP_AS_LIVE_DOC | Required for evals and regression safety | Keep as fixture docs/data | P1 |
| `examples/demo/` | Demo sample | DELETE_AFTER_CONSOLIDATION | Useful while demo tests exist, not product input | Replace with product seed/fixture strategy later | P3 |
| `examples/validation/` | Output validation fixtures | KEEP_AS_LIVE_DOC | Supports validation tests | Keep as test fixtures | P2 |
| `data/demo_runs/latest/` | Generated demo outputs | DELETE_AFTER_CONSOLIDATION | Local generated artifacts, not source | Delete after product exports exist | P3 |
| `data/regression_reports/`, `data/ingestion_reports/` | Local report artifacts | MERGE_INTO_LIVE_DOC | Useful ops evidence but generated | Keep generated-output policy; do not treat as product records | P2 |
| `data/nvidia_corpus/` | Product RAG corpus | KEEP_AS_LIVE_DOC | Active local corpus and manifests | Prune test/temp files separately | P1 |
| `frontend/` docs/code | Local demo UI | CONVERT_TO_BACKLOG | Working demo, not product UI | Use as reference for product UI replacement | P1 |
| `scripts/run_startup_radar_demo.py` | Demo CLI | ARCHIVE_HISTORY | Useful smoke/manual tool, not product workflow | Keep until product CLI/API exists, then archive | P3 |

## 10. Deletion Candidates

Deletion must happen in a later explicit pruning epic, not in Epic 28.

| Candidate | Reason | Dependency before deletion | Priority |
|---|---|---|---|
| `data/demo_runs/latest/*` | Generated local demo outputs, not source or product records | Product exports/fixtures clarified | P3 |
| `data/nvidia_corpus/archive_test.md` | Test-looking corpus artifact in product corpus | Confirm no active tests depend on path | P3 |
| `data/nvidia_corpus/nim_test.md` | Test-looking corpus artifact in product corpus | Confirm no active tests depend on path | P3 |
| `data/nvidia_corpus/temp_test_source.md` | Temporary test source in product corpus | Confirm no active tests depend on path | P3 |
| `data/ingestion_reports/*.json` and `*.md` committed reports | Generated local run reports can bloat product repo | Define generated report retention policy | P3 |
| Demo docs after product docs exist | Demo docs would overrepresent non-product path | Product API/UI/export docs completed | P3 |

## 11. Contract/Test/Eval Candidates

| Candidate | Origin | Target | Priority |
|---|---|---|---|
| Product API contract | `src/api/schemas.py`, `docs/50_minimal_fastapi_demo_api.md` | New contract covering startup/run/brief/review/export endpoints | P1 |
| Product entity contract | `docs/03_data_contracts.md`, `src/briefing/schemas.py`, pipeline schemas | Pydantic/DB boundary contract before DB implementation | P0 |
| Degraded dependency state tests | `src/api/service.py`, `src/rag/qdrant_store.py` | Tests for explicit DB/Qdrant/corpus degraded states | P0 |
| Documentation pruning gate | `docs/27_developer_rag_design.md` | Checklist or script preventing archived docs from driving implementation | P2 |
| Settings tests | `EVALS.md`, `src/config/settings.py` | Unit tests for env/default behavior | P2 |
| Product output validation | `src/validation/output_validation.py` | Extend validators after product API schemas exist | P2 |
| Human review quality gate | `docs/09_user_workflow.md`, `AGENTS.md` | Test/contract for review decision states | P1 |

## 12. Product Mode Target Behavior

Target behavior for the final product:

- A user creates or imports a `Startup`.
- The system records `StartupEvidence` with source, quote, confidence, and
  validation status.
- A user or scheduler creates an `AnalysisRun`.
- The run executes the existing pipeline and persists score records, gap
  diagnosis, NVIDIA mapping, recommendations, RAG context metadata, warnings,
  and missing evidence.
- The system creates a versioned `ActionBriefRecord`.
- The UI displays startup lists, run history, latest opportunity ranking,
  evidence, gaps, scores, recommendations, degraded states, and review status.
- A reviewer creates a `ReviewDecision`.
- Exports are created as `ExportRecord` objects, not loose local demo files.
- Quality gates run against product records and preserve warnings.

## 13. Recommended Product API Surface

Proposed only; not implemented in this epic.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/startups` | Create startup profile/entity |
| GET | `/startups` | List startups with latest status |
| GET | `/startups/{id}` | Retrieve startup, evidence summary, latest run |
| POST | `/startups/{id}/analysis-runs` | Start analysis for a startup |
| GET | `/analysis-runs/{id}` | Retrieve run status and structured outputs |
| GET | `/analysis-runs/{id}/brief` | Retrieve canonical persisted auditable Action Brief |
| GET | `/analysis-runs/{id}/brief/export/json` | Export canonical persisted Action Brief as JSON |
| POST | `/analysis-runs/{id}/evaluate` | Run quality evaluation on a persisted brief |
| POST | `/analysis-runs/{id}/review` | Record human review/status decision |
| GET | `/opportunities` | List ranked opportunities from persisted runs |
| GET | `/exports/{id}` | Retrieve export artifact metadata/content |

## 14. Required Product Entities

| Entity | Purpose |
|---|---|
| Startup | Durable startup identity, metadata, sector, website, and lifecycle status |
| StartupEvidence | Public evidence with source URL, quote, kind, confidence, and validation |
| AnalysisRun | Versioned execution of the pipeline for a startup |
| ScoreRecord | Defensibility, Inception Fit, Production Readiness, and composite scores |
| GapDiagnosis | Diagnosed gaps, evidence tags, confidence, and missing evidence |
| NvidiaMapping | Gap-to-technology candidates and provenance |
| ActionBriefRecord | Versioned structured brief and rendered Markdown |
| ReviewDecision | Human status, reviewer, notes, and next action |
| ExportRecord | Export format, path/storage key, version, and originating brief |
| ProductReadinessCheck | Operational checks for DB, Qdrant, corpus freshness, eval status |

## 15. Productization Roadmap

1. **Epic 29 - Product Backend Foundation (P0):** entity contracts, persistence
   model, repositories/services, product API contracts, explicit degraded
   dependency model, and migration path from demo inputs to persisted runs.
2. **Epic 30 - Product API Implementation (P0/P1):** implement startup,
   analysis-run, brief, evaluate, review, opportunities, and export endpoints
   without changing pipeline/scoring/RAG logic.
3. **Epic 31 - Product UI Replacement (P1):** replace sample-first UI with
   persisted startup/run/review/opportunity workflows.
4. **Epic 32 - Documentation Pruning (P2/P3):** archive historical plans/demo
   docs, remove generated outputs, merge live docs, and fix Obsidian stale
   limitations.
5. **Epic 33 - Operational Hardening (P2):** settings tests, CI matrix review,
   degraded-state tests, corpus freshness surfacing, and product output
   validation.

## 16. Recommended Immediate Next Step

Start **Epic 29 - Product Backend Foundation**.

Justification: the highest-risk P0 items all depend on persistence and product
API contracts. Without durable entities and analysis-run lifecycle, the current
system remains a high-quality demo harness rather than a usable product. Epic 29
should not alter scoring, RAG, recommendation, or UI logic; it should define and
wire the product data boundary needed by all later product work.

## Audit Summary

- Required areas analyzed: root docs/config, `docs/`, `docs/contracts/`,
  `docs/plans/`, `obsidian-vault/`, `examples/`, `scripts/`, `frontend/`,
  `src/api/`, `src/pipeline/`, `src/briefing/`, `src/rag/`,
  `src/evaluation/`, `src/scoring/`, `src/recommendation/`, `tests/`, and
  selected `data/` artifacts.
- Consolidated backlog items: 34.
- Product item categories:
  - `IMPLEMENTED_KEEP`: 5
  - `IMPLEMENTED_NEEDS_HARDENING`: 4
  - `PRODUCT_BACKLOG`: 12
  - `REPLACE`: 3
  - `DELETE`: 2
  - `ARCHIVE`: 2
  - `CONTRACT_OR_TEST`: 6
- Product item decisions:
  - `KEEP`: 5
  - `HARDEN`: 4
  - `IMPLEMENT`: 12
  - `REPLACE`: 3
  - `DELETE`: 2
  - `ARCHIVE`: 2
  - `CONTRACT_OR_TEST`: 6
