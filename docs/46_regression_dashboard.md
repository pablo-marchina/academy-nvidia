# Regression Dashboard

**Epic 22** | **Data:** 2026-06-10

## Objetivo

Consolidar os reports de manutencao do corpus NVIDIA em um dashboard local simples
em Markdown e JSON. O dashboard compara, em uma unica visao, ingestao, freshness,
RAG evals, golden evals e checks de Action Brief.
Tambem incorpora Answer Quality JUnit quando disponivel.

Este epico nao altera retrieval, Qdrant ingestion, scoring, diagnosis,
recommendation ou Action Brief logic.

## Entrypoints

### Local

```bash
make regression-dashboard
```

Ou diretamente:

```bash
python scripts/build_regression_dashboard.py
python scripts/build_regression_dashboard.py --reports-dir reports/corpus-maintenance/<run-id>
```

### GitHub Actions

O workflow `.github/workflows/corpus-maintenance.yml` executa o dashboard no final
da manutencao, mesmo se uma etapa anterior falhar. O Markdown gerado e anexado ao
`GITHUB_STEP_SUMMARY`, e os arquivos do dashboard sao enviados junto com o artifact
`corpus-maintenance-reports`.

## Inputs

O script le, quando existirem:

- `source_sync_dry_run.json`
- `source_sync_promote.json`
- `freshness_audit.json` ou freshness Markdown historico
- `qdrant_ingest_dry_run.json`
- `qdrant_ingestion.json`
- `rag_eval_junit.xml`
- `golden_eval_junit.xml`
- `answer_quality_eval_junit.xml`

Se `--reports-dir` nao for informado, o script tenta localizar o ultimo diretorio
em `reports/corpus-maintenance/`. Se nao houver reports, ainda gera dashboard com
status `WARN` e warnings explicitos.
Para Answer Quality, tambem existe fallback local para
`data/regression_reports/answer_quality_eval_junit.xml`, gerado por
`make answer-quality-junit`.

## Outputs

Arquivos canonicos:

- `data/regression_reports/latest_dashboard.md`
- `data/regression_reports/latest_dashboard.json`

O JSON contem:

- `status`: `PASS`, `WARN` ou `FAIL`
- `metrics`: contadores consolidados
- `warnings`: motivos nao bloqueantes
- `failures`: motivos bloqueantes
- `failed_cases`: casos falhos de RAG/golden evals quando extraidos de JUnit
- `failure_details`: mensagens resumidas de falhas/erros de JUnit
- `inputs`: reports encontrados ou ausentes

## Metricas

| Metrica | Origem principal |
|---|---|
| `documents_seen` | Qdrant ingest dry-run ou real ingestion |
| `documents_valid` | Qdrant ingest dry-run ou real ingestion |
| `documents_skipped` | Qdrant ingest dry-run ou real ingestion |
| `chunks_created` | Qdrant ingest dry-run ou real ingestion |
| `chunks_upserted` | Qdrant ingestion real |
| `sources_failed` | source sync e ingestion |
| `validation_errors` | source sync e ingestion |
| `stale_sources` | freshness audit |
| `expired_sources` | freshness audit |
| `deprecated_sources` | freshness audit |
| `rag_eval_passed` | `rag_eval_junit.xml` |
| `rag_eval_failed_cases` | `rag_eval_junit.xml` |
| `golden_eval_passed` | `golden_eval_junit.xml` |
| `golden_eval_failed_cases` | `golden_eval_junit.xml` |
| `answer_quality_junit_present` | `answer_quality_eval_junit.xml` |
| `answer_quality_tests` | `answer_quality_eval_junit.xml` |
| `answer_quality_failures` | `answer_quality_eval_junit.xml` |
| `answer_quality_errors` | `answer_quality_eval_junit.xml` |
| `answer_quality_skipped` | `answer_quality_eval_junit.xml` |
| `answer_quality_failed_cases` | `answer_quality_eval_junit.xml` |
| `answer_quality_status` | `answer_quality_eval_junit.xml` |
| `action_brief_required_sections_passed` | golden evals de Action Brief |
| `missing_context_count` | reports que exponham `missing_context` |
| `missing_evidence_count` | reports que exponham `missing_evidence` |

## Regras de Status

`FAIL` se qualquer regra bloqueante ocorrer:

- `validation_errors > 0`
- `sources_failed > 0`
- `expired_sources > 0`
- RAG eval falhar
- Golden eval falhar
- Answer Quality eval falhar (`failures > 0` ou `errors > 0`)

`WARN` se nao houver falhas, mas houver:

- `stale_sources > 0`
- `missing_context_count > 0`
- `missing_evidence_count > 0`
- reports ausentes ou malformados
- `answer_quality_eval_junit.xml` ausente quando o dashboard espera reports locais

`PASS` quando nao houver failures nem warnings.

## CI Behavior

O workflow usa `--no-fail-on-status` ao construir o dashboard para garantir que
Job Summary e artifact sejam publicados. A secao Answer Quality do Job Summary
mostra presenca do XML, status, testes, failures, errors e skipped. Depois disso, uma etapa final le
`latest_dashboard.json` e falha somente se `status == "FAIL"`.

Consequencias:

- `PASS`: workflow passa.
- `WARN`: workflow passa, mas o resumo mostra warnings.
- `FAIL`: workflow falha apos publicar summary e artifact.
- O XML `answer_quality_eval_junit.xml` e publicado dentro do artifact
  `corpus-maintenance-reports`.

## Limitacoes

- JUnit de pytest nao contem metricas detalhadas de RAG; o dashboard extrai apenas
  pass/fail e nomes de casos falhos.
- Answer Quality JUnit cobre status operacional dos testes; metricas semanticas
  detalhadas continuam no harness deterministico, nao no XML puro do pytest.
- Os checks de Action Brief sao derivados dos golden evals existentes; nao ha um
  runner separado de Action Brief.
- Reports ausentes viram `WARN`, nao `FAIL`, para preservar diagnostico em runs
  parciais.
