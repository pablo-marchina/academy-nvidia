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
| Demo Acceptance Integration (Epic 27) | `tests/integration/test_demo_acceptance.py` | 5 | ⏭️ (integration) |
| Demo UI E2E Smoke (Epic 27) | `tests/e2e/test_demo_ui.spec.ts` | 2 | Playwright |
| CLI Demo Integration (Epic 24) | `tests/integration/test_cli_demo.py` | 6 | ⏭️ (integration) |
| API Demo Integration (Epic 25) | `tests/integration/test_api_demo.py` | 9 | ⏭️ (integration) |
| Product Database (Epic 29) | `tests/unit/test_product_database.py` | 2 | ✅ |
| Product Repositories (Epic 29) | `tests/unit/test_product_repositories.py` | 3 | ✅ |
| Product Service (Epic 29) | `tests/unit/test_product_service.py` | 3 | ✅ |
| Product API Integration (Epic 29) | `tests/integration/test_product_api.py` | 2 | integration |
| Alembic Migrations (Epic 30) | `tests/unit/test_alembic_migrations.py` | 2 | ✅ |
| Review Repository (Epic 30) | `tests/unit/test_review_repository.py` | 3 | ✅ |
| Opportunity Service (Epic 30) | `tests/unit/test_opportunity_service.py` | 6 | ✅ |
| Export Service (Epic 30) | `tests/unit/test_export_service.py` | 6 | ✅ |
| Claim Repository (Epic 32) | `tests/unit/test_claim_repository.py` | 12 | ✅ |
| Claim Ledger Service (Epic 32) | `tests/unit/test_claim_ledger.py` | 9 | ✅ |
| Claim API Integration (Epic 32) | `tests/integration/test_claim_api.py` | 9 | integration |
| Product PATCH/Review/Export API Integration (Epic 30) | `tests/integration/test_product_patch_review_export.py` | 12 | integration |
| PostgreSQL Migration (Epic 30) | `tests/integration/test_postgres_migration.py` | 3 | skippable |
| Activation Playbook Loader (Epic 33) | `tests/unit/test_activation_playbook_loader.py` | 13 | ✅ |
| Activation Playbook Matcher (Epic 33) | `tests/unit/test_activation_playbook_matcher.py` | 9 | ✅ |
| Activation API Integration (Epic 33) | `tests/integration/test_activation_api.py` | 8 | integration |
| Dossier Repository (Epic 34) | `tests/unit/test_dossier_repository.py` | 7 | ✅ |
| Dossier Service (Epic 34) | `tests/unit/test_dossier_service.py` | 10 | ✅ |
| Dossier API Integration (Epic 34) | `tests/integration/test_dossier_api.py` | 8 | integration |
| Structured Outputs Unit (Epic 36) | `tests/unit/test_structured_outputs.py` | 30 | ✅ |
| Structured Outputs Integration (Epic 36) | `tests/integration/test_structured_outputs.py` | 4 | integration |
| Capability Registry (Epic 36.1) | `tests/unit/test_capability_registry.py` | 6 | ✅ |
| Config Registry (Epic 36.1) | `tests/unit/test_config_registry.py` | 9 | ✅ |
| Readiness Service (Epic 36.1) | `tests/unit/test_readiness_service.py` | 10 | ✅ |
| Product Readiness API (Epic 36.1) | `tests/integration/test_product_readiness_api.py` | 9 | integration |
| Product UI E2E Smoke (Epic 37) | `tests/e2e/test_product_ui.spec.ts` | 2 | Playwright |
| Workflow State (Epic 41) | `tests/unit/test_workflow_state.py` | 5 | ✅ |
| Workflow Repository (Epic 41) | `tests/unit/test_workflow_repository.py` | 19 | ✅ |
| Workflow Runner (Epic 41) | `tests/unit/test_workflow_runner.py` | 6 | ✅ |
| Workflow API Integration (Epic 41) | `tests/integration/test_workflow_api.py` | 12 | integration |
| **Hybrid RAG (Epic 42)** | `tests/unit/test_hybrid_rag.py` | **31** | ✅ |
| **Opportunity Score (Epic 43)** | `tests/unit/test_opportunity_score.py` | **43** | ✅ |
| **Product Golden Path Acceptance (Epic 38)** | `tests/acceptance/test_product_golden_path.py` | **11 classes/suites** | acceptance |
| **No Demo Dependency Guard (Epic 38)** | `tests/acceptance/test_no_demo_dependency.py` | **3 tests** | acceptance |
| **No Demo Dependency (Epic 45)** | `tests/acceptance/test_no_demo_dependency.py` | **3** | acceptance |
| **Check No Demo Dependency (Epic 45)** | `scripts/check_no_demo_dependency.py` | **manual** | script |
| **Total** | **77 Python test files + 2 Playwright specs + 1 script** | **~818 Python + 8 E2E** | **~752 pass + acceptance + UI smoke** |

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
| `database/` (2 files) | ✅ REAL | ✅ | 8 unit + 2 API integration |
| `repositories/claim.py` (Epic 32) | ✅ REAL | ✅ | 12 unit |
| `services/product/claim_ledger.py` (Epic 32) | ✅ REAL | ✅ | 9 unit |
| `api/product_routes.py` claims (Epic 32) | ✅ REAL | ✅ | 9 integration |
| `services/product/claim_constants.py` (Epic 32) | ✅ REAL | ✅ | (via test_claim_repository) |
| `evaluation/` (9 files) | ✅ REAL | ✅ | 20 + 14 (Epic 13) + 11 (Epic 14) + 9 (Epic 23 answer quality) + 4 (Epic 23.2 optional judge) |
| `playbook/` (3 files) | ✅ REAL | ✅ | 13 (loader) + 9 (matcher) |
| `repositories/activation.py` (Epic 33) | ✅ REAL | ✅ | (via matcher tests) |
| `services/product/activation_service.py` (Epic 33) | ✅ REAL | ✅ | 9 (matcher) |
| `api/product_routes.py` activation (Epic 33) | ✅ REAL | ✅ | 8 integration |
| `repositories/dossier.py` (Epic 34) | ✅ REAL | ✅ | 7 |
| `services/product/dossier_service.py` (Epic 34) | ✅ REAL | ✅ | 10 |
| `api/product_routes.py` dossier (Epic 34) | ✅ REAL | ✅ | 8 integration |
| `interface/` (1 file) | ❌ STUB | ❌ | 0 |
| `scripts/check_scope.py` | ✅ REAL | ✅ | 7 |
| `scripts/check_docs_closure.py` | ✅ REAL | ✅ | 7 |
| `scripts/build_regression_dashboard.py` | ✅ REAL | ✅ | 14 |
| `validation/output_validation.py` | ✅ REAL | ✅ | 12 |
| `evaluation/structured_outputs.py` (Epic 36) | ✅ REAL | ✅ | 30 |
| `services/product/capability_registry.py` (Epic 36.1) | ✅ REAL | ✅ | 6 |
| `services/product/config_registry.py` (Epic 36.1) | ✅ REAL | ✅ | 9 |
| `services/product/readiness_service.py` (Epic 36.1) | ✅ REAL | ✅ | 10 |
| `orchestration/` (Epic 41) | ✅ REAL | ✅ | 30 unit + 12 integration |
| `rag/query_planner.py` (Epic 42) | ✅ REAL | ✅ | 5 (via test_hybrid_rag) |
| `rag/sparse_retrieval.py` (Epic 42) | ✅ REAL | ✅ | 4 (via test_hybrid_rag) |
| `rag/fusion.py` (Epic 42) | ✅ REAL | ✅ | 7 (via test_hybrid_rag) |
| `rag/reranker.py` (Epic 42) | ✅ REAL | ✅ | 4 (via test_hybrid_rag) |
| `rag/citation.py` (Epic 42) | ✅ REAL | ✅ | 4 (via test_hybrid_rag) |
| `rag/evidence_refs.py` (Epic 42) | ✅ REAL | ✅ | 3 (via test_hybrid_rag) |
| `quality/evaluators/rag_quality.py` (Epic 42) | ✅ REAL | ✅ | (via test_hybrid_rag — evaluate_rag_retrieval) |

