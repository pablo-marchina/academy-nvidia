# Scheduled Corpus Maintenance Workflow

**Epic 21** | **Data:** 2026-06-10

## Objetivo

Automatizar a manutencao controlada do corpus NVIDIA sem publicar mudancas ruins
silenciosamente. O workflow roda sync dry-run, auditoria de freshness, ingestao
Qdrant dry-run, ingestao real opcional, RAG evals, golden evals e coleta reports
como artifacts.

Este epico nao adiciona crawler, nao altera retrieval, embeddings, scoring,
diagnosis, recommendation, briefing ou `recommended_motion`.

## Entrypoints

### GitHub Actions

Workflow: `.github/workflows/corpus-maintenance.yml`

- `workflow_dispatch`: execucao manual com inputs explicitos.
- `schedule`: execucao semanal segura, sem promocao de fontes e sem ingestao real.

### Local

Script:

```bash
python scripts/run_corpus_maintenance.py
```

Makefile:

```bash
make corpus-maintenance-dry-run
make corpus-maintenance-evals
make corpus-maintenance-ingest
```

## Inputs e Defaults

| Input | Default | Efeito |
|---|---:|---|
| `run_sync` | `true` | Roda `sync_nvidia_sources.py --dry-run`. |
| `run_ingestion` | `false` | Roda ingestao real no Qdrant apenas quando `true`. |
| `run_evals` | `true` | Roda RAG evals e golden evals. |
| `promote_sources` | `false` | Roda sync com `--promote` apenas se explicitamente habilitado. |
| `recreate_collection` | `false` | Passa `--recreate-collection` para ingestao real. |
| `fail_on_stale` | `false` | Falha auditoria se houver fontes stale. |
| `fail_on_expired` | `true` | Falha auditoria se houver fontes expiradas. |

## Sequencia

1. Source sync dry-run:
   `python scripts/sync_nvidia_sources.py --dry-run --fail-on-validation-error`
2. Freshness audit:
   `python scripts/audit_nvidia_corpus_freshness.py --format json`
3. Qdrant ingest dry-run:
   `python scripts/ingest_nvidia_corpus.py --dry-run --mock-embeddings`
4. Qdrant ingestion real, apenas com `run_ingestion=true`.
5. RAG evals, apenas com `run_evals=true`.
6. Golden evals, apenas com `run_evals=true`.
7. Upload de reports/artifacts no GitHub Actions.

## Reports

O script cria reports em `reports/corpus-maintenance/<run-id>/` por padrao.

Arquivos esperados:

- `source_sync_dry_run.json`
- `source_sync_promote.json`, apenas se `promote_sources=true`
- `freshness_audit.json`
- `qdrant_ingest_dry_run.json`
- `qdrant_ingestion.json`, apenas se `run_ingestion=true`
- `rag_eval_junit.xml`, apenas se `run_evals=true`
- `golden_eval_junit.xml`, apenas se `run_evals=true`
- `*.stdout.log` e `*.stderr.log` por etapa
- `maintenance_summary.json`

No GitHub Actions, o artifact se chama `corpus-maintenance-reports`.

## Qdrant

O workflow sobe Qdrant local via Docker Compose somente quando a ingestao real esta
habilitada:

```bash
docker compose up -d qdrant
```

O dry-run de ingestao valida documentos, chunking e construcao de entradas usando
`--mock-embeddings`, sem carregar modelo real nem fazer upsert. A ingestao real,
quando explicitamente habilitada, usa a configuracao normal do script de ingestao.

## Seguranca

- A ingestao real nao roda por default.
- O schedule sempre usa `run_ingestion=false` e `promote_sources=false`.
- Nao ha auto-commit.
- Nao ha publicacao externa de reports.
- Nao ha secrets obrigatorios.
- O sync continua limitado a `source_allowlist.yaml`, respeitando os controles do
  Epic 19.
- `fail_on_expired=true` por default impede que fonte expirada passe em modo
  silencioso.

## Testes e Validacao

O escopo aprovado do Epic 21 nao inclui novos arquivos em `tests/`. A validacao do
novo script e feita por execucao local em modo seguro, alem dos gates:

```bash
pytest
ruff check .
black --check .
mypy src
```

## Limitacoes

- O schedule nao revisa nem commita mudancas; um humano ainda deve inspecionar
  reports antes de promover fontes ou ingerir real.
- O workflow nao executa testes de integracao Qdrant; a ingestao real depende do
  Qdrant local iniciado no runner.
- RAG evals continuam usando os testes deterministicos existentes.
