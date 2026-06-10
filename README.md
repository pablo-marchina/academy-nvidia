# NVIDIA Startup AI Radar — Opportunity Intelligence for NVIDIA Inception

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
11. **Product RAG** retrieves NVIDIA documentation snippets (lexical, in-memory) to enrich briefs with grounded, provenance-tracked context.
12. **RAG Evaluation** offline evaluation layer with golden queries, 7 retrieval metrics, and 6 quality gates for the Product RAG module.

See [docs/00_case_plan.md](docs/00_case_plan.md) for the full case plan and [docs/02_architecture.md](docs/02_architecture.md) for the architectural flow.

## Current Capabilities

### Pipeline (11-step deterministic flow)
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
- `src/rag/` — Product RAG ingestion, lexical retrieval, playbook retriever
- `src/evaluation/` — Offline RAG evaluation (golden queries, metrics, quality gates)
- `src/config/` — settings via pydantic-settings

### Testing
- 188 unit tests across 21 test files
- All scoring modules have scenario-based tests (Portuguese-named golden examples)
- Gap diagnosis: 14 tests covering 10/15 gaps individually + end-to-end + missing evidence
- NVIDIA mapping: coverage verified for all 15 gaps (each has ≥1 technology mapped)
- Recommendation engine: 22 tests covering action matrix, priority, experiments, per-gap, and full integration
- Pipeline integration: 10 tests covering full flow with gaps, recommendations, weak evidence, missing_evidence propagation, and extended output shape
- RAG ingestion: 4 tests (sources, corpus, chunking, metadata)
- RAG retrieval: 6 tests (index, gap, tech, empty, keywords, scores)
- Playbook retriever: 5 tests (inference gap, agent gap, missing, brief dicts, no-rag crash)
- RAG Evaluation: 20 tests (golden queries, metrics, quality gates, provenance, brief compatibility)

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
- RAG retrieval is purely lexical (no embeddings, no vector DB, no reranking).
- RAG evaluation uses golden queries and deterministic metrics — no LLM judge, no semantic understanding.
- Corpus is manually curated in `data/nvidia_corpus/` (10 documents — no automated ingestion).
- Relevance scoring is simple keyword-match-based, no semantic understanding.
- Recommendation Engine is deterministic (no LLM) and not yet integrated into the pipeline — deferred to Epic 10 (Briefing/CLI).
- Gap Diagnosis module (`src/diagnosis/gap_diagnosis.py`) exists but is not yet called by the pipeline — scores are available but not part of the output.
- Scores depend on the quality and coverage of public evidence available for the startup.
- Evidence confidence is assigned heuristically by rule-based validation, not by a learned model.
- The system does not prove real internal usage of AI — it only structures publicly available signals.
- `recommended_motion` is a preliminary suggestion based on deterministic rules, not a final business decision.
- No human-in-the-loop technically implemented (only documented in architecture plan).
- No integration tests exist — all 188 tests are unit tests.
- No eval harness exists — `tests/evals/` is empty.
- Agents (`src/agents/`), database (`src/database/`), and interface (`src/interface/`) are stubs.
- Obsidian vault has structure but no populated content beyond templates.