## Lacunas de cobertura

- **Integração:** `tests/integration/` tem 9 testes Qdrant (skippable via QDRANT_TEST_URL)
- **Config:** `src/config/settings.py` sem testes
- **Novos scripts:** `scripts/check_scope.py` e `scripts/check_docs_closure.py` testados (14 testes)
- **Activation Playbook:** Epics 33 coberto por 22 testes unitários (loader + matcher) e 8 testes de integração (API). Sem teste de loader para path inexistente (Path(...).resolve() já cobre).
- **Workflow Orchestration (Epic 41):** 30 testes unitários (state, repository, runner) + 12 testes de integração (API). Runner depende de session commit — tests sem commit falham. LangGraph detection testada via `_has_langgraph()`.

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
| Demo Acceptance | 5 integration tests (health, RAG status without Qdrant, sample brief output shape, answer quality evaluate, path traversal protection) + 2 Playwright smoke tests (UI happy path and API offline error) | ✅ |
| Workflow State (Epic 41) | 5 tests (constants, defaults, full state, serialization) | ✅ |
| Workflow Repository (Epic 41) | 19 tests (CRUD, status transitions, node tracing, retry) | ✅ |
| Workflow Runner (Epic 41) | 6 tests (node registration, retry policy, langgraph detection, full execution) | ✅ |
| Workflow API Integration (Epic 41) | 12 tests (POST/GET product-runs, nodes, analysis-run link, langgraph status) | ✅ |
| Hybrid RAG Query Planner (Epic 42) | 5 tests (empty, gaps, technology, product_summary, claims+gaps) | ✅ |
| Hybrid RAG Sparse Retrieval (Epic 42) | 4 tests (empty index, build+retrieve, lifecycle filter, score bounds) | ✅ |
| Hybrid RAG Fusion (Epic 42) | 7 tests (RRF empty/only/dense/sparse/dedup/weighted/top-k, weighted fusion, weighted dedup) | ✅ |
| Hybrid RAG Reranker (Epic 42) | 4 tests (NoOp passthrough, NoOp top_k, CrossEncoder default, build factory) | ✅ |
| Hybrid RAG Citation (Epic 42) | 4 tests (empty, single chunk, evidence refs format, source coverage, factory) | ✅ |
| Hybrid RAG Evidence Refs (Epic 42) | 3 tests (from chunks, from result, dossier section) | ✅ |
| Hybrid RAG RetrievalMode (Epic 42) | 1 test (enum values) | ✅ |
| Opportunity Score Tiers (Epic 43) | 6 tests (critical, high, medium, low, not_recommended, contraindication override) | ✅ |
| Opportunity Score Penalties (Epic 43) | 13 tests (claims, evidence coverage, degraded, contraindication, non_ai, low confidence, incomplete data) | ✅ |
| Opportunity Score Components (Epic 43) | 5 tests (gap_resolution, nvidia_mapping, activation_readiness, dossier_completeness, claim_support) | ✅ |
| Opportunity Score Service (Epic 43) | 19 tests (compute, get_latest, recompute, penalties, ranked, bounds, components, evidence refs, error, scope) | ✅ |

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

