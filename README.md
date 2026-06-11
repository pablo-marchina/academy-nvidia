# NVIDIA Startup AI Radar — Opportunity Intelligence for NVIDIA Inception

[![CI](https://github.com/anomalyco/academy-nvidia/actions/workflows/ci.yml/badge.svg)](https://github.com/anomalyco/academy-nvidia/actions/workflows/ci.yml)

NVIDIA Startup AI Radar transforma sinais públicos de startups brasileiras em um ranking acionável, combinando agentes de coleta, validação de evidências, classificação AI-native, Production AI Readiness, AI-Native Defensibility Score e NVIDIA Inception Fit Score. O sistema diagnostica production AI gaps, recupera playbooks NVIDIA via RAG e gera um Startup Action Brief com prioridade, evidências, tecnologias recomendadas, experimento técnico sugerido e próxima ação para o time de Startups & VCs.

## Objective

Build a reproducible, versioned, AI-oriented workspace that prioritizes traceability, evidence quality, structured outputs, and continuous evaluation before complex product features are implemented. O case completo está em [docs/00_case_plan.md](docs/00_case_plan.md).

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
11. **Product RAG** retrieves NVIDIA documentation snippets (lexical + semantic + hybrid) to enrich briefs with grounded, provenance-tracked context.
12. **RAG Evaluation** offline evaluation layer with golden queries, 7 retrieval metrics, and 6 quality gates for the Product RAG module.
13. **Reranking + Context Packing** deterministic reranking (composite score: gap/tech boost + provenance/duplicate/irrelevant penalties) and context packing (dedup, gap/tech limits, provenance filtering) for enriched, clean NVIDIA context in briefs.
14. **Persistent Vector Store (Qdrant)** optional Qdrant-backed vector store with lazy connection, full payload provenance, and server-side filtering — falls back to in-memory.
15. **CI/CD & Quality Gates** GitHub Actions CI (ruff, black, mypy, pytest), pre-commit hooks, Makefile targets, scope/documentation validation scripts.
16. **Source Sync** Allowlist-based download of NVIDIA documentation to staging with hash comparison, robots.txt verification, rate limiting, and optional promotion to the local corpus.
17. **Corpus Freshness & Versioning** Local lifecycle policy with source versions, active/deprecated flags, stale/expired audit, and default retrieval filtering for active non-expired corpus chunks.
18. **Scheduled Corpus Maintenance** Manual and scheduled-safe workflow that runs source sync dry-run, freshness audit, Qdrant ingest dry-run, optional real ingestion, RAG evals, golden evals, and artifact reports.
19. **Regression Dashboard** Local Markdown/JSON dashboard consolidating ingestion, freshness, RAG evals, golden evals, Action Brief checks, warnings, and regressions for GitHub Actions summaries.
20. **Answer Quality Evaluation** Offline deterministic harness for final RAG/Action Brief quality: required sections, missing evidence, uncertainty, motion stability, unsupported claims, and citation coverage.
21. **Optional LLM Judge Adapter** Experimental/manual answer quality judge interface with offline null provider and informational JSON/Markdown reports.

See [docs/00_case_plan.md](docs/00_case_plan.md) for the full case plan and [docs/02_architecture.md](docs/02_architecture.md) for the architectural flow.

## Current Capabilities

### Pipeline (12-step deterministic flow, RAG optional)
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
12. **Product RAG (optional)** — hybrid retrieval (lexical/semantic), deterministic reranking, context packing, provenance tracking

13. **CI/CD & Quality Gates** — GitHub Actions (ruff, black, mypy, pytest), pre-commit hooks, Makefile targets, scope-check and docs-closure verification scripts.

### Modules implemented
- `src/scraping/` — fetcher, parser, source policy
- `src/extraction/` — extractor, schemas (Pydantic)
- `src/classification/` — AI-native classifier (heuristic)
- `src/validation/` — evidence validator (deterministic)
- `src/scoring/` — defensibility, inception fit, production readiness, composite ranking
- `src/pipeline/` — pipeline orchestrator (run_full_pipeline)
- `src/diagnosis/` — gap diagnosis (15 detectors) + NVIDIA technology mapping
- `src/recommendation/` — deterministic recommendation engine (schemas, engine)
- `src/briefing/` — Startup Action Brief consolidation and Markdown rendering
- `src/rag/` — Product RAG ingestion, lexical + semantic + hybrid retrieval, embeddings, vector store, playbook retriever, **deterministic reranking, context packing, Qdrant persistent vector store**
- `src/evaluation/` — Offline RAG evaluation (golden queries, metrics, quality gates, multi-mode comparison, **reranking/packed**), deterministic Answer Quality evaluation, and optional experimental LLM judge adapter with offline null provider
- `src/config/` — settings via pydantic-settings
- `scripts/` — validation and quality gate scripts (check_scope, check_docs_closure, validate), Qdrant corpus ingestion, NVIDIA source sync, corpus freshness audit, corpus maintenance orchestration, regression dashboard generation

### Testing
- 511 Python tests (499 passing + 12 skippable integration) across 46 Python test files, plus 2 Playwright UI smoke tests
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

## Stack

- Python
- FastAPI
- Pydantic
- LangGraph
- PostgreSQL
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

## Environment Configuration

Copy `.env.example` to `.env` and fill in the keys you actually need for local development.

Important variables:

- `OPENAI_API_KEY`
- `NVIDIA_API_KEY`
- `COHERE_API_KEY`
- `DATABASE_URL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`
- `QDRANT_VECTOR_SIZE` (default `384`, matching the default RAG embedding model)
- `RAG_EMBEDDING_MODEL` (default `sentence-transformers/all-MiniLM-L6-v2`)
- `RAG_VECTOR_BACKEND`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`

## Running the CLI Demo

The project includes an end-to-end CLI demo that runs the full pipeline on a
sample startup and generates a Startup Action Brief.

### Basic demo

```bash
python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json
```

### Offline mode (no Qdrant, no external deps)

```bash
python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json --offline
```

### With local RAG (InMemoryVectorStore)

```bash
python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json --use-rag --rag-backend local
```

### With answer quality evaluation

```bash
python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json --run-answer-quality-eval
```

### Makefile targets

```bash
make demo-cli           # basic demo
make demo-cli-offline   # offline mode
make demo-cli-rag       # with local RAG
```

### Outputs

All files are written to `data/demo_runs/latest/`:

- `startup_action_brief.md` — Markdown brief
- `startup_action_brief.json` — JSON brief
- `demo_run_report.json` — run metadata and timing
- `answer_quality_eval.json` — optional quality evaluation

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
make ui-dev      # run the local demo UI
make ui-build    # build the local demo UI
make ui-e2e      # run Playwright smoke tests for the local demo UI
make demo-acceptance  # API acceptance + UI build + UI E2E smoke
make demo-full-check  # alias for demo-acceptance
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

The project includes a minimal FastAPI demo API that exposes the pipeline, brief generation, and answer quality evaluation via HTTP endpoints.

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

### Available endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/version` | Project version info |
| `GET` | `/rag/status` | RAG backend configuration and Qdrant availability |
| `POST` | `/brief` | Generate a Startup Action Brief |
| `POST` | `/brief/evaluate` | Evaluate brief answer quality (PASS/WARN/FAIL) |
| `GET` | `/demo/artifacts` | List generated demo artifacts |

### Example request

```bash
curl -X POST http://localhost:8000/brief \
  -H "Content-Type: application/json" \
  -d '{
    "startup_name": "Nexus AI Labs",
    "profile": {"sector": "HealthTech", "description": "AI healthcare platform"},
    "evidence": [{"claim": "Deep learning in production", "confidence": "high"}],
    "offline": true
  }'
```

### Swagger UI

Open http://localhost:8000/docs in your browser.

### API tests

```bash
make api-test
# or
pytest tests/integration/test_api_demo.py -v
```

## Running the Minimal Demo UI

The project includes a local Vite + React demo UI under `frontend/`. It consumes
the FastAPI demo API and does not duplicate scoring, diagnosis, recommendation,
RAG retrieval, Qdrant ingestion, or answer quality logic.

### Configure UI

```bash
cd frontend
cp .env.example .env
```

Default API URL:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Start API and UI

Terminal 1:

```bash
make api-dev
```

Terminal 2:

```bash
make ui-install
make ui-dev
```

Open the Vite URL, usually http://127.0.0.1:5173.

### UI demo flow

1. Click `Load example`.
2. Keep `Offline mode` enabled for the simplest local demo.
3. Click `Generate Startup Action Brief`.
4. Review scorecards, gaps, NVIDIA technologies, evidence, warnings,
   uncertainties, RAG status, and Markdown output.
5. Click `Evaluate brief` to run optional answer quality evaluation.

### UI build

```bash
make ui-build
```

### Demo acceptance

Run the repeatable API + UI smoke suite:

```bash
make demo-acceptance
```

This runs API acceptance tests, the frontend build, and Playwright smoke tests.
The default path is offline and does not require Qdrant or LLM calls. Qdrant
offline must appear as status/warning, not as a demo crash.

If Playwright browsers are not installed locally, run:

```bash
cd frontend
npx playwright install chromium
```

See [docs/52_demo_acceptance.md](docs/52_demo_acceptance.md) for the automated
coverage and manual fallback checklist.

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

## Known Limitations

- The pipeline uses deterministic heuristics, not an LLM, for all scoring and diagnosis steps.
- Scraping collects from a single public URL — no crawling in scale.
- RAG semantic/hybrid retrieval requires the optional `rag` extra for real embeddings: `pip install -e ".[rag]"` (mock provider used in tests).
- RAG evaluation multi-mode comparison uses `MockEmbeddingProvider` by default — real semantic quality requires `sentence-transformers`.
- Qdrant ingestion with the default `sentence-transformers/all-MiniLM-L6-v2` model uses 384-dimensional vectors, so `QDRANT_VECTOR_SIZE` must remain `384` for that collection.
- Corpus is local and allowlist-backed in `data/nvidia_corpus/`; scheduled maintenance is safe by default and does not promote sources or run real ingestion unless explicitly requested in a manual workflow run.
- Regression dashboard quality is limited by the reports available in the run; missing reports are surfaced as `WARN`, and JUnit-based eval reports expose pass/fail and failed cases rather than full retrieval metrics.
- Answer quality evaluation is deterministic and pattern-based; it checks required structure, provenance, motion stability, and known unsupported-claim patterns, but it is not a semantic LLM judge.
- Output validation is structural and contract-focused; it does not replace human review or semantic judgment, and unknown output types return controlled warnings rather than hard failures.
- Optional LLM judge reports are experimental and informational; Epic 23.2 implements only an offline null provider, no real provider integration, no API calls, and no CI gate.
- Minimal Demo UI is local/dev only, has no authentication or deploy workflow, and now has a narrow Playwright smoke suite rather than broad frontend unit coverage.
- Relevance scoring in lexical mode is keyword-match-based; semantic mode uses cosine similarity; reranking uses a deterministic composite formula (no cross-encoder).
- Vector store is in-memory only (no persistence across sessions — Qdrant-ready for production; optional QdrantStore adapter available in Epic 15).
- Context packing uses configurable limits (per-tech=2, per-gap=3, global=5) — may drop relevant contexts in edge cases.
- RAG pipeline integrated as optional Step 11 — no support for multi-turn or interactive context queries.
- QdrantStore does not auto-fallback to in-memory on connection error (caller must catch `QdrantConnectionError`).
- Automated ingestion script at `scripts/ingest_nvidia_corpus.py` handles corpus → Qdrant pipeline with validation, hashing, embeddings, and provenance preservation.
- Corpus freshness audit at `scripts/audit_nvidia_corpus_freshness.py` runs offline and detects stale, expired, deprecated, superseded, missing metadata, and duplicate active versions.
- Recommendation Engine is deterministic (no LLM) — now fully integrated in the pipeline.
- Gap Diagnosis module (`src/diagnosis/gap_diagnosis.py`) exists but is not yet called by the pipeline — scores are available but not part of the output.
- Scores depend on the quality and coverage of public evidence available for the startup.
- Evidence confidence is assigned heuristically by rule-based validation, not by a learned model.
- The system does not prove real internal usage of AI — it only structures publicly available signals.
- `recommended_motion` is a preliminary suggestion based on deterministic rules, not a final business decision.
- No human-in-the-loop technically implemented (only documented in architecture plan).
- Golden eval harness at `tests/evals/` with 38 tests across 7 golden cases.
- Agents (`src/agents/`), database (`src/database/`), and interface (`src/interface/`) are stubs.
- Obsidian vault has structure but no populated content beyond templates.
- CI only tests on Ubuntu — no Windows/macOS matrix in CI.
- Integration tests excluded from CI (require `QDRANT_TEST_URL`).
- Pre-commit hooks not auto-installed — developer must run `pre-commit install`.
- `check_scope.py` relies on `git diff` against HEAD — may behave unexpectedly during rebase.
