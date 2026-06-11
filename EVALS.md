# EVALS — Baseline de Testes e Cobertura

## Testes Unitários

| Módulo | Arquivo | Testes | Status |
|---|---|---|---|
| Schemas | `tests/unit/test_schemas.py` | 4 | ✅ |
| Source Policy | `tests/unit/test_source_policy.py` | 3 | ✅ |
| Fetcher | `tests/unit/test_fetcher.py` | 7 | ✅ |
| Parser | `tests/unit/test_parser.py` | 4 | ✅ |
| Extractor | `tests/unit/test_extractor.py` | 14 | ✅ |
| AI Classifier | `tests/unit/test_classifier.py` | 10 | ✅ |
| Evidence Validator | `tests/unit/test_evidence_validator.py` | 14 | ✅ |
| Defensibility Score | `tests/unit/test_defensibility_score.py` | 6 | ✅ |
| Inception Fit Score | `tests/unit/test_inception_fit_score.py` | 6 | ✅ |
| Production Readiness | `tests/unit/test_production_readiness.py` | 6 | ✅ |
| Composite Ranking | `tests/unit/test_composite_ranking.py` | 9 | ✅ |
| Gap Diagnosis | `tests/unit/test_gap_diagnosis.py` | 14 | ✅ |
| NVIDIA Mapping | `tests/unit/test_nvidia_mapping.py` | 6 | ✅ |
| Gap Taxonomy | `tests/unit/test_gap_taxonomy.py` | 1 | ✅ |
| Pipeline | `tests/unit/test_pipeline.py` | 10 | ✅ |
| Recommendation Engine | `tests/unit/test_recommendation_engine.py` | 22 | ✅ |
| Action Brief | `tests/unit/test_action_brief.py` | 10 | ✅ |
| RAG Ingestion | `tests/unit/test_rag_ingestion.py` | 4 | ✅ |
| RAG Retrieval | `tests/unit/test_rag_retrieval.py` | 6 | ✅ |
| Playbook Retriever | `tests/unit/test_playbook_retriever.py` | 5 | ✅ |
| RAG Evaluation | `tests/unit/test_rag_eval.py` | 20 | ✅ |
| RAG Embeddings | `tests/unit/test_rag_embeddings.py` | 15 | ✅ |
| Semantic Retrieval | `tests/unit/test_semantic_retrieval.py` | 15 | ✅ |
| Hybrid Retrieval | `tests/unit/test_hybrid_retrieval.py` | 12 | ✅ |
| RAG Evaluation Semantic | `tests/unit/test_rag_eval_semantic.py` | 14 | ✅ |
| RAG Reranking | `tests/unit/test_rag_reranking.py` | 9 | ✅ |
| Context Packing | `tests/unit/test_context_packing.py` | 13 | ✅ |
| RAG Eval Reranking | `tests/unit/test_rag_eval_reranking.py` | 11 | ✅ |
| Action Brief RAG Context | `tests/unit/test_action_brief_rag_context.py` | 5 | ✅ |
| Pipeline RAG Integration | `tests/unit/test_pipeline_rag.py` | 10 | ✅ |
| Qdrant Store Unit | `tests/unit/test_qdrant_store.py` | 20 | ✅ |
| Qdrant Pipeline Integration | `tests/integration/test_qdrant_rag_pipeline.py` | 9 | ⏭️ (skippable) |
| Corpus Freshness Audit | `tests/unit/test_corpus_freshness_audit.py` | 11 | ✅ |
| Check Scope | `tests/unit/test_check_scope.py` | 7 | ✅ |
| Check Docs Closure | `tests/unit/test_check_docs_closure.py` | 7 | ✅ |
| Regression Dashboard | `tests/unit/test_regression_dashboard.py` | 14 | ✅ |
| Answer Quality Eval | `tests/evals/test_answer_quality_golden.py` | 9 | ✅ |
| Optional LLM Judge | `tests/unit/test_llm_judge_adapter.py` | 4 | ✅ |
| Output Validation Gate (Epic 26.2) | `tests/unit/test_output_validation.py` | 12 | ✅ |
| CLI Demo Integration (Epic 24) | `tests/integration/test_cli_demo.py` | 6 | ⏭️ (integration) |
| API Demo Integration (Epic 25) | `tests/integration/test_api_demo.py` | 9 | ⏭️ (integration) |
| **Total** | **45 arquivos** | **506** | **494 pass, 12 skip** |

## Cobertura por módulo