## Pytest Markers (Epic 39)

| Marker | Descrição | Onde roda |
|--------|-----------|-----------|
| `unit` | Testes isolados (default, sem marker) | `make validate-fast`, `make test`, `make test-unit` |
| `integration` | Testes de integração (Qdrant, PostgreSQL, API) | `make test-integration`, CI manual |
| `acceptance` | Product Golden Path | `make acceptance`, `make prepare-release` |
| `e2e` | Playwright E2E | `make ui-e2e-product`, `make ui-e2e` |
| `slow` | Testes lentos (>5s) | `make test-slow` |
| `optional` | Dependências opcionais (rag, llm-judge) | `make test-optional` |
| `external_service` | Serviços externos (Qdrant real, PostgreSQL) | `make test-external` |

`make validate-fast` roda: `pytest -m "not (integration or acceptance or e2e or slow or optional or external_service)"`

## Makefile Validate Targets (Epic 39)

| Target | Components | Use |
|--------|-----------|-----|
| `validate-fast` | lint + format-check + typecheck + test-unit | Iteração rápida (<60s) |
| `validate-backend` | validate-fast | Backend-only |
| `validate-frontend` | ui-lint + ui-build | Frontend checks |
| `validate-docs` | check_scope + check_docs_closure | Documentation integrity |
| `validate-full` | validate-fast + validate-docs + validate-frontend | Pre-commit validation |
| `prepare-release` | validate-full + acceptance + ui-build | Pre-release gate |

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

