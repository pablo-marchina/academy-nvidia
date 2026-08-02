# Production Runbook — NVIDIA Startup AI Radar

This runbook is the authoritative way to build, start, validate, operate, and stop the complete product stack.

## 1. What the release starts

A single `docker compose up` starts the implemented design rather than a reduced demo:

- PostgreSQL for product records, audit history, workflow state, and the LangGraph checkpointer;
- Alembic migrations before application startup;
- Qdrant with the governed NVIDIA corpus;
- an idempotent corpus bootstrap that downloads the configured embedding model only when the collection is not ready;
- NVIDIA Triton serving the `cross_encoder` reranker;
- FastAPI with liveness/readiness probes and migration checks;
- a durable PostgreSQL-backed workflow worker;
- the React/Vite frontend served by Nginx;
- an internal trusted-proxy boundary so the browser never receives the API proxy secret.

The first corpus bootstrap uses `BAAI/bge-m3` and the Triton build preloads `cross-encoder/ms-marco-MiniLM-L-6-v2`. Keep enough disk and memory available for these models and the container images.

## 2. Requirements

- Docker Desktop with Docker Compose v2;
- Git;
- Windows PowerShell 7 or a POSIX shell;
- outbound access to Docker Hub, NVIDIA NGC, Hugging Face, and any API providers enabled in `.env`;
- on a public server, TLS termination in front of port 3000 and firewall rules that do not expose PostgreSQL, Qdrant, or Triton to the internet.

The stack runs the reranker on CPU by default. A compatible NVIDIA GPU can be added later through Compose device reservations without changing the API contract.

## 3. Configure the release

### PowerShell

```powershell
git clone https://github.com/pablo-marchina/academy-nvidia.git
cd academy-nvidia
git checkout improve/dashboard-output-performance
Copy-Item .env.example .env

# Generate a random 48-byte trusted-proxy secret and replace the placeholder.
$proxyKey = [Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))
(Get-Content .env) `
  -replace 'replace-with-a-random-value-of-at-least-32-characters', $proxyKey |
  Set-Content .env
```

Open `.env` and configure the providers you intend to use. For the complete NVIDIA path, set at least `NVIDIA_API_KEY`. Add `SERPAPI_API_KEY`, `FIRECRAWL_API_KEY`, or `GITHUB_TOKEN` only when those governed collectors are enabled. Never commit `.env`.

The database credentials in `.env.example` deliberately match `docker-compose.yml`. Change them together before deploying outside a local machine.

## 4. Build and start everything

```powershell
docker compose pull postgres qdrant
docker compose up --build -d
```

Observe the release bootstrap:

```powershell
docker compose ps
docker compose logs -f migrate rag-bootstrap triton-reranker api workflow-worker frontend
```

`migrate` and `rag-bootstrap` are one-shot services. A successful completed state is expected. The API and worker start only after migrations, corpus readiness, and Triton readiness succeed.

## 5. Validate the running release

### Container and liveness status

```powershell
docker compose ps
Invoke-RestMethod http://localhost:3000/health
Invoke-RestMethod http://localhost:3000/api/health/live
```

### Full readiness

```powershell
$ready = Invoke-RestMethod http://localhost:3000/api/health/ready
$ready | ConvertTo-Json -Depth 10
if (-not $ready.ready) { throw 'Product readiness gate failed' }
```

A release is ready only when all of these are available:

- PostgreSQL responds and its Alembic revision equals repository head;
- the local NVIDIA corpus passes freshness validation;
- Qdrant has the calibrated collection, payload, corpus version, and embedding dimension;
- Triton reports the `cross_encoder` model ready;
- all required product capabilities pass the central readiness gate.

### Inspect individual dependencies

```powershell
Invoke-RestMethod http://localhost:3000/api/health/product | ConvertTo-Json -Depth 10
Invoke-RestMethod http://localhost:3000/api/health/dependencies | ConvertTo-Json -Depth 10
Invoke-RestMethod http://localhost:3000/api/workflows/langgraph-status
```

## 6. Execute the real product workflow

Create a startup with at least one real, entity-specific source. Replace the sample data with the company being analyzed.

```powershell
$startupBody = @{
  name = 'Example AI Startup'
  website = 'https://example.com'
  country = 'Brazil'
  sector = 'Enterprise AI'
  description = 'Evidence-backed description of the company.'
  product_summary = 'The company deploys an LLM application in production.'
  status = 'active'
  tags = @('llm', 'enterprise-ai')
  evidence = @(
    @{
      claim = 'The company operates an LLM product.'
      source_url = 'https://example.com/product'
      source_type = 'official_site'
      quote_or_evidence = 'Replace this with a verifiable excerpt from the official product page.'
      confidence = 'high'
      metadata = @{}
    }
  )
} | ConvertTo-Json -Depth 10

