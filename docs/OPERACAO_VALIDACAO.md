# Operação, Validação e Critérios de Aceite

## Objetivo

Este documento define como configurar, executar, validar e diagnosticar o produto em ambiente local ou de entrega. O foco é garantir que o runtime real esteja pronto, sem mocks, sem shortcuts e com ranking global de startups.

## Pré-requisitos

```text
Python >= 3.11
Node.js compatível com frontend/package.json
Docker e Docker Compose
PostgreSQL
Qdrant
NVIDIA Triton Inference Server para reranker em produção
```

## Setup inicial

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[full,scraping,rag,agent-orchestration,postgres,observability,security]"
cp .env.example .env
npm --prefix frontend ci
```

Subir serviços locais:

```bash
docker compose up -d postgres qdrant
alembic upgrade head
```

## Configuração mínima de produto

`.env` deve conter:

```text
APP_MODE=product
PRODUCT_DB_URL=postgresql+psycopg2://radar:radar@localhost:5432/nvidia_radar
LANGGRAPH_CHECKPOINTER=postgres
LANGGRAPH_POSTGRES_URL=postgresql://radar:radar@localhost:5432/nvidia_radar
WORKFLOW_NODE_MAX_RETRIES=2

RAG_REQUIRED_FOR_PRODUCT=true
RAG_VECTOR_BACKEND=qdrant
RAG_RETRIEVAL_MODE=bm25_graphrag_qdrant_triton_rerank
RAG_EMBEDDING_MODEL=BAAI/bge-m3
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=nvidia_corpus
QDRANT_VECTOR_SIZE=1024

BM25_ENABLED=true
GRAPHRAG_ENABLED=true
TRITON_RERANKER_ENABLED=true
TRITON_RERANKER_REQUIRED=true
TRITON_RERANKER_URL=http://localhost:8000/v2/models/nvidia-reranker/infer
```

## Ingestão e validação do corpus

```bash
python scripts/ingest_nvidia_corpus.py --clear
python scripts/check_rag_corpus_coverage.py
python scripts/check_reranker_ready.py
```

Critérios:

```text
coleção Qdrant existe
vetores têm dimensão 1024
corpus local tem chunks ativos
fontes NVIDIA têm url/source_id/version
BM25, GraphRAG e Triton estão ativos
```

## Executar produto

Backend:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
npm --prefix frontend run dev
```

Health checks:

```bash
curl http://localhost:8000/health/product
curl http://localhost:8000/product/readiness
curl http://localhost:8000/workflows/langgraph-status
```

## Fluxo operacional completo

### 1. Discovery

```text
POST /discovery/manual-seed
GET  /discovery/candidates
```

### 2. Promoção

```text
POST /discovery/candidates/{candidate_id}/promote
```

### 3. Workflow

```text
POST /workflows/product-runs
GET  /workflows/product-runs/{workflow_id}
GET  /workflows/product-runs/{workflow_id}/nodes
```

### 4. Revisão humana se necessário

```text
GET  /workflows/{workflow_id}/review-payload
POST /workflows/{workflow_id}/resume
```

### 5. Score e ranking

```text
POST /analysis-runs/{analysis_run_id}/opportunity-score
GET  /opportunities/ranked
```

## Validação rápida

```bash
python -m compileall -q src
python -m pytest -m "not (integration or acceptance or e2e or slow or optional or external_service)" --tb=short
npm --prefix frontend run typecheck
npm --prefix frontend run build
```

## Validação de produto

```bash
python scripts/check_product_configuration.py --actual-env-only
python scripts/check_single_runtime_pipeline.py
python scripts/check_no_mock_runtime.py
python scripts/check_docs_match_runtime.py
python scripts/product_doctor.py
python scripts/product_acceptance_report.py --api-url http://localhost:8000
```

## Validação de release

```bash
make validate-full
make acceptance-backend
make package-final-release
python scripts/check_final_release_zip.py
```