## Demo Acceptance (Epic 27)

### Execucao

```bash
make api-test
make ui-build
make ui-e2e
make demo-acceptance
```

### Testes

- 5 integration tests em `tests/integration/test_demo_acceptance.py` cobrindo health, RAG status sem Qdrant, sample brief output shape, answer quality evaluate e path traversal.
- 2 Playwright smoke tests em `tests/e2e/test_demo_ui.spec.ts` cobrindo UI happy path e erro legivel de API offline.

### Invariantes

- Smoke offline nao exige Qdrant.
- Qdrant offline deve aparecer como warning/status, nao crash.
- `POST /brief` deve preservar `brief_json`, `brief_markdown`, scores, `recommended_motion`, gaps, evidence, warnings e `run_report`.
- E2E valida wiring da demo; nao altera scoring, diagnosis, recommendation, RAG retrieval, Qdrant ingestion ou Action Brief logic.

## Documentation Mining Validation (Epic 28)

### Execucao

Epic 28 e documental. A validacao principal e manual/estrutural sobre
`docs/54_final_product_backlog.md`, com `python scripts/check_scope.py` e
`make validate` executados quando aplicavel.

### Invariantes

- Nenhuma mudanca funcional em `src/`, `frontend/`, scripts de runtime,
  pipeline, RAG, scoring, recommendation, Qdrant ingestion ou workflows.
- O backlog final deve conter todas as secoes obrigatorias, tabela acionavel,
  politica documental, tabela de poda documental, contradicoes e proximo epic
  tecnico recomendado.
- Categorias permitidas: IMPLEMENTED_KEEP, IMPLEMENTED_NEEDS_HARDENING,
  PRODUCT_BACKLOG, REPLACE, DELETE, ARCHIVE, CONTRACT_OR_TEST.
- Decisoes permitidas: KEEP, HARDEN, IMPLEMENT, REPLACE, DELETE, ARCHIVE,
  CONTRACT_OR_TEST.
- Prioridades permitidas: P0, P1, P2, P3.
- Todo item consolidado deve ter origem rastreavel.

## Startup Discovery Engine (Epic 40)

### Execução

```bash
pytest tests/unit/test_discovery_signals.py -v
pytest tests/unit/test_discovery_dedup.py -v
pytest tests/unit/test_discovery_repository.py -v
pytest tests/integration/test_discovery_api.py -v
```

### Testes

- 11 unit tests em `tests/unit/test_discovery_signals.py`: LLM, IA, GPU, CUDA, TensorRT, NLP, nvidia_tech, evidence_excerpts, confidence (high/medium/low/bounds, manual_seed, signal-only).
- 15 unit tests em `tests/unit/test_discovery_dedup.py`: normalize_name (lowercase, whitespace, casefold), extract_domain (URL variants, empty, no_scheme), is_duplicate_by_name (match, case_insensitive, no_match, empty), is_duplicate_by_domain (match, no_match, empty).
- 15 unit tests em `tests/unit/test_discovery_repository.py`: DiscoveryRun CRUD (create, complete, fail, degrade, filter, not_found) + Candidate CRUD (create, bulk, filter, mark_duplicate, promote, find_duplicate, update_status, update_fields).
- 14 integration tests em `tests/integration/test_discovery_api.py`: list_sources, manual_seed (happy path, dedup repeat, empty name skipped), runs (list, get, 404), candidates (list, filter, detail, 404), promote (creates startup, twice returns already, nonexistent 404), dedup (no duplicate).

### Invariantes

