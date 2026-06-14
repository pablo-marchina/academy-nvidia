# Final Architecture Summary — NVIDIA Startup AI Radar

**Versão:** 1.0
**Data:** 2026-06-13
**Épico:** 45

## Visão Geral

O NVIDIA Startup AI Radar é uma plataforma multiagente determinística que identifica startups brasileiras AI-native, coleta evidências públicas, diagnostica maturidade técnica e recomenda tecnologias NVIDIA. A arquitetura é modular, testável e opera sem dependência de LLM para seu core scoring.

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Product UI (Vite + React + TS)           │
│  Setup │ Capabilities │ Discovery │ Startups │ Workflow         │
│  Opportunities │ Dossier │ Quality │ Export                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP (fetch)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Product API (30+ endpoints)           │
│  /product/* │ /startups/* │ /analysis-runs/* │ /opportunities   │
│  /discovery/* │ /workflows/* │ /exports/* │ /health/*           │
└──────┬──────────────────┬──────────────────┬────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│ Product DB   │  │ Workflow        │  │ Discovery Engine     │
│ SQLite/PG    │  │ Orchestration   │  │ 6 sources, signals,  │
│ Alembic migs │  │ 11-node runner  │  │ dedup, promote       │
│ 12 tables    │  │ LangGraph opt.  │  │                      │
└──────────────┘  └────────┬────────┘  └──────────────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │    Pipeline (11 steps)    │
              │   Deterministic, offline  │
              │                          │
              │  1. Extract              │
              │  2. Classify (AI-native) │
              │  3. Validate evidence    │
              │  4. Defensibility Score  │
              │  5. Inception Fit Score  │
              │  6. Production Readiness │
              │  7. Composite Ranking    │
              │  8. Gap Diagnosis (15)   │
              │  9. NVIDIA Tech Mapping  │
              │ 10. Recommendation       │
              │ 11. RAG (optional)       │
              └──────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
   ┌────────────────┐ ┌──────────┐ ┌──────────────┐
   │ Claim Ledger   │ │ Quality  │ │ Opportunity  │
   │ Deterministic  │ │ Layer    │ │ Score        │
   │ evidence→claim │ │ 6+ evals │ │ 10 components│
   └────────────────┘ └──────────┘ └──────────────┘
              │            │            │
              ▼            ▼            ▼
   ┌────────────────┐ ┌──────────┐ ┌──────────────────┐
   │ Activation     │ │ Dossier  │ │ RAG (optional)   │
   │ Playbooks      │ │ Versioned│ │ Hybrid dense+    │
   │ 10 YAML-based  │ │ JSON+MD  │ │ sparse + BM25    │
   └────────────────┘ └──────────┘ └──────────┬───────┘
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │ Qdrant (opt.)  │
                                     │ Vector store   │
                                     │ + in-memory    │
                                     └────────────────┘
```

## Componentes

### Product API
- FastAPI com CORS, lifespan, 4 routers (product, workflow, demo legacy, health)
- 30+ endpoints REST com schemas Pydantic
- Swagger UI em `/docs`
- Health endpoints: `/health/product`, `/health/dependencies`

### Product DB
- SQLAlchemy ORM com SQLite (default) e PostgreSQL (suportado)
- Alembic para migrations versionadas (7 migrations)
- 12 tabelas: Startup, Evidence, AnalysisRun, ActionBrief, ReviewDecision, ExportRecord, ClaimRecord, ActivationRecommendationRecord, ActivationDossierRecord, OpportunityScoreRecord, WorkflowRun, WorkflowNodeRun
- `PRODUCT_DB_URL` configurável via ambiente

### Discovery Engine
- 6 fontes de descoberta: manual_seed, configured_url_list, distrito, ace, bossa, inovativa
- Signal detection com 30+ keywords AI-native
- Dedup por nome normalizado + domínio
- Ciclo de vida DiscoveryRun (queued/running/completed/degraded/failed)
- Promoção de candidato a Startup com migração de evidências

### Workflow Orchestration
- 11-node sequential runner (fallback) + LangGraph opcional
- Nodes: load_startup, collect_evidence, validate_evidence, diagnose_gaps, retrieve_nvidia_context, map_technologies, generate_claims, match_playbooks, generate_dossier, run_quality, summarize_readiness
- Retry por node (max 1), degraded/failed propagation
- State persistence com tracing por node

### Hybrid RAG
- Retrieval modes: dense_only, sparse_only, hybrid, hybrid_with_rerank
- BM25 sparse retriever + dense embeddings (sentence-transformers)
- RRF + weighted score fusion
- Deterministic reranking (composite score + provenance/duplicate penalties)
- Context packing (dedup, gap/tech limits, provenance filtering)
- Qdrant opcional para persistência de vectors
- Fallback in-memory quando Qdrant indisponível

### Claim Ledger
- Geração determinística de claims a partir de registros persistidos
- Evidence coverage metrics: `total_claims`, `supported_claims`, `unsupported_claims`
- Suporte a human review de claims

### Activation Playbooks
- 10 playbooks em YAML (inference, latency, agent, data, CV, voice, simulation, robotics, security, private deployment)
- Matching determinístico por gap_type
- Confidence score com boost/penalty por mapping, claims, degraded state

### Opportunity Score
- 10 componentes ponderados: composite ranking, evidence coverage, gap resolution, NVIDIA mapping, activation readiness, dossier completeness, quality score, claim support, review status, production readiness
- 8 tipos de penalidade: claims, evidence, degraded, contraindication, non_ai, low confidence, incomplete data
- Score tiers: critical/high/medium/low/not_recommended
- Weight redistribution quando componente ausente

### Activation Dossier
- Versionado (JSON + Markdown), gerado deterministicamente
- Projeta: startup, scores, gaps, mappings, activation playbooks, claims, reviews, readiness checks
- Idempotente — `force=true` para regenerar

### Product Quality
- 6+ evaluators: structured output reliability, RAG retrieval, config registry, capability registry
- Quality thresholds por métrica com pass/fail
- Quality summary com overall_status

### Product UI
- 10 views: Setup, Capabilities, Discovery, Startups, Opportunities, Workflow, Export, Quality + StartupDetail, AnalysisRun
- Vite + React + TypeScript, estado local (sem React Router)
- Consome Product API real, não lê data/demo_runs
- Playwright E2E smoke tests (6 testes)

### Validation
- Makefile com 15+ targets
- CI/CD: GitHub Actions (ruff, black, mypy, pytest)
- Pre-commit hooks (ruff, black, trailing-whitespace, etc.)
- Scope check (`scripts/check_scope.py`)
- Docs closure check (`scripts/check_docs_closure.py`)
- No demo dependency check (`scripts/check_no_demo_dependency.py`)

## Dados Persistidos

| Entidade | Tabela | FK |
|---|---|---|
| Startup | `startups` | — |
| Evidence | `evidences` | startup_id |
| AnalysisRun | `analysis_runs` | startup_id |
| ActionBrief | `action_briefs` | analysis_run_id |
| ReviewDecision | `review_decisions` | analysis_run_id |
| ExportRecord | `export_records` | analysis_run_id |
| ClaimRecord | `claim_records` | startup_id, analysis_run_id |
| ActivationRecommendation | `activation_recommendation_records` | analysis_run_id |
| ActivationDossier | `activation_dossier_records` | analysis_run_id |
| OpportunityScore | `opportunity_score_records` | analysis_run_id |
| WorkflowRun | `workflow_runs` | startup_id |
| WorkflowNodeRun | `workflow_node_runs` | workflow_run_id |

## Optional Features

| Feature | Extra pip | Config | Status if missing |
|---|---|---|---|
| RAG embeddings | `[rag]` | `RAG_EMBEDDING_MODEL` | `missing_dependency` |
| Qdrant vector store | — | `QDRANT_URL` | Fallback in-memory |
| LangGraph orchestration | `[agent-orchestration]` | `AGENT_ORCHESTRATION_ENABLED` | Sequential fallback |
| LLM Judge / Instructor | `[llm-judge]` | `ANSWER_QUALITY_LLM_JUDGE_ENABLED` | `not_configured` |

## Degraded State Handling

- Missing required config → `ready=false` (API), `missing_dependency` (capability)
- Missing optional feature → `not_configured` (capability), product continues
- Pipeline exception → persisted `failed` AnalysisRun com error_message
- Qdrant offline → degraded (se configurado), fallback in-memory (se não)
- RAG não configurado → degraded state em analysis runs com `use_rag=true`
