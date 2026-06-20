# NVIDIA Startup AI Radar — Opportunity Intelligence for NVIDIA Inception

[![CI](https://github.com/anomalyco/academy-nvidia/actions/workflows/ci.yml/badge.svg)](https://github.com/anomalyco/academy-nvidia/actions/workflows/ci.yml)

NVIDIA Startup AI Radar transforma sinais públicos de startups brasileiras em um ranking acionável, combinando agentes de coleta, validação de evidências, classificação AI-native, Production AI Readiness, AI-Native Defensibility Score e NVIDIA Inception Fit Score. O sistema diagnostica production AI gaps, recupera playbooks NVIDIA via RAG e gera um Startup Action Brief com prioridade, evidências, tecnologias recomendadas, experimento técnico sugerido e próxima ação para o time de Startups & VCs.

## Objective

Build a reproducible, versioned, AI-oriented workspace that prioritizes traceability, evidence quality, structured outputs, and continuous evaluation. Productization is guided by the consolidated final backlog in [docs/54_final_product_backlog.md](docs/54_final_product_backlog.md).

The primary product flow uses persisted entities (startups, analysis runs, Action Briefs, exports, reviews) via the product API. Legacy demo routes, sample-first UI inputs, and demo CLI surfaces have been removed from the active product path.

## Problem

NVIDIA needs a reliable way to identify, attract, and nurture Brazilian startups with real AI-native potential instead of companies that only wrap third-party LLMs without durable technical advantages. O Radar resolve esse problema com uma pipeline auditável que combina scoring duplo, ranking ponderado por confiança e briefings com experimentos técnicos sugeridos.

## Guiding Question

How can NVIDIA identify, attract, and nurture Brazilian AI-native startups in a context where frontier AI labs are threatening startups that rely only on LLM wrappers?

## High-Level Architecture

1. Search planning defines what evidence must be collected.
2. Scraping and parsing gather public, policy-compliant signals.
3. Extraction converts raw evidence into structured startup profiles.
4. Classification and evidence validation separate facts from inference.
5. **Dual Scoring Engine** computes Defensibility Score + Inception Fit Score.
6. **Confidence-aware Ranking** positions the startup with explicit uncertainty.
7. **Gap Diagnosis** detects production AI gaps (15 gap types) with confidence.
8. **NVIDIA Technology Mapping** maps each gap to relevant NVIDIA technologies.
9. **Recommendation Engine** generates deterministic per-gap recommendations with action, priority, experiment, and next step.
10. **Startup Action Brief** produces executive-ready outputs with traceability.
11. **Product RAG** retrieves NVIDIA documentation snippets from Qdrant with real embeddings to enrich briefs with grounded, provenance-tracked context.
12. **RAG Evaluation** offline evaluation layer with golden queries, 7 retrieval metrics, and 6 quality gates for the Product RAG module.
13. **Reranking + Context Packing** deterministic reranking (composite score: gap/tech boost + provenance/duplicate/irrelevant penalties) and context packing (dedup, gap/tech limits, provenance filtering) for enriched, clean NVIDIA context in briefs.
14. **Persistent Vector Store (Qdrant)** required Qdrant-backed vector store with full payload provenance and server-side filtering in `APP_MODE=product`.
15. **CI/CD & Quality Gates** GitHub Actions CI (ruff, black, mypy, pytest), pre-commit hooks, Makefile targets, scope/documentation validation scripts.
16. **Startup Discovery Engine** Multi-source discovery of AI-native Brazilian startups with manual seed and URL list importers, keyword-based AI-native signal detection, dedup (normalized_name + domain), DiscoveryRun lifecycle (queued/running/completed/degraded/failed), candidate management, and promotion to Startup records with evidence migration.
17. **Source Sync** Allowlist-based download of NVIDIA documentation to staging with hash comparison, robots.txt verification, rate limiting, and optional promotion to the local corpus.
17. **Corpus Freshness & Versioning** Local lifecycle policy with source versions, active/deprecated flags, stale/expired audit, and default retrieval filtering for active non-expired corpus chunks.
18. **Scheduled Corpus Maintenance** Manual and scheduled-safe workflow that runs source sync dry-run, freshness audit, Qdrant ingest dry-run, optional real ingestion, RAG evals, golden evals, and artifact reports.
19. **Regression Dashboard** Local Markdown/JSON dashboard consolidating ingestion, freshness, RAG evals, golden evals, Action Brief checks, warnings, and regressions for GitHub Actions summaries.
20. **Answer Quality Evaluation** Offline deterministic harness for final RAG/Action Brief quality: required sections, missing evidence, uncertainty, motion stability, unsupported claims, and citation coverage.
21. **Evidence & Claim Ledger** Deterministic claim generation from persisted pipeline records, evidence coverage metrics, unsupported claim detection, and human review of claims.
21. **Optional LLM Judge Adapter** Experimental/manual answer quality judge interface with offline null provider and informational JSON/Markdown reports.

See [docs/54_final_product_backlog.md](docs/54_final_product_backlog.md) for the consolidated product backlog, [docs/contracts/product_api_contract.md](docs/contracts/product_api_contract.md) for the product API contract, and [docs/73_final_architecture_summary.md](docs/73_final_architecture_summary.md) for the detailed architecture summary.

## Current Capabilities

### Pipeline (12-step deterministic flow)
1. **Extraction** — structured startup profile from raw text (sector, signals, tech stack, customers, funding)
2. **AI-native Classification** — 5-level heuristic classification (NON_AI → AI_NATIVE_SERVICE) with confidence
3. **Evidence Validation** — FACT/INFERENCE/HYPOTHESIS tagging with confidence recalibration
4. **AI-Native Defensibility Score** — 6-dimension scoring (0–100) measuring technical moat durability
5. **NVIDIA Inception Fit Score** — 4-dimension scoring (0–100) measuring ecosystem alignment
6. **Production AI Readiness** — 4-dimension scoring (0–100) measuring production maturity
7. **Composite Ranking** — weighted aggregation (defensibility 30%, inception fit 25%, production readiness 35%, classification 10%) with confidence penalty and motion hint
8. **Gap Diagnosis** — 15 deterministic gap detectors with confidence and evidence tags
9. **NVIDIA Technology Mapping** — deterministic matrix mapping each gap to relevant technologies
10. **Recommendation Engine** — per-gap recommendations with action, priority, and suggested experiment
11. **Output Consolidation** — aggregated evidence_used, missing_evidence, reasoning
12. **Product RAG** — Qdrant semantic retrieval, deterministic reranking, context packing, provenance tracking

13. **CI/CD & Quality Gates** — GitHub Actions (ruff, black, mypy, pytest), pre-commit hooks, Makefile targets, scope-check and docs-closure verification scripts.

14. **Claim Ledger** — Deterministic claim generation from evidence/gap/mapping records, evidence coverage metrics, unsupported critical claim detection, claim review
15. **Claim API** — REST endpoints for listing claims, evidence coverage, and human review

16. **Opportunity Score & Pipeline Ranking** — Evidence-backed 0.0–1.0 scoring with 10 weighted components (composite ranking, evidence coverage, gap resolution, NVIDIA mapping, activation readiness, dossier completeness, quality score, claim support, review status, production readiness), 8 penalty types, weight redistribution, score tiers (critical/high/medium/low/not_recommended), explanation model, and ranked pipeline API.

### Startup Discovery Engine
- **Source Registry** — `src/config/discovery_sources.json` (6 sources) + `src/discovery/source_registry.py` (loader with cache, `is_usable()`, `list_enabled_sources()`)
- **Signal Detection** — `src/discovery/signals.py` (30+ keywords, 5-factor confidence, has_nvidia_tech flag, evidence excerpts)
- **Dedup** — `src/discovery/dedup.py` (normalize_name, extract_domain, is_duplicate_by_name, is_duplicate_by_domain)
- **Repository** — `src/repositories/discovery.py` (DiscoveryRun + Candidate CRUD, promote, dedup, bulk creation)
- **Service** — `src/discovery/service.py` (manual seed, URL list, promote, dedup)
- **API** — 9 endpoints in `src/api/product_routes.py` (sources, manual-seed, url-list, runs, candidates, promote, dedup)

### Workflow Orchestration
- **Workflow Runner** — LangGraph-based 11-node execution in `APP_MODE=product`, with per-node retry, degraded/failed status propagation, state persistence, and explicit failure if orchestration is not configured. Sequential execution is reserved for test/development mode.
- **Workflow Nodes** — 11 nodes wrapping existing services: load_startup_or_candidate (critical), collect_or_load_evidence, validate_evidence, diagnose_gaps, retrieve_nvidia_context, map_nvidia_technologies, generate_claims, match_activation_playbooks, generate_activation_dossier, run_product_quality, summarize_readiness.
- **Workflow API** — 6 REST endpoints (POST/GET product-runs, GET nodes, GET analysis-run workflow, GET langgraph-status).
- **Workflow Repository** — CRUD for workflow runs with full node-level tracing (input/output snapshots, retry count, error tracking).
- **Database Models** — `WorkflowRun` and `WorkflowNodeRun` with FK, indexes, lifecycle statuses.
- **Degraded State Codes** — 6 new readiness codes (WORKFLOW_NODE_FAILED, WORKFLOW_DEGRADED, WORKFLOW_RAG_SKIPPED, WORKFLOW_QUALITY_FAILED, WORKFLOW_DOSSIER_MISSING, WORKFLOW_DISCOVERY_PROMOTION_FAILED).
- **Capability Registry** — 3 capabilities: `agent_orchestration` (requires `[agent-orchestration]` extra), `workflow_runs`, `workflow_node_tracing`.

### Product UI (10 consolidated views)
1. **Setup** — product readiness, configuration checklist, Playwright E2E notes, quality report link
2. **Capabilities** — product capability registry with status and setup instructions
3. **Discovery** — sources, discovery runs, candidates list with filters, manual seed, promote to startup
4. **Startups** — startup list with status, detail panel, analysis run creation
5. **Analysis Run** — full run detail with scores, claims, gaps, NVIDIA mappings, readiness checks
6. **Dossier** — activation dossier with markdown, raw JSON, warnings for low coverage/unsupported claims
7. **Opportunities** — All opportunities + Ranked tab with opportunity-score columns
8. **Workflow** — workflow runs list, node timeline (read-only), detail view
9. **Export Delivery** — checklist, export commands (curl), limitations and notes
10. **Quality** — dedicated quality report view with metrics and pass/fail breakdown

### Modules implemented
- `src/repositories/claim.py` — claim persistence, coverage, unsupported detection
- `src/services/product/claim_ledger.py` — deterministic claim generation
- `src/services/product/claim_constants.py` — enums and types
- `src/scraping/` — fetcher, parser, source policy
- `src/extraction/` — extractor, schemas (Pydantic)
- `src/classification/` — AI-native classifier (heuristic)
- `src/validation/` — evidence validator (deterministic)
- `src/scoring/` — defensibility, inception fit, production readiness, composite ranking
- `src/pipeline/` — pipeline orchestrator (run_full_pipeline)
- `src/diagnosis/` — gap diagnosis (15 detectors) + NVIDIA technology mapping
- `src/recommendation/` — deterministic recommendation engine (schemas, engine)
- `src/briefing/` — Startup Action Brief consolidation and Markdown rendering
- `src/rag/` — Product RAG ingestion, lexical + semantic + hybrid retrieval, embeddings, vector store, playbook retriever, **deterministic reranking, context packing, Qdrant persistent vector store, + Epic 42: Hybrid RAG (query planner, BM25 sparse retrieval, RRF/weighted fusion, cross-encoder reranking, citation packaging, evidence refs helpers)**
- `src/evaluation/` — Offline RAG evaluation (golden queries, metrics, quality gates, multi-mode comparison, **reranking/packed**), deterministic Answer Quality evaluation, and optional experimental LLM judge adapter with offline null provider
- `src/config/` — settings via pydantic-settings
- `src/database/`, `src/repositories/`, `src/services/product/` — SQLite-first transactional product persistence, persisted analysis lifecycle, and explicit degraded states
- `scripts/` — validation and quality gate scripts (check_scope, check_docs_closure, validate), Qdrant corpus ingestion, NVIDIA source sync, corpus freshness audit, corpus maintenance orchestration, regression dashboard generation

### Testing
- ~775 Python tests across 76 Python test files, plus 6 Playwright UI E2E smoke tests
- Backend acceptance tests (`tests/acceptance/`, marker: `acceptance`) validate the Product Golden Path
- Playwright E2E smoke tests (`tests/e2e/test_product_ui.spec.ts`, 6 tests) cover UI golden path (setup, capabilities, startup creation, detail, analysis run, dossier, opportunities)
- All scoring modules have scenario-based tests (Portuguese-named golden examples)
- Gap diagnosis: 14 tests covering 10/15 gaps individually + end-to-end + missing evidence
- NVIDIA mapping: coverage verified for all 15 gaps (each has ≥1 technology mapped)
- Recommendation engine: 22 tests covering action matrix, priority, experiments, per-gap, and full integration
- Pipeline integration: 10 tests covering full flow with gaps, recommendations, weak evidence, missing_evidence propagation, and extended output shape
- RAG ingestion: 4 tests (sources, corpus, chunking, metadata)
- RAG retrieval: 6 tests (index, gap, tech, empty, keywords, scores)
- Playbook retriever: 5 tests (inference gap, agent gap, missing, brief dicts, no-rag crash)
- RAG Evaluation: 20 tests (golden queries, metrics, quality gates, provenance, brief compatibility)
- RAG Embeddings: 12 tests (mock provider, determinism, normalization, batch, missing dependency message)
- Semantic Retrieval: 15 tests (contexts, provenance, filters, query text)
- Hybrid Retrieval: 12 tests (fallback, RRF fusion, filters, dedup)
- Multi-Mode Eval: 14 tests (lexical/semantic/hybrid comparison, regressions)
- RAG Reranking: 9 tests (deterministic composite score, gap/tech boost, provenance penalty)
- Context Packing: 13 tests (dedup, limits, metrics, build_supporting_contexts)
- RAG Eval Reranking: 11 tests (HYBRID_RERANKED and HYBRID_RERANKED_PACKED modes, packed metrics, regression detection)
- Action Brief RAG Context: 5 tests (optional packing, empty defaults, motion unchanged)
- Pipeline RAG Integration: 10 tests (packed contexts, no RAG, empty index, brief section, dropped not in brief, motion unchanged, provenance, quality summary, backward compat, lexical mode)
- Qdrant Store: 20 tests (lazy connection, error, add, remove, clear, get, size, search, filters, provenance, factory)
- Qdrant Pipeline Integration: 9 tests (skippable — requires QDRANT_TEST_URL)
- Corpus Freshness Audit: 11 tests (stale, expired, deprecated, superseded, missing metadata, duplicate active versions, fail flags, version promotion, retrieval/vector filters)
- Check Scope: 7 tests (sensitive changes require docs, override flag, contract detection)
- Check Docs Closure: 6 tests (plan, ROADMAP, EVALS, Obsidian checks)
- Regression Dashboard: 14 tests (PASS/WARN/FAIL, missing reports, JUnit missing context, Answer Quality JUnit pass/failure/error/skipped/missing, optional LLM judge present/absent, Markdown sections, JSON fields)
- Answer Quality Eval: 9 tests (offline golden cases, missing sections/evidence/uncertainty, motion stability, unsupported claims, citation coverage, absolute language)
- Optional LLM Judge: 4 tests (offline null provider, report aggregation, prompt contents, manual script output)
- Output Validation Gate: 12 tests (Action Brief, Markdown, dashboard, and API output validators)
- Discovery Signals: 11 tests (LLM, IA, GPU, CUDA, TensorRT, NLP, nvidia_tech, evidence_excerpts, confidence bounds)
- Discovery Dedup: 15 tests (normalize_name, extract_domain, duplicate checks)
- Discovery Repository: 15 tests (DiscoveryRun + Candidate CRUD)
- Discovery API: 14 integration tests (sources, manual seed, runs, candidates, promote, dedup)
- Workflow State: 5 tests (constants, defaults, serialization)
- Workflow Repository: 19 tests (CRUD, status transitions, node tracing, retry)
- Workflow Runner: 6 tests (node registration, retry policy, langgraph detection, full workflow execution)
- Workflow API Integration: 12 tests (POST/GET product-runs, nodes, analysis-run link, langgraph status)

## Stack

- Python
- FastAPI
- Pydantic
- LangGraph
- PostgreSQL
- SQLite (default transactional product database)
- Qdrant
- Playwright
- BeautifulSoup
- trafilatura
- pytest
- Docker Compose
- ruff
- black
- mypy
- pre-commit
- GitHub Actions
- Vite
- React
- TypeScript

## Quickstart

### Required Setup
1. Copy `.env.example` to `.env` and set at minimum:
   - `APP_MODE=product`
   - `PRODUCT_DB_URL=postgresql+psycopg://...`
   - `QDRANT_URL=http://localhost:6333`
   - `QDRANT_COLLECTION=nvidia_corpus`
   - `RAG_VECTOR_BACKEND=qdrant`
   - `RAG_REQUIRED_FOR_PRODUCT=true`
   - `RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`
   - `AGENT_ORCHESTRATION_ENABLED=true`
   - `ENABLE_PRODUCT_PERSISTENCE=true`
2. Install backend:
   ```bash
   pip install -e ".[dev,rag,agent-orchestration]"
   ```
3. Run migrations:
   ```bash
   alembic upgrade head
   ```
4. Start backend:
   ```bash
   uvicorn src.api.main:app --reload
   ```
5. Check readiness:
   ```bash
   curl http://localhost:8000/product/readiness
   curl http://localhost:8000/product/capabilities
   ```

### Optional Setup
- **RAG:** `pip install -e ".[rag]"` + configure `RAG_EMBEDDING_MODEL`
- **Qdrant:** `docker compose up qdrant -d` + configure `QDRANT_URL`
- **LLM Judge / Instructor:** `pip install -e ".[llm-judge]"` + `ENABLE_INSTRUCTOR_TRIAL=true`

### Start Frontend
```bash
cp frontend/.env.example frontend/.env
cd frontend && npm install && npm run dev
```
Open http://localhost:5173 in your browser.

### Run First Analysis (via API)
```bash
# Create startup
curl -X POST http://localhost:8000/startups \
  -H "Content-Type: application/json" \
  -d '{"name":"My Startup","website":"https://example.com","sector":"AI"}'

# Get startup ID from response, then run analysis
curl -X POST http://localhost:8000/startups/{id}/analysis-runs \
  -H "Content-Type: application/json" \
  -d '{"use_rag":false}'

# View dossier
curl -X POST http://localhost:8000/analysis-runs/{run_id}/dossier

# Run quality checks
curl -X POST http://localhost:8000/analysis-runs/{run_id}/quality-runs

# View opportunities
curl http://localhost:8000/opportunities
```

### Run Acceptance Tests
```bash
make acceptance           # Backend acceptance tests (Product Golden Path)
make ui-e2e-product       # Playwright E2E smoke (separate target, requires backend)
python scripts/product_acceptance_report.py  # Readiness report
```

### Troubleshooting
- Readiness false: check `curl /product/readiness` → `blocking_missing_config`
- Analysis run fails: check `curl /analysis-runs/{id}` → `error_message`, `degraded_reason`
- UI blank: check `curl http://localhost:8000/health/product` → status
- Missing features: check `curl /product/capabilities` for `not_configured` status

## Product Walkthrough

The following script walks through the complete product flow from environment setup to delivery. Estimated time: 15–20 minutes.

### 1. Prepare Environment
```bash
cp .env.example .env
# Edit .env: APP_MODE=product, PRODUCT_DB_URL=postgresql+psycopg://...,
# QDRANT_URL, QDRANT_COLLECTION, RAG_VECTOR_BACKEND=qdrant,
# RAG_REQUIRED_FOR_PRODUCT=true, RAG_EMBEDDING_MODEL, AGENT_ORCHESTRATION_ENABLED=true
pip install -e ".[dev,rag,agent-orchestration]"
alembic upgrade head
```

### 2. Start Backend
```bash
uvicorn src.api.main:app --reload
# Verify: curl http://localhost:8000/health → {"status": "ok"}
```

### 3. Start Frontend
```bash
cp frontend/.env.example frontend/.env
cd frontend && npm install && npm run dev
```
Open http://localhost:5173 in your browser.

### 4. Setup (UI)
- Open **Setup** tab
- Confirm `Product is ready: true`
- Verify configuration checklist shows all required items complete
- Review capabilities status

### 5. Capabilities (UI)
- Open **Capabilities** tab
- Verify categories: Product Core, Discovery, RAG, Quality, Workflow, Orchestration

### 6. Discovery (UI)
- Open **Discovery** tab
- Review available discovery sources
- Click **Manual Seed**, add a startup name and URL
- Verify candidates appear with AI-native signal detection

### 7. Promote Candidate
- Select a candidate
- Click **Promote to Startup**
- Verify startup created in the Startups list

### 8. Run Workflow
- Open the startup detail
- Click **Run Analysis** (or trigger workflow via API)
- Wait for completion (status: `completed` or `degraded`)
- Verify: scores, gaps, NVIDIA mappings, claims

### 9. Opportunities (UI)
- Open **Opportunities** tab
- Switch to **Ranked** tab
- Verify opportunity scores, activation playbooks, evidence coverage

### 10. Dossier (UI)
- Select a high-priority startup
- Open **Dossier**
- View Markdown summary and raw JSON
- Note any warnings (low coverage, unsupported claims)

### 11. Quality (UI)
- Open **Quality** tab
- Verify quality metrics and pass/fail breakdown

### 12. Export (UI)
- Open **Export Delivery** tab
- Review export checklist
- Execute curl commands to export Markdown/JSON

### 13. Validation
```bash
make validate          # lint + format + typecheck + unit tests
make acceptance        # Product Golden Path
python scripts/check_no_demo_dependency.py  # no demo data proof
```

### 14. E2E Smoke (optional)
```bash
npx playwright install
make ui-e2e-product    # requires backend + frontend running
```

## Validation Command Matrix

| Command | Objetivo | Pré-requisitos | Esperado | Bloqueia entrega? |
|---|---|---|---|---|
| `make validate-fast` (ou `make validate`) | lint + format-check + typecheck + unit tests | Python + dev extras, pip install | 0 errors | Sim |
| `make validate-backend` | Idem validate-fast | Python + dev extras | 0 errors | Sim |
| `make validate-frontend` | tsc --noEmit + npm run build | Node + npm install | 0 errors | Sim |
| `make acceptance` | Product Golden Path (17 steps) | Backend running, DB migrated | All PASS | Sim |
| `make validate-docs` | check_scope + check_docs_closure | Git HEAD | All PASS | Overridable |
| `make typecheck` | mypy src | Python + dev extras | 0 errors | Sim |
| `make format-check` | black --check . | Python + dev extras | 0 errors | Sim |
| `make validate-full` | validate-fast + docs + frontend | Python + Node | 0 errors | Sim |
| `make prepare-release` | validate-full + acceptance + ui-build | Python + Node | 0 errors | Sim |
| `make ui-e2e-product` | Playwright E2E smoke (6 tests) | Backend + frontend running, browsers | 6 PASS | No (extra) |

### Quick Reference
```bash
make validate          # Fast iteration (<60s)
make validate-full     # Pre-commit validation
make acceptance        # Product Golden Path
make prepare-release   # Pre-release gate
```

### Running Individual Validations
```bash
pytest                 # All unit tests
ruff check .           # Lint
black --check .        # Format
mypy src               # Typecheck
pytest -m acceptance   # Acceptance tests only
python scripts/check_no_demo_dependency.py  # No demo dependency
```

## Playwright Policy

1. **Playwright E2E is separate** from core validation targets.
2. **Browser binaries are not installed automatically.** Manual command:
   ```bash
   npx playwright install
   ```
3. **Playwright does not block `make validate`** — absence of browsers never breaks `validate-fast`.
4. **`make ui-e2e-product` is extra evidence**, not a delivery gate.
5. If browsers are unavailable, E2E tests are skipped gracefully (Playwright config handles this).
6. E2E tests auto-start backend + frontend via Playwright's `webServer` config.

## Sample Input Policy

1. **Fixtures are test data only** — never loaded by product code or UI.
2. **No product path reads `data/demo_runs/`, `examples/demo/`, or `sample_inputs/`.**
3. **Approved test/documentation locations:** `tests/fixtures/` and `docs/examples/`.
4. **The product flow uses persisted DB/API entities** created through `/startups` and `/analysis-runs`.

---

## Installation

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the core project:

```bash
pip install -e .
```

Install developer dependencies:

```bash
pip install -e ".[dev]"
playwright install
```

Install optional RAG embedding dependencies when generating real local embeddings
for semantic/hybrid retrieval or Qdrant ingestion:

```bash
pip install -e ".[rag]"
```

Use `pip install -e ".[dev,rag]"` for a development environment with both test
tools and real RAG embeddings. The `rag` extra is optional because
`sentence-transformers` is specific to embeddings/RAG and pulls heavier model
runtime dependencies that the core pipeline does not need.

## Database Migrations

The product database uses Alembic for versioned schema migrations:

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Auto-generate a new migration from model changes
alembic revision --autogenerate -m "description"

# Show current revision
alembic current

# Show migration history
alembic history
```

Or via Makefile:
```bash
make db-upgrade
make db-downgrade
make db-migrate msg="description"
```

The migration reads `PRODUCT_DB_URL` from the environment. In `APP_MODE=product`,
`PRODUCT_DB_URL` must point to PostgreSQL. SQLite is reserved for explicit test
or development mode.

See `docs/contracts/product_db_migrations.md` for full documentation.

## Environment Configuration

Copy `.env.example` to `.env` and fill in the keys you actually need for local development.

Important variables:

- `OPENAI_API_KEY`
- `NVIDIA_API_KEY`
- `COHERE_API_KEY`
- `DATABASE_URL`
- `PRODUCT_DB_URL` (PostgreSQL required in `APP_MODE=product`)
- `PRODUCT_DB_TEST_URL` (PostgreSQL test URL, optional)
- `APP_MODE`
- `ENABLE_PRODUCT_PERSISTENCE`
- `RAG_REQUIRED_FOR_PRODUCT`
- `PRODUCT_DATA_DIR`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`
- `QDRANT_VECTOR_SIZE` (default `384`, matching the default RAG embedding model)
- `RAG_EMBEDDING_MODEL` (default `sentence-transformers/all-MiniLM-L6-v2`)
- `RAG_VECTOR_BACKEND`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`

## Product API

The primary flow uses persisted entities via the FastAPI product API. See
[docs/contracts/product_api_contract.md](docs/contracts/product_api_contract.md)
for endpoint documentation and usage.

## Product CLI/API

The active product path is the persisted FastAPI product API. Legacy demo CLI,
demo routes, and sample-first UI inputs have been removed from the active repo.

## Running Tests

```bash
pytest
```

## Code Quality

```bash
ruff check .
black --check .
mypy src
```

Or use the Makefile:
```bash
make lint        # ruff check .
make format-check  # black --check .
make typecheck   # mypy src
make test        # pytest (unit only)
make validate    # all of the above
make rag-eval    # RAG evaluation tests
make answer-quality-junit  # generate data/regression_reports/answer_quality_eval_junit.xml
make answer-quality-llm-judge  # optional/experimental offline null judge report
make validate-output  # run Workspace Output Validation Gate tests
make validate-brief-output  # run Action Brief output validation tests
make validate-dashboard-output  # run regression dashboard output validation tests
pytest tests/evals/test_answer_quality_golden.py -q  # answer quality evals
make corpus-maintenance-dry-run  # sync dry-run + freshness audit + ingest dry-run
make corpus-maintenance-evals    # safe maintenance + RAG/golden evals
make corpus-maintenance-ingest   # explicit real Qdrant ingestion path
make regression-dashboard  # build local Markdown/JSON regression dashboard
make ui-install  # install frontend dependencies
make ui-dev      # run the Product UI
make ui-build    # build the Product UI
make acceptance  # run Product Golden Path acceptance tests (separate target)
make acceptance-backend  # run acceptance tests excluding E2E
make prepare-release  # validate + acceptance + ui-build (pre-release gate)
make product-readiness-report  # generate readiness report via API
make ui-e2e-product  # Playwright E2E smoke tests for Product UI (separate target)
```

## CI/CD

GitHub Actions CI runs on push/PR to `main`:

- `ruff check .`
- `black --check .`
- `mypy src`
- `pytest -m "not integration"`

Corpus maintenance has a separate workflow at `.github/workflows/corpus-maintenance.yml`.
It supports manual `workflow_dispatch` and a safe weekly schedule. Real Qdrant ingestion
is disabled by default and requires `run_ingestion=true`; source promotion is also
disabled by default and requires `promote_sources=true`. Reports are uploaded as the
`corpus-maintenance-reports` artifact. The workflow also builds the regression dashboard,
writes `latest_dashboard.md` to the GitHub Actions Job Summary, uploads
`latest_dashboard.md` and `latest_dashboard.json` as artifacts, and fails only when the
consolidated dashboard status is `FAIL` (not for `WARN`).

Pre-commit hooks are available (install with `pre-commit install`):

- `trailing-whitespace`, `end-of-file-fixer`, `check-yaml/toml/json`
- `check-added-large-files`, `ruff`, `black`

Local validation scripts:

```bash
make validate
# or
scripts/validate.sh
python scripts/check_scope.py
python scripts/check_docs_closure.py
```

## Running the API

The FastAPI server exposes product endpoints only; legacy demo routes are not included in the main app.

### Start the API

```bash
# Production mode
uvicorn src.api.main:app

# Development mode with hot reload
uvicorn src.api.main:app --reload
```

Or via Makefile:

```bash
make api         # production
make api-dev     # development with reload
```

### Product endpoints (primary flow)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/startups` | Persist a product startup and initial evidence |
| `GET` | `/startups` | List persisted startups |
| `GET` | `/startups/{id}` | Read a persisted startup |
| `PATCH` | `/startups/{id}` | Update startup fields partially |
| `POST` | `/startups/{id}/analysis-runs` | Execute and persist an analysis run |
| `GET` | `/analysis-runs/{id}` | Read persisted lifecycle and outputs |
| `GET` | `/analysis-runs/{id}/brief` | Canonical source for the persisted, auditable quantitative Action Brief |
| `GET` | `/analysis-runs/{id}/brief/export/json` | Export the same persisted Action Brief with JSON export metadata |
| `POST` | `/analysis-runs/{id}/review` | Record human review decision |
| `GET` | `/analysis-runs/{id}/reviews` | List review decisions for a run |
| `GET` | `/opportunities` | Ranked opportunities with filters and pagination |
| `POST` | `/analysis-runs/{id}/exports` | Generate JSON or Markdown export |
| `GET` | `/exports/{id}` | Retrieve export metadata |
| `GET` | `/health/product` | Check product database and schema |
| `GET` | `/health/dependencies` | Check database, Qdrant, and RAG corpus |

Product consumers should treat `GET /analysis-runs/{id}/brief` as the canonical
read model for the user-facing Action Brief. It serializes the already persisted
`AnalysisRun` Action Brief with quantitative recommendations, evidence/RAG IDs,
audit trail, quality/calibration snapshots, and `brief_metrics`; it does not
trigger brief generation, RAG retrieval, scoring, scraping, or recommendation
ranking. Use `GET /analysis-runs/{id}` for run lifecycle/status and summary
context, not as the primary Action Brief payload.

### Removed Demo Endpoints

The main FastAPI app no longer exposes `/brief`, `/brief/evaluate`, or
`/demo/artifacts`. Use the persisted product resources under `/startups`,
`/analysis-runs`, `/opportunities`, `/reviews`, `/dossier`, and `/exports`.

### Swagger UI

Open http://localhost:8000/docs in your browser.

### Product API tests

```bash
pytest tests/integration/test_product_api.py -v
pytest tests/integration/test_product_patch_review_export.py -v
```

## Product Setup

### Required Configuration

1. Copy `.env.example` to `.env` and configure at minimum:
   - `PRODUCT_DB_URL` — PostgreSQL URL required in `APP_MODE=product`
   - `APP_MODE` — set to `product`
   - `ENABLE_PRODUCT_PERSISTENCE` — set to `true`
2. Install the base package:
   ```bash
   pip install -e .
   ```
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the API:
   ```bash
   uvicorn src.main:app --reload
   ```

### Checking Readiness

```bash
# Quick readiness check
curl http://localhost:8000/product/readiness

# List all features and their status
curl http://localhost:8000/product/capabilities

# Configuration checklist with progress
curl http://localhost:8000/product/setup-checklist

# All environment variables and current values
curl http://localhost:8000/product/configuration
```

### Optional Features

| Feature | Extra | Env Var | Install Command |
|---|---|---|---|
| RAG (sentence-transformers) | `rag` | `RAG_EMBEDDING_MODEL` | `pip install -e ".[rag]"` |
| LLM Judge / Instructor Trial | `llm-judge` | `ANSWER_QUALITY_LLM_JUDGE_ENABLED=true` | `pip install -e ".[llm-judge]"` |
| Qdrant Vector Store | — | `QDRANT_URL`, `QDRANT_COLLECTION` | Start Qdrant via docker-compose |

To enable the optional Instructor trial:
```bash
pip install -e ".[llm-judge]"
echo "ENABLE_INSTRUCTOR_TRIAL=true" >> .env
echo "ANSWER_QUALITY_LLM_JUDGE_ENABLED=true" >> .env
```

If Instructor is not installed, the LLM Judge uses `NullLLMJudgeProvider`
(deterministic offline scores) and the structured output trial reports
`missing_dependency`. The product core remains fully functional.

### How Readiness Blocks

- Missing **required** configuration → `ready=false` with clear messages.
- Missing **optional** configuration → feature marked `not_configured` or `missing_dependency`, but `ready=true`.
- Missing optional extra (e.g., `instructor`) → capability status `missing_dependency`, product continues working.
- No blocking occurs for optional features — the user sees what is missing but can still use the product.

## Product UI

A local Vite + React + TypeScript product UI lives under `frontend/`. It
consumes the Product API (`/product/readiness`, `/product/capabilities`,
`/startups`, `/analysis-runs`, `/opportunities`, `/dossier`, etc.) and
provides a workspace for setup, capabilities, startup management, analysis
execution, opportunities, dossier/quality visualization, and review actions.

The Product UI is the primary interface for the product flow.

### Prerequisites

- Backend running on `http://localhost:8000` (see [Running the API](#running-the-api))
- Product database configured (see [Product Setup](#product-setup))

### Environment

Copy `frontend/.env.example` to `frontend/.env`:

```bash
cp frontend/.env.example frontend/.env
```

Available variables:

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_APP_ENV` | `development` | Environment label |

These are client-side variables visible in the browser bundle. Never put
secrets (API keys, passwords) in frontend env vars.

### Running

```bash
make ui-install   # install frontend dependencies (npm install)
make ui-dev       # run the local dev server
make ui-build     # build for production
```

### Setup / Readiness

Open `http://localhost:5173` in your browser. The UI automatically checks
product readiness:

- **Ready** — all required configuration is set. Use the workspace.
- **Not Ready** — blocking and optional missing configuration is displayed
  with setup instructions.

The page shows a configuration checklist with progress, unavailable and
degraded capabilities, and user messages.

### Capabilities

Navigate to the **Capabilities** tab to see all registered product capabilities
grouped by category. Each capability shows status, required env vars, extras,
and setup instructions.

### Usage Flow

1. Ensure the product is **Ready** (Setup tab).
2. Create a startup via the **Startups** tab (name, website, sector).
3. Open the startup and click **Run Analysis**.
4. View the analysis run result: scores, gaps, NVIDIA mappings, claims,
   evidence coverage, activation recommendations, readiness checks.
5. Generate and view the **Activation Dossier** (Markdown + JSON).
6. Browse **Opportunities** — ranked table with scores, playbooks, coverage.
7. Submit reviews for analysis runs and claims (optional).

### E2E Tests (separate target)

```bash
make ui-e2e-product   # Run product UI E2E smoke tests (6 tests: readiness, capabilities, startups, opportunities, create startup, run analysis)
```

E2E tests require both backend and frontend running (auto-configured via Playwright webServer). Not included in `make validate`.

### Acceptance Tests (separate target)

```bash
make acceptance            # Run Product Golden Path backend acceptance tests
make acceptance-backend    # Same as acceptance (excludes E2E)
make prepare-release       # Full pre-release validation: validate + acceptance + ui-build
```

Acceptance tests validate the full product flow: readiness → capabilities → startup CRUD → analysis run → claims → activation playbook → dossier → quality → opportunities → export. Run via `@pytest.mark.acceptance`, excluded from `make validate`.

## Using the Obsidian Vault

The project includes an Obsidian knowledge-capture workspace in [obsidian-vault](/C:/Users/Inteli/Documents/Projetos/academy-nvidia/obsidian-vault). Use it for research capture, evidence notes, daily logs, and draft decisions.

Rule of thumb:

- Obsidian is the lab.
- The repository is production.

## Workspace Clarification Gate

The project includes a Workspace Clarification Gate rule in `AGENTS.md` that instructs the AI to ask clarifying questions before generating code, architecture, large docs, workflows, frontend, API, or long prompts when critical ambiguity exists. The rule limits questions to 3 per turn, requires recommended defaults, and defines safe fallback behavior when the user does not respond.

This prevents the AI from generating large artifacts based on unchecked assumptions — especially for UI, API, architecture, contracts, dependencies, CI/CD, pipeline, and RAG changes.

## Workspace Output Validation Gate

The project includes a Workspace Output Validation Gate rule in `AGENTS.md` and focused validators in `src/validation/output_validation.py`. Before closing non-trivial tasks that generate structured outputs, the AI must validate contract/schema, format, scope, evidence/uncertainty preservation, and relevant operational checks.

Current validators cover Startup Action Brief JSON, generated Markdown, regression dashboard JSON, and API response JSON using existing Pydantic schemas and the NVIDIA gap-to-technology mapping. The gate stays lightweight for small hotfixes: trivial localized fixes should record only the minimal relevant check.

## Using Skills

Reusable AI skills live in [skills](/C:/Users/Inteli/Documents/Projetos/academy-nvidia/skills). Each skill defines:

- when to use it
- required evidence and constraints
- expected outputs
- examples and, where appropriate, schemas

## Contributing

1. Start from a small, testable increment.
2. Update docs when changing contracts, evaluation logic, or architecture.
3. Register important decisions in [DECISIONS.md](/C:/Users/Inteli/Documents/Projetos/academy-nvidia/DECISIONS.md).
4. Add tests or explicitly justify why tests are not yet present.
5. Preserve traceability between claims, sources, schemas, and outputs.

## Quality Rule

No startup recommendation is valid without evidence and an explicit technical gap.

## Release Checklist

Use this checklist to validate a release candidate before delivery.

### Preparation
- [ ] Backend env configured (`cp .env.example .env`)
- [ ] DB migrations applied (`alembic upgrade head`)
- [ ] Product readiness checked (`GET /product/readiness` → `ready=true`)

### Validation
- [ ] Backend tests passed (`make validate-fast`)
- [ ] Frontend build passed (`make validate-frontend`)
- [ ] Docs closure passed (`make validate-docs`)
- [ ] Scope check passed (`python scripts/check_scope.py`)
- [ ] Acceptance path executed (`make acceptance`)

### Evidence
- [ ] No `data/demo_runs` dependency (`python scripts/check_no_demo_dependency.py`)
- [ ] Limitations documented (see Known Limitations below)
- [ ] Screenshots captured (see `docs/screenshots/INSTRUCTIONS.md`)
- [ ] Product walkthrough reviewed (see Product Walkthrough section above)
- [ ] Final evaluation report updated (`docs/74_final_evaluation_report.md`)

### Optional (non-blocking)
- [ ] E2E smoke tests passed (`make ui-e2e-product`)
- [ ] Full pre-release gate (`make prepare-release`)
- [ ] Obsidian vault backfill

## Known Limitations

### CI & Environment

| Limitation | Impact | Blocks delivery? | Mitigation | Future |
|---|---|---|---|---|
| CI only tests on Ubuntu | Windows/macOS not tested | No | CI uses Ubuntu (GitHub hosted) | Add matrix build |
| Pre-commit hooks not auto-installed | Hooks don't run automatically | No | Documented in README | Auto-install via setup.py |
| Integration tests excluded from CI | Qdrant/PG tests manual only | Yes for release readiness | Run Docker Compose Postgres + Qdrant locally before release | Add service containers to CI |
| Playwright requires manual browser install | E2E doesn't run without `npx playwright install` | No | Separate target, documented | Add CI E2E stage |

### Product Intelligence

| Limitation | Impact | Blocks delivery? | Mitigation | Future |
|---|---|---|---|---|
| Pipeline uses deterministic heuristics, not LLM | Less flexible than human judgment | No | Deterministic = auditable, testable | Add optional LLM judge |
| Scores depend on public evidence quality | Startups with low web presence get lower scores | No | Confidence penalty signals uncertainty | Improve source connectors |
| Evidence confidence is heuristic | May not reflect true reliability | No | Rule-based, transparent | Add learned calibration |
| `recommended_motion` is preliminary | Not a final business decision | No | Explicitly documented | Add human review workflow |
| Opportunity Score weights are judgment-based | May not reflect real priorities | No | All weights documented in contract | Calibrate against outcomes |

### Validation & Testing

| Limitation | Impact | Blocks delivery? | Mitigation | Future |
|---|---|---|---|---|
| Acceptance tests excluded from `make validate` | Full flow test requires `make acceptance` | No | Documented; `prepare-release` includes both | Evaluate merging |
| No frontend unit tests | Only E2E covers UI | No (acceptable v1) | Backend tests cover API | Add Vitest |
| No React Router | No deep-linking or browser navigation | No (acceptable v1) | State-based navigation | Add React Router |
| Golden fixture is minimal | Edge cases in unit tests | No | Unit/integration tests cover edge cases | Enrich fixture |
| Acceptance tests can use SQLite in `APP_MODE=test` | PostgreSQL is required for product mode | Yes for product release readiness | Run product acceptance with Docker Compose Postgres before release | Add PG CI job |

### User Interface (v1 limitations)

| Limitation | Impact | Blocks delivery? | Mitigation | Future |
|---|---|---|---|---|
| Discovery candidates limited to 100 | Pagination missing | No | Documented | Add pagination |
| Workflow view read-only | Can't create workflow from UI | No | API trigger works | Add UI button |
| Export view shows curl commands, no trigger | Requires terminal | No | Commands documented | Add UI export button |
| No batch opportunity compute | Must compute per analysis run | No | API handles it | Add batch endpoint |

### RAG & Vector Store

| Limitation | Impact | Blocks delivery? | Mitigation | Future |
|---|---|---|---|---|
| RAG requires `[rag]` extra in product mode | Product readiness blocks without real embeddings | Yes | Install `pip install -e ".[rag]"` and set `RAG_EMBEDDING_MODEL` | Keep model/version audit current |
| QdrantStore no auto-fallback to in-memory | Qdrant offline = product readiness failure | Yes | Start Qdrant and ingest corpus | Add managed deployment recipe |
| Context packing limits (2/3/5) | May drop relevant contexts in edge cases | No | Configurable via `PackingConfig` | Evaluate dynamic limits |
| Reranking is deterministic, no cross-encoder | May miss semantic relevance | No | Transparent formula | Add optional cross-encoder |
| No multi-turn RAG queries | Single-shot retrieval only | No | Adequate for briefs | Add interactive mode |

### Codebase & Process

| Limitation | Impact | Blocks delivery? | Mitigation | Future |
|---|---|---|---|---|
| Obsidian vault has structure but minimal content | Research notes not backfilled | No | Manual process documented | Automate backfill |
| `check_scope.py` uses `git diff HEAD` | May behave unexpectedly during rebase | No | Override flag available | Improve robustness |
| `src/agents/` and `src/interface/` remain stubs | Agent framework not implemented | No | Not required for product flow | Implement v1 agents |
| No human review workflow | Review is single-decision only | No | Appendix-only audit log | Add review workflow |
| No PDF export | JSON and Markdown only | No | Adequate for delivery | Add PDF generation |