- Nenhuma alteração em scoring, RAG, Qdrant, recommendation central, LangGraph, pipeline.
- Discovery alimenta fluxo existente: Startup -> AnalysisRun -> Claims -> Playbook -> Dossier -> Quality -> Opportunities.
- Duplicatas marcadas como `duplicate`, nunca deletadas.
- Erros de fonte geram DiscoveryRun `degraded` ou `failed`, nunca crash.
- Discovery não depende de APIs pagas, LLM, ou dados de demo.
- URL list discovery respeita `robots.txt` e políticas de scraping.

## Epic 45 — Final Delivery Package & Acceptance Evidence

**Tipo:** Documentação + scripts de validação

| Artefato | Status |
|---|---|
| `docs/72_final_acceptance_evidence.md` | Template criado |
| `docs/73_final_architecture_summary.md` | Criado |
| `docs/74_final_evaluation_report.md` | Criado |
| `docs/screenshots/INSTRUCTIONS.md` | Criado |
| `sample_inputs/README.md` | Criado |
| `scripts/check_no_demo_dependency.py` | Criado |
| `README.md` — Demo Script | Atualizado |
| `README.md` — Validation Matrix | Atualizado |
| `README.md` — Playwright Policy | Atualizado |
| `README.md` — Sample Input Policy | Atualizado |
| `README.md` — Release Checklist | Atualizado |
| `README.md` — Known Limitations | Consolidado |

### Validation Matrix

| Comando | Categoria | Alvo | Bloqueia entrega? |
|---|---|---|---|
| `make validate-fast` | Build | lint + format + typecheck + unit tests | Sim |
| `make validate-backend` | Build | validate-fast | Sim |
| `make validate-frontend` | Build | tsc --noEmit + npm run build | Sim |
| `make acceptance` | Build | Product Golden Path | Sim |
| `make validate-docs` | Build | check_scope + check_docs_closure | Overridable |
| `make validate-full` | Build | validate-fast + docs + frontend | Sim |
| `make prepare-release` | Build | validate-full + acceptance + ui-build | Sim |
| `python scripts/check_no_demo_dependency.py` | Evidence | No demo dependency | Sim |
| `make ui-e2e-product` | Evidence | Playwright E2E smoke | No (extra) |

### Invariants

- Nenhuma feature nova adicionada
- Nenhuma mudança em scoring, RAG, Discovery, LangGraph, UI, Quality
- README não promete endpoint inexistente
- Known limitations honestas e completas
- Sample inputs não são fallback automático
- Playwright não bloqueia validate-fast
- Nenhuma dependência de `data/demo_runs`

## Product Backend Foundation (Epic 29)

### Tests

- 2 database tests: SQLite directory/schema initialization and URL sanitization.
- 3 repository tests: startup CRUD/uniqueness, run/brief/readiness persistence,
  and Action Brief versioning.
- 3 product service tests: real pipeline persistence, failed lifecycle without
  fallback, and no `data/demo_runs` dependency.
- 2 API integration tests: product happy path, health endpoints, duplicate
  startup, and missing-resource behavior.

## Epic 44 — Final Product UI & Demo Flow Hardening

**Tipo:** Frontend-only (sem novos testes Python)

| View | Status | Testado por |
|---|---|---|
| Setup | Enhanced | Playwright E2E |
| Capabilities | Unchanged | Playwright E2E |
| Discovery | New | Manual (backend tests cover API) |
| Startups | Unchanged | Playwright E2E |
| Startup Detail | Unchanged | Playwright E2E |
| Analysis Run | Unchanged | Playwright E2E |
| Dossier | Enhanced | Playwright E2E |
| Opportunities | Enhanced | Playwright E2E |
| Workflow | New | Manual (backend tests cover API) |
| Export Delivery | New | Manual |
| Quality | New | Manual (backend tests cover API) |

**Validação:** `npm run build` — `tsc -b` + `vite build` passam sem erros.
Sem alterações em backend, scoring, RAG, Qdrant ou LangGraph.

### Invariants

- Product state is persisted in the SQLAlchemy transactional database.
- Qdrant remains a vector/RAG dependency and does not store product entities.
- Pipeline exceptions create a persisted `failed` AnalysisRun.
- Optional dependency or evidence problems are represented as explicit
  readiness checks and a `degraded` run.
- Product modules do not read `data/demo_runs`.