| Módulo | Implementado? | Testado? | Testes |
|---|---|---|---|
| `extraction/schemas.py` | ✅ REAL | ✅ | 4 |
| `extraction/extractor.py` | ✅ REAL | ✅ | 14 |
| `scraping/source_policy.py` | ✅ REAL | ✅ | 3 |
| `scraping/fetcher.py` | ✅ REAL | ✅ | 7 |
| `scraping/parser.py` | ✅ REAL | ✅ | 4 |
| `classification/ai_native_classifier.py` | ✅ REAL | ✅ | 10 |
| `validation/evidence_validator.py` | ✅ REAL | ✅ | 14 |
| `scoring/defensibility_score.py` | ✅ REAL | ✅ | 6 |
| `scoring/inception_fit_score.py` | ✅ REAL | ✅ | 6 |
| `scoring/production_readiness.py` | ✅ REAL | ✅ | 6 |
| `scoring/composite_ranking.py` | ✅ REAL | ✅ | 9 |
| `pipeline/run_pipeline.py` | ✅ REAL | ✅ | 10 |
| `briefing/action_brief.py` | ✅ REAL | ✅ | 10 |
| `briefing/schemas.py` | ✅ REAL | ✅ | (via action brief) |
| `recommendation/schemas.py` | ✅ REAL | ✅ | (via recommendation engine) |
| `recommendation/recommendation_engine.py` | ✅ REAL | ✅ | 22 |
| `diagnosis/gap_diagnosis.py` | ✅ REAL | ✅ | 9 |
| `diagnosis/nvidia_mapping.py` | ✅ REAL | ✅ | 6 |
| `config/settings.py` | ✅ REAL | ❌ | 0 |
| `agents/` (9 files) | ❌ STUB | ❌ | 0 |
| `rag/` (10 files) | ✅ REAL | ✅ | 15 + 56 (Epic 13) + 22 (Epic 14) + 10 (Epic 14.1) + 20 (Epic 15) |
| `database/` (2 files) | ❌ STUB | ❌ | 0 |
| `evaluation/` (9 files) | ✅ REAL | ✅ | 20 + 14 (Epic 13) + 11 (Epic 14) + 9 (Epic 23 answer quality) + 4 (Epic 23.2 optional judge) |
| `interface/` (1 file) | ❌ STUB | ❌ | 0 |
| `scripts/check_scope.py` | ✅ REAL | ✅ | 7 |
| `scripts/check_docs_closure.py` | ✅ REAL | ✅ | 7 |
| `scripts/build_regression_dashboard.py` | ✅ REAL | ✅ | 14 |
| `validation/output_validation.py` | ✅ REAL | ✅ | 12 |

## Lacunas de cobertura

- **Integração:** `tests/integration/` tem 9 testes Qdrant (skippable via QDRANT_TEST_URL)
- **Config:** `src/config/settings.py` sem testes
- **Novos scripts:** `scripts/check_scope.py` e `scripts/check_docs_closure.py` testados (14 testes)

## Critérios de aceite por módulo

