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
- `src/evaluation/` — Offline RAG evaluation (golden queries, metrics, quality gates, multi-mode comparison, **reranking/packed**)
- `src/config/` — settings via pydantic-settings
- `scripts/` — validation and quality gate scripts (check_scope, check_docs_closure, validate)

### Testing
- 375 tests (337 unit + 38 golden evals + 12 skippable integration) across 37 test files
- All scoring modules have scenario-based tests (Portuguese-named golden examples)
- Gap diagnosis: 14 tests covering 10/15 gaps individually + end-to-end + missing evidence
- NVIDIA mapping: coverage verified for all 15 gaps (each has ≥1 technology mapped)
- Recommendation engine: 22 tests covering action matrix, priority, experiments, per-gap, and full integration
- Pipeline integration: 10 tests covering full flow with gaps, recommendations, weak evidence, missing_evidence propagation, and extended output shape
- RAG ingestion: 4 tests (sources, corpus, chunking, metadata)
- RAG retrieval: 6 tests (index, gap, tech, empty, keywords, scores)
- Playbook retriever: 5 tests (inference gap, agent gap, missing, brief dicts, no-rag crash)
- RAG Evaluation: 20 tests (golden queries, metrics, quality gates, provenance, brief compatibility)
- RAG Embeddings: 11 tests (mock provider, determinism, normalization, batch)
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
- Check Scope: 7 tests (sensitive changes require docs, override flag, contract detection)
- Check Docs Closure: 6 tests (plan, ROADMAP, EVALS, Obsidian checks)

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
- Streamlit for a future MVP interface

## Installation

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and developer dependencies:

```bash
pip install -e ".[dev]"
playwright install
```

## Environment Configuration

Copy `.env.example` to `.env` and fill in the keys you actually need for local development.

Important variables:

- `OPENAI_API_KEY`
- `NVIDIA_API_KEY`
- `COHERE_API_KEY`
- `DATABASE_URL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`

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
```

## CI/CD

GitHub Actions CI runs on push/PR to `main`:

- `ruff check .`
- `black --check .`
- `mypy src`
- `pytest -m "not integration"`

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

The API scaffold is intentionally minimal at this stage. Once dependencies are installed, run:

```bash
uvicorn src.main:app --reload
```

## Using the Obsidian Vault

The project includes an Obsidian knowledge-capture workspace in [obsidian-vault](/C:/Users/Inteli/Documents/Projetos/academy-nvidia/obsidian-vault). Use it for research capture, evidence notes, daily logs, and draft decisions.

Rule of thumb:

- Obsidian is the lab.
- The repository is production.

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
- RAG semantic/hybrid retrieval requires `sentence-transformers` for real embeddings (mock provider used in tests).
- RAG evaluation multi-mode comparison uses `MockEmbeddingProvider` by default — real semantic quality requires `sentence-transformers`.
- Corpus is manually curated in `data/nvidia_corpus/` (10 documents — no automated ingestion).
- Relevance scoring in lexical mode is keyword-match-based; semantic mode uses cosine similarity; reranking uses a deterministic composite formula (no cross-encoder).
- Vector store is in-memory only (no persistence across sessions — Qdrant-ready for production; optional QdrantStore adapter available in Epic 15).
- Context packing uses configurable limits (per-tech=2, per-gap=3, global=5) — may drop relevant contexts in edge cases.
- RAG pipeline integrated as optional Step 11 — no support for multi-turn or interactive context queries.
- QdrantStore does not auto-fallback to in-memory on connection error (caller must catch `QdrantConnectionError`).
- Automated ingestion script at `scripts/ingest_nvidia_corpus.py` handles corpus → Qdrant pipeline with validation, hashing, embeddings, and provenance preservation.
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