$startup = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:3000/api/startups `
  -ContentType 'application/json' `
  -Body $startupBody
```

Queue the only production workflow. The API returns HTTP 202 immediately; PostgreSQL preserves the run and the worker executes LangGraph.

```powershell
$workflow = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:3000/api/workflows/product-runs `
  -ContentType 'application/json' `
  -Body (@{ startup_id = $startup.id; use_rag = $true } | ConvertTo-Json)

$workflowId = $workflow.id
```

Poll persisted state rather than keeping a long HTTP request open:

```powershell
do {
  Start-Sleep -Seconds 2
  $workflow = Invoke-RestMethod "http://localhost:3000/api/workflows/product-runs/$workflowId"
  Write-Host "$($workflow.status) — $($workflow.current_node)"
} while ($workflow.status -in @('queued', 'running'))

$workflow | ConvertTo-Json -Depth 20
if ($workflow.status -notin @('completed', 'degraded', 'awaiting_review')) {
  throw "Workflow ended with status $($workflow.status): $($workflow.error_message)"
}
```

Inspect node-level execution:

```powershell
Invoke-RestMethod "http://localhost:3000/api/workflows/product-runs/$workflowId/nodes" |
  ConvertTo-Json -Depth 10
```

When a run requests human review, retrieve its payload, submit a documented decision, and resume it through the existing review endpoints. The PostgreSQL checkpointer preserves the interrupt state.

## 7. Use the dashboard

Open:

```text
http://localhost:3000
```

For incremental discovery and population, keep the default batch at five companies and source budget at five. Increase them only after observing source success rate and latency. The dashboard read limit is independent from the analysis batch.

## 8. Release validation commands

Run these before tagging a release:

```powershell
python -m pip install -e '.[dev,full,observability]'
ruff check src tests scripts
pytest -q
docker compose config --quiet
docker compose build api frontend triton-reranker
docker compose run --rm migrate
docker compose run --rm rag-bootstrap
```

Then run the readiness and real-workflow checks from sections 5 and 6. A green unit suite without a ready corpus, Triton model, current migration, worker, and real persisted workflow is not a valid production release.

## 9. Updating the NVIDIA corpus

After changing governed corpus files or `sources.yaml`:

```powershell
docker compose run --rm rag-bootstrap python scripts/ingest_nvidia_corpus.py `
  --recreate-collection `
  --require-real-embeddings `
  --fail-on-validation-error

docker compose restart api workflow-worker
```

Confirm `/api/health/ready` again before accepting new work.

## 10. Operations

Useful commands:

```powershell
# Logs
docker compose logs -f api workflow-worker

# Restart stateless services
docker compose restart api workflow-worker frontend

# Apply a new repository revision
docker compose build api frontend triton-reranker
docker compose run --rm migrate
docker compose up -d

# Stop without deleting data
docker compose down

# Destructive reset — removes PostgreSQL, Qdrant, model and product volumes
docker compose down -v
```

Back up the `postgres_data`, `qdrant_data`, and `product_data` volumes before upgrades. Do not use `down -v` in production unless a full reset is intentional.

## 11. Release acceptance criteria

A release is accepted only when:

1. CI, offline evaluation, migration verification, frontend build, and Compose validation are green;
2. all required containers are healthy and one-shot bootstrap services completed successfully;
3. `/api/health/ready` returns HTTP 200 with `ready=true`;
4. a real company can be created, queued, processed by the worker, and retrieved after completion;
5. every recommendation has company-specific evidence and citation-ready NVIDIA context;
6. no company exceeds the bounded recommendation/technology limits;
7. unsupported workload families and generic directory contamination are absent;
8. the dossier, brief, claims, gaps, scores, mappings, readiness records, and audit history are persisted and visible;
9. restarting API and worker does not lose workflow state;
10. the public deployment uses TLS, backups, secret rotation, and network isolation.