| Módulo | Critério | Status |
|---|---|---|
| Schemas | Validação de enums e criação de objetos | ✅ |
| Scraping | HTTP mocked, parser com fallback | ✅ |
| Extractor | Perfil completo, parcial, vazio, sinais AI | ✅ |
| Classifier | 5 níveis + evidência fraca | ✅ |
| Evidence Validator | 14 cenários de fonte/tipo/confiança | ✅ |
| Defensibility Score | 5 cenários + shape test | ✅ |
| Inception Fit Score | 5 cenários + shape test | ✅ |
| Production Readiness | 6 cenários (alto/baixo/sem evidência) | ✅ |
| Composite Ranking | Pesos, redistribuição, motion, ranking | ✅ |
| Gap Diagnosis | 7 gaps + inferência + evidência faltante | ✅ |
| NVIDIA Mapping | Gap conhecido/desconhecido, cobertura total | ✅ |
| Recommendation Engine | 22 testes (ação, prioridade, experimento, per-gap, integração) | ✅ |
| Pipeline | 10 testes (5 existentes + 5 integração: diagnóstico, recomendação, evidência fraca, missing_evidence, shape estendido) | ✅ |
| Action Brief | 10 testes (high-fit, evidência fraca, sem gap, missing evidence, tech sem gap, incertezas, markdown, schema, JSON, low confidence) | ✅ |
| RAG Ingestion | 4 testes (sources, corpus load, chunking metadata, source propagation) | ✅ |
| RAG Retrieval | 6 testes (index, gap, tech, empty, keywords, scores) | ✅ |
| Playbook Retriever | 5 testes (inference gap, agent gap, missing, brief dicts, no-rag) | ✅ |
| RAG Evaluation | 20 testes (golden queries, metrics, quality gates, provenance, compatibility) | ✅ |
| RAG Embeddings | 15 testes (mock provider, determinismo, normalização, batch, custom size, erro claro sem `sentence-transformers`, compatibilidade de métodos de dimensão) | ✅ |
| Semantic Retrieval | 15 testes (contextos, proveniência, store vazio, filtros por product/gap/source_id, top_k, score range, query text building) | ✅ |
| Hybrid Retrieval | 12 testes (fallback lexical, fusão RRF, proveniência, top_k, score range, filtros, fusão vazia/dedup) | ✅ |
| RAG Evaluation Semantic | 14 testes (mode eval lexical/semantic/hybrid, comparison, regressions, format, backward compat) | ✅ |
| RAG Reranking | 9 testes (gap/tech boost, provenance/duplicate/irrelevant penalties, empty, config, score range, order) | ✅ |
| Context Packing | 13 testes (dedup, per-tech/per-gap/global limits, provenance, empty, dropped reasons, metrics, build_supporting) | ✅ |
| RAG Eval Reranking | 11 testes (5 modos, packed metrics, regression detection, backward compat) | ✅ |
| Action Brief RAG Context | 5 testes (RAG-optional, context injection, empty default, motion unchanged) | ✅ |
| Pipeline RAG Integration | 10 testes (pipeline com packed contexts, sem RAG, empty index, brief section, dropped not in brief, motion unchanged, provenance, quality summary, backward compat, lexical mode) | ✅ |
| Qdrant Store Unit | 20 tests (lazy conn, error, add, remove, clear, get, size, search, filters, provenance, factory) | ✅ |
| Qdrant Pipeline Integration | 9 tests (upsert, filters, remove, clear, get, provenance, error) | ⏭️ skippable |
| Ingest NVIDIA Corpus | 17 tests (hash, CLI, dry-run, ingest in-memory, payload, report) | ✅ |
| Qdrant Corpus Ingestion | 3 tests (ingest, recreate, idempotence) | ⏭️ skippable |
| Corpus Freshness Audit | 11 tests (stale, expired, deprecated, superseded, missing metadata, duplicate active versions, fail flags, version promotion, retrieval/vector filters) | ✅ |
| Regression Dashboard | 14 tests (clean PASS, stale WARN, validation_errors FAIL, missing reports WARN, JUnit missing context parsing, Answer Quality JUnit pass/failure/error/skipped/missing, Optional LLM Judge present/absent, Markdown sections, JSON fields) | ✅ |
| Answer Quality Eval | 9 tests (golden answer quality pass, missing required section, missing evidence omitted, uncertainty omitted, technology without gap, motion change, unsupported claims, low citation coverage, absolute language warning) | ✅ |
| Output Validation Gate | 12 tests (valid brief, missing section, invalid motion, invalid gap, invalid NVIDIA technology, missing evidence, recommendation without evidence, dashboard required metrics, Markdown TODO warning, empty critical section, API warnings, low-confidence uncertainty) | ✅ |

## Critérios de Qualidade do Desenvolvimento

Estes critérios avaliam a **qualidade do processo de desenvolvimento assistido por IA**, não a qualidade do produto.

| Critério | O que verifica | Como medir |
|----------|---------------|------------|
| Plano salvo | Plano foi versionado em `docs/plans/` antes do build | Verificar se existe arquivo .md para o épico/tarefa |
| Escopo respeitado | Mudanças estão dentro do escopo aprovado | Review Diff: nenhum arquivo fora do escopo |
| Contratos consultados | Contratos foram lidos antes de alterar módulos | Agente declara quais contratos leu (ou justifica por que não) |
| Clarification Gate respeitado | IA perguntou antes de gerar quando havia ambiguidade (ou registrou menor escopo seguro) | Verificar log da conversa: perguntas com formato correto, ≤3, com defaults |
| Output Validation Gate respeitado | Outputs estruturados foram validados antes de concluir tarefa | Verificar validators/Makefile aplicáveis, warnings/failures reportados e hotfix trivial justificado |
| Review Diff executado | Diff foi revisado antes do commit | Log da execução do review_diff.md |
| Obsidian atualizado | Notas de decisão, resumo e limitações foram criadas/atualizadas | Verificar existência de notas em 03 Research/, 04 Decisions/, 02 Project Control/ |
| Decisões registradas | Decisões arquiteturais ou de processo foram registradas | DECISIONS.md ou ADR em docs/adr/ |
| Limitações registradas | Known Limitations foi revisado e atualizado | Diff no arquivo Known Limitations |
| Validações executadas | pytest, ruff, black, mypy rodaram sem erros (ou com erros pre-existentes justificados) | Log dos comandos |
| ERROR_LOG atualizado | Erros relevantes foram registrados | Conteúdo de ERROR_LOG.md (não vazio se houve erros) |
| Alucinação zero | Nenhuma fonte, tecnologia ou feature foi inventada | Revisão manual do diff e do reasoning |
| Feature fantasma zero | Nenhuma feature foi documentada sem ser implementada | Comparar docs com código real |