## Checklist de aceite final

| Critério | Como verificar |
|---|---|
| API sobe sem erro | `GET /health/product` |
| Readiness sem blockers | `GET /product/readiness` |
| LangGraph disponível | `GET /workflows/langgraph-status` |
| PostgreSQL usado | `PRODUCT_DB_URL` e migrations aplicadas |
| Checkpointer persistente | `LANGGRAPH_POSTGRES_URL` e `APP_MODE=product` |
| Qdrant pronto | `scripts/check_rag_corpus_coverage.py` |
| Triton pronto | `scripts/check_reranker_ready.py` |
| Discovery cria candidatos | `GET /discovery/candidates` |
| Workflow cria node timeline | `GET /workflows/product-runs/{id}/nodes` |
| RAG usa modo oficial | `rag_retrieval_metrics.retrieval_mode` |
| Recomendações são geradas | `ranked_recommendations` no run |
| Quality run existe | `GET /analysis-runs/{id}/quality-summary` |
| Opportunity score existe | `GET /analysis-runs/{id}/opportunity-score` |
| Ranking global lista startups | `GET /opportunities/ranked` |
| Ledger existe | `data/decision_ledger.csv` |

## Troubleshooting

### `APP_MODE=product requires a persistent LangGraph Postgres checkpointer`

Causa: o runner não conseguiu construir `PostgresSaver`.

Correções:

```text
verificar LANGGRAPH_POSTGRES_URL
verificar PRODUCT_DB_URL
subir PostgreSQL
instalar extras postgres/agent-orchestration
rodar migrations
```

### `TRITON_RERANKER_URL is required for production reranking`

Causa: Triton reranker obrigatório sem URL.

Correções:

```text
subir Triton Inference Server
configurar TRITON_RERANKER_URL
validar endpoint /v2/models/{model}/infer
rodar scripts/check_reranker_ready.py
```

### `Qdrant collection is empty`

Causa: corpus não foi ingestado ou Qdrant usa collection errada.

Correções:

```bash
python scripts/ingest_nvidia_corpus.py --clear
```

Verificar:

```text
QDRANT_URL
QDRANT_COLLECTION
QDRANT_VECTOR_SIZE
RAG_EMBEDDING_MODEL
```

### Workflow fica `awaiting_review`

Isso pode ser esperado. Verifique:

```text
GET /workflows/{workflow_id}/review-payload
GET /analysis-runs/{analysis_run_id}/quality-summary
GET /analysis-runs/{analysis_run_id}/evidence-coverage
```

Depois retome:

```text
POST /workflows/{workflow_id}/resume
```

### Ranking global vazio

Causas comuns:

```text
nenhum workflow concluído
analysis_run_id não possui opportunity score
OpportunityScoreRecord não foi criado
filtros min_score/tier removem tudo
UI está consultando endpoint errado
```

Correção:

```text
POST /analysis-runs/{analysis_run_id}/opportunity-score
GET /opportunities/ranked?limit=50
```

### Quality falha por claims sem suporte

Causa: claims críticos não têm evidência suficiente.

Ações:

```text
inspecionar /analysis-runs/{id}/claims
inspecionar /analysis-runs/{id}/evidence-bundle
reexecutar coleta com mais fontes
revisar fontes oficiais e independentes
```

## Métricas mínimas para monitorar

```text
workflow_runs.status
workflow_node_runs.retry_count
workflow_node_runs.status
rag_retrieval_metrics.retrieved_context_count
rag_retrieval_metrics.citation_ready_context_count
quality overall_status
unsupported critical claims
opportunity_score
score_tier
```

## Não aceitar como entrega final

```text
workflow sem PostgreSQL
workflow sem Qdrant
RAG desabilitado
Triton ausente em APP_MODE=product
ranking hardcoded
startup única hardcoded
mock de API no frontend
recommendation sem evidência/contexto RAG
decision ledger ausente
quality gates ignorados
```