### Alvos
- **Curto prazo:** 100% dos épicos não triviais terão plano salvo, Review Diff executado, Obsidian atualizado
- **Médio prazo:** Review Diff detecta 0 falsos negativos (nada fora de escopo passa)
- **Longo prazo:** Developer RAG implementado com recall@5 ≥90%

## CI/CD Quality Gates

| Gate | Ferramenta | Onde roda | Falha bloqueia? |
|------|-----------|-----------|-----------------|
| Ruff lint | `ruff check .` | CI, pre-commit, `make lint` | ✅ |
| Black format | `black --check .` | CI, pre-commit, `make format-check` | ✅ |
| Mypy typecheck | `mypy src` | CI, `make typecheck` | ✅ |
| Unit tests | `pytest` | CI, `make test` | ✅ |
| Scope check | `python scripts/check_scope.py` | Manual (antes do commit) | ⚠️ (overridable) |
| Docs closure | `python scripts/check_docs_closure.py` | Manual (antes de fechar épico) | ⚠️ (overridable) |
| Pre-commit hooks | `.pre-commit-config.yaml` | `git commit` (se instalado) | ✅ |
| Full validation | `make validate` / `scripts/validate.sh` | Local (antes do commit) | ✅ |
| Regression dashboard | `make regression-dashboard` | Local e corpus maintenance workflow | ⚠️ WARN não bloqueia; FAIL bloqueia no workflow |

### Gatilhos
- **Push/PR para main:** CI roda automaticamente (ruff, black, mypy, pytest)
- **git commit (local):** pre-commit hooks rodam se instalados
- **Antes do commit (agente IA):** `make validate` + `python scripts/check_scope.py`
- **Antes de fechar épico:** `python scripts/check_docs_closure.py`

## Golden Evals (Epic 17)

### Casos Golden

| Case | Motion | Score | Gaps Detectados | Testes |
|------|--------|-------|-----------------|--------|
| startup_high_fit | `lack_evidence_more_research` | 17.6 | 7 (healthcare, latency, vision, etc.) | 10 |
| startup_weak_evidence | `not_recommended` | 1.2 | 0 | 4 |
| startup_non_ai | `not_recommended` | 2.8 | 0 | 4 |
| startup_no_rag_context | `lack_evidence_more_research` | 29.4 | 8 | 4 |
| startup_rag_supported | `lack_evidence_more_research` | 9.7 | 1 | 4 |
| startup_validate_manually | `lack_evidence_more_research` | 3.9 | 0 | 5 |
| startup_monitor_or_discard | `lack_evidence_more_research` | 4.8 | 7 | 4 |

### Invariantes Verificados (por golden case)
1. Pipeline Contract — todos os campos obrigatórios presentes e válidos
2. Expected Motion — `recommended_motion` dentro da faixa esperada
3. Score Range — `final_priority_score` entre min_score e max_score
4. Expected Gaps — gaps detectados incluem os esperados
5. No Tech Without Gap — recomendações sem gap detectado não têm tecnologias
6. Missing Evidence Propagation — `missing_evidence` propaga de diagnosis → pipeline result
7. Confidence Coherence — high confidence sem evidência high não produz composite high
8. Action Brief Sections — mínimo de seções + Executive Summary + Evidence
9. Action Brief Markdown — renderização markdown válida
10. No Strong Rec Without Evidence — `approach_now` só com HIGH confidence evidence
11. RAG: Motion Stability — RAG não altera `recommended_motion`
12. RAG: Context in Brief — `supporting_nvidia_context` e `packed_rag_contexts` presentes
13. RAG: Context Not in Evidence — conteúdo RAG não aparece em `evidence_used`

### Execução
```bash
pytest tests/evals/ -v          # golden evals apenas
pytest tests/evals/ --tb=short  # com saída enxuta
```

### Regressão
Se um golden case falhar:
1. Verificar se a mudança no pipeline foi intencional
2. Rodar pipeline no golden case para ver novo output
3. Atualizar `expected_outputs.json` e o campo `expected` no JSON do caso
4. Re-executar `pytest tests/evals/` para confirmar

## Answer Quality Evals (Epic 23)

### Casos Golden

| Case | Pipeline case | Foco |
|------|---------------|------|
| high_fit_supported_answer | startup_high_fit | evidence, gaps, techs, RAG citations |
| weak_evidence_preserved | startup_weak_evidence | missing_evidence and low-confidence honesty |
| non_ai_no_nvidia_push | startup_non_ai | no NVIDIA push without gaps |
| rag_context_good_gap | startup_rag_supported | RAG context citation coverage |
| gap_without_rag_context | startup_no_rag_context | gap honesty without required RAG source |
| low_confidence_validate_manually | startup_validate_manually | uncertainty preservation |
| irrelevant_or_conflicting_rag_context | startup_rag_supported | unsupported-claim detection |
| required_missing_evidence | startup_monitor_or_discard | missing evidence as a gate |

### Métricas

`required_sections_present`, `missing_evidence_preserved`,
`uncertainty_preserved`, `recommended_motion_consistent`,
`required_evidence_ids_present`, `required_gap_ids_present`,
`required_technology_ids_present`, `unsupported_claim_count`,
`rag_context_citation_coverage`, `startup_evidence_citation_coverage`,
`forbidden_absolute_language_count`, `answer_quality_status`.

### Execução

```bash
pytest tests/evals/test_answer_quality_golden.py -q
pytest tests/evals/test_answer_quality_golden.py --junit-xml=data/regression_reports/answer_quality_eval_junit.xml
make answer-quality-junit
```

Sem chamadas externas, sem LLM judge, sem Qdrant obrigatório.

## Optional LLM Judge (Epic 23.2)

### Execução

```bash
make answer-quality-llm-judge
python scripts/run_answer_quality_llm_judge.py --max-cases 1
```

### Reports

- `data/regression_reports/answer_quality_llm_judge_report.json`
- `data/regression_reports/answer_quality_llm_judge_report.md`

### Testes

- 4 unitarios cobrindo provider nulo offline, agregacao de report, prompt com contexto/resposta/evidencias/rubrica e script manual gerando JSON/Markdown.

### Invariantes

- Provider real nao implementado.
- Sem chamadas externas, sem chave de API e sem dependencia nova.
- Report ausente no dashboard e `INFO`, nao `WARN` ou `FAIL`.
- O judge opcional nao altera JUnit, quality gates deterministicas, scoring, diagnosis, recommendation, retrieval ou Action Brief.

## Ingestion (Epic 18)

### Script
```bash
python scripts/ingest_nvidia_corpus.py              # ingestao real (Qdrant)
python scripts/ingest_nvidia_corpus.py --dry-run     # validacao sem upsert
python scripts/ingest_nvidia_corpus.py --mock-embeddings --backend in_memory  # offline
```

### Payload Qdrant por chunk
| Campo | Descricao |
|-------|-----------|
| `chunk_id` | Deterministico: `{source_id}_{index:03d}` |
| `content_hash` | MD5 do documento completo |
| `chunk_hash` | MD5 do conteudo do chunk |
| `version` | Versao do source |
| `document_type` | Tipo do documento |
| `provenance` | `{source_url, source_title}` |
| `ingestion_run_id` | Identificador unico da execucao |

### Testes
- 17 unitarios (backend in_memory, sem Qdrant)
- 3 integracao (skippable — requer QDRANT_TEST_URL)

## Metricas aspiracionais (futuras)

- Precision@k para ranking de startups
- Recall@k para cobertura de evidências
- Faithfulness de diagnósticos vs julgamento especialista
- Business usefulness score (survey time NVIDIA)

## Source Sync (Epic 19)

### Script
`ash
python scripts/sync_nvidia_sources.py --dry-run           # validar allowlist
python scripts/sync_nvidia_sources.py --staging-only       # baixar para staging
python scripts/sync_nvidia_sources.py --source-id nim --promote  # sync + promote
python scripts/sync_nvidia_sources.py --promote --report-path report.json
`

### Testes
- 49 unitarios (all mocked — zero chamadas externas)
- Coverage: allowlist validation, CLI, fetcher, robots.txt, dry-run, staging, promote, hash, report

### Fluxo
`
allowlist --> fetch (rate limit, robots.txt) --> staging --> hash compare --> promote (opcional)
`

## Corpus Freshness Audit (Epic 20)

### Script
```bash
python scripts/audit_nvidia_corpus_freshness.py --format json
python scripts/audit_nvidia_corpus_freshness.py --format markdown --report-path corpus_audit.md
python scripts/audit_nvidia_corpus_freshness.py --fail-on-stale
python scripts/audit_nvidia_corpus_freshness.py --fail-on-expired
```

### Testes
- 11 unitarios (offline, sem Qdrant, sem chamadas externas)
- Coverage: stale, expired, deprecated, superseded, missing metadata, duplicate active versions, report counters, fail flags, version promotion, retrieval filter, vector-store filter

### Invariantes
- Retrieval padrao exclui inactive/deprecated/superseded/expired
- `sources.yaml` permite multiplas versoes por `source_id`
- Apenas uma versao ativa por `source_id`, salvo excecao futura explicita

## Corpus Maintenance Workflow (Epic 21)

### Script
```bash
python scripts/run_corpus_maintenance.py
python scripts/run_corpus_maintenance.py --no-run-ingestion --run-evals
python scripts/run_corpus_maintenance.py --run-ingestion
```

### Reports
- `maintenance_summary.json`
- `source_sync_dry_run.json`
- `freshness_audit.json`
- `qdrant_ingest_dry_run.json`
- `qdrant_ingestion.json`, se `run_ingestion=true`
- `rag_eval_junit.xml`, se `run_evals=true`
- `golden_eval_junit.xml`, se `run_evals=true`
- `answer_quality_eval_junit.xml`, quando `run_evals=true`
- stdout/stderr logs por etapa

### Validacao
- Script local validado por execucao em modo seguro.
- Sem novos testes unitarios porque o escopo aprovado do Epic 21 nao inclui `tests/`; a cobertura operacional fica registrada pelos reports e pelos quality gates existentes.

### Invariantes
- Ingestao real nao roda por default.
- Schedule nao promove fontes.
- Schedule nao ingere Qdrant real.
- `fail_on_expired=true` por default.

## Regression Dashboard (Epic 22)

### Script
```bash
python scripts/build_regression_dashboard.py
python scripts/build_regression_dashboard.py --reports-dir reports/corpus-maintenance/<run-id>
make regression-dashboard
```

### Reports
- `data/regression_reports/latest_dashboard.md`
- `data/regression_reports/latest_dashboard.json`

### Testes
- 14 unitarios cobrindo PASS, WARN, FAIL, reports ausentes, JUnit, Optional LLM Judge, secoes Markdown e campos JSON.

### Invariantes
- `FAIL` para `validation_errors`, `sources_failed`, `expired_sources`, RAG eval failure, golden eval failure ou answer quality eval failure quando `answer_quality_eval_junit.xml` existir.
- `WARN` para `stale_sources`, `missing_context_count`, `missing_evidence_count`, reports ausentes ou Answer Quality JUnit ausente.
- Optional LLM Judge e informativo: report ausente ou presente nao altera status global do dashboard.
- GitHub Actions publica summary/artifact antes de falhar por `FAIL`.
- `WARN` nao falha workflow.

## Output Validation Gate (Epic 26.2)

### Execução

```bash
make validate-output
make validate-brief-output
make validate-dashboard-output
python -m pytest tests/unit/test_output_validation.py --tb=short
```

### Testes

- 12 unitarios cobrindo Action Brief valido, secao obrigatoria ausente, motion invalido, gap invalido, tecnologia NVIDIA invalida, `missing_evidence` ausente, recomendacao sem evidencia, dashboard sem metrica obrigatoria, Markdown com TODO, secao critica vazia, API warnings preservados e baixa confianca sem incerteza.

### Invariantes

- Action Brief deve preservar contrato, secoes criticas, gaps validos, tecnologias NVIDIA mapeadas, evidencia, `missing_evidence` e incerteza quando confidence for baixa.
- Markdown com placeholder gera `WARN` controlado; secao critica vazia gera `FAIL`.
- Dashboard precisa expor status `PASS/WARN/FAIL` e metricas obrigatorias.
- API responses sao validadas por schemas Pydantic existentes; response type desconhecido gera `WARN`.
- A gate nao altera scoring, retrieval, recommendation, Action Brief generation, API/UI behavior ou dependencias.
