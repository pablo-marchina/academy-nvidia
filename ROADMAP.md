# ROADMAP -- Status Real (Junho 2026)

## Concluídos

### Epic 0 -- Case Consolidation (concluído)
- [x] docs/00_case_plan.md
- [x] docs/08_demo_script.md
- [x] docs/09_user_workflow.md
- [x] ROADMAP.md
- [x] DECISIONS.md
- [x] README.md

### Epic 1 -- Foundation (Scraping + Extraction)
- [x] Fetch public page (src/scraping/fetcher.py)
- [x] Parse HTML to clean text (src/scraping/parser.py)
- [x] Source policy (src/scraping/source_policy.py)
- [x] Structured extraction (src/extraction/extractor.py)
- [x] Pydantic schemas (src/extraction/schemas.py)
- [x] 14 unit tests

### Epic 2 -- AI-native Classification
- [x] 5-level heuristic classifier (src/classification/ai_native_classifier.py)
- [x] Fact/Inference/Hypothesis separation
- [x] 10 unit tests covering all levels

### Epic 3 -- Evidence Validation
- [x] Deterministic evidence validator (src/validation/evidence_validator.py)
- [x] Confidence recalibration per source type
- [x] 14 unit tests

### Epic 4 -- Dual Scoring Engine
- [x] AI-Native Defensibility Score (src/scoring/defensibility_score.py, 6 dims)
- [x] NVIDIA Inception Fit Score (src/scoring/inception_fit_score.py, 4 dims)
- [x] Composite score with configurable weights
- [x] 6 + 6 + 9 = 21 unit tests with golden examples

### Epic 5 -- Production AI Readiness
- [x] 4-dimension readiness scoring (src/scoring/production_readiness.py)
- [x] Evidence-aware confidence penalty
- [x] 6 unit tests

### Epic 6 -- Composite Ranking + Motion Hints
- [x] Confidence-aware weighted ranking (src/scoring/composite_ranking.py)
- [x] Motion hints (immediate_outreach -> not_recommended)
- [x] 9 unit tests

### Epic 7 -- Gap Diagnosis + NVIDIA Mapping
- [x] 15 gap detectors (src/diagnosis/gap_diagnosis.py, 902 lines)
- [x] NVIDIA technology mapping matrix (src/diagnosis/nvidia_mapping.py, 228 lines)
- [x] Schemas tipados (EvidenceTag, GapWithEvidence, NvidiaTechnologyCandidate, GapDiagnosisResult)
- [x] Gaps inferidos marcados como INFERRED
- [x] Output inclui evidence_used e missing_evidence
- [x] Cobertura: 10/15 gaps testados individualmente
- [x] Coverage mapping: todos os 15 gaps tem >=1 tecnologia NVIDIA
- [x] 14 + 6 + 1 = 21 unit tests

### Epic 7.1 -- Architecture Utilization Audit + Pipeline Integration
- [x] Pipeline orchestrator (src/pipeline/run_pipeline.py, 7 steps)
- [x] Pipeline calls all 3 scores + composite ranking
- [x] 5 pipeline unit tests
- [x] AGENTS.md updated with closure checklist
- [x] README.md with Current Capabilities + Known Limitations
- [x] DECISIONS.md updated
- [x] EVALS.md with real coverage
- [x] docs/25_end_of_epic_closure.md
- [x] docs/26_architecture_utilization_audit.md
- [x] Obsidian vault backfill

### Epic 8 -- Recommendation Engine (concluido)
- [x] Schemas tipados: SuggestedTechnicalExperiment, RecommendedNextAction, PerGapRecommendation, RecommendationResult
- [x] Engine deterministico sem RAG, LangGraph ou LLM
- [x] Action matrix com 4 acoes (approach_now -> not_recommended)
- [x] Prioridade e complexidade por gap + tecnologia
- [x] SuggestedTechnicalExperiment gerado apenas para APPROACH_NOW (14 templates)
- [x] 22 unit tests (acao, prioridade, experimentos, per-gap, integracao)
- [x] NvidiaRecommendation antigo removido de src/extraction/schemas.py
- [x] docs/06_recommendation_logic.md reescrito

### Epic 7.2 -- Development Workspace Quality System (concluido)
- [x] docs/plans/PLAN_TEMPLATE.md
- [x] docs/adr/ADR_TEMPLATE.md
- [x] docs/contracts/ -- 6 contratos de desenvolvimento
- [x] docs/27_developer_rag_design.md
- [x] docs/28_development_workspace_quality.md
- [x] 7 prompts versionados
- [x] AGENTS.md com 10 regras de workspace
- [x] DECISIONS.md com 5 decisoes de workspace
- [x] EVALS.md com criterios de qualidade do desenvolvimento
- [x] Obsidian -- 5 notas em 02 Project Control/

### Epic 9.1 -- Integrate Diagnosis and Recommendation into Full Pipeline (concluido)
- [x] Pipeline estendido de 7 para 11 steps
- [x] run_full_pipeline() agora chama gap diagnosis, NVIDIA mapping e recommendation engine
- [x] PipelineResult inclui gap_diagnosis e recommendation
- [x] missing_evidence propagado de todos os modulos ate o output final
- [x] Nenhuma tecnologia NVIDIA recomendada sem gap diagnosticado
- [x] Evidencia fraca reduz forca da recomendacao (action != APPROACH_NOW)
- [x] 10 pipeline tests (5 existentes atualizados + 5 novos)
- [x] Total: 148 testes (138 + 10)
- [x] Contrato pipeline_output atualizado para v2.0
- [x] DECISIONS.md: Decision 016 registrada

---

## Em andamento / Proximos

### Epic 10 -- Startup Action Brief (concluido)
- [x] src/briefing/ module with schemas, builder, and markdown renderer
- [x] StartupActionBrief Pydantic schema with 13 sections
- [x] build_action_brief(PipelineResult) -> StartupActionBrief
- [x] render_action_brief_markdown(brief) -> str
- [x] Verdict logic (high_priority -> not_recommended)
- [x] Evidence-aware: uncertainties, missing_evidence preserved
- [x] No NVIDIA tech without diagnosed gap
- [x] 10 unit tests (high-fit, weak, no-gap, missing, markdown, JSON, schema)
- [x] docs/16_briefing_template.md reescrito
- [x] docs/contracts/briefing_contract.md criado
- [x] Total: 153 tests, 17 arquivos

### Epic 11 -- Product RAG / Playbook Retrieval (concluido)
- [x] data/nvidia_corpus/ com 10 documentos Markdown mapeados para 15 gaps e 14 experimentos
- [x] src/rag/schemas.py -- RagSource, RagDocument, RagChunk, RetrievalQuery, RetrievedContext, PlaybookRetrievalResult
- [x] src/rag/ingestion.py -- load_sources(), load_markdown_document(), chunk_document(), load_and_chunk_corpus()
- [x] src/rag/retrieval.py -- ChunkIndex in-memory, retrieve(), retrieve_by_gap_type(), retrieve_by_technology()
- [x] src/rag/playbook_retriever.py -- PlaybookRetriever.retrieve_for_gaps(), retrieve_for_brief()
- [x] Chunking deterministico por headings ##, metadados preservados
- [x] Retrieval lexical sem embeddings, sem Qdrant, sem novas dependencias
- [x] Provenance obrigatoria: cada chunk carrega source_id, url, product
- [x] RAG enriquece mas nunca decide (brief funciona sem RAG)
- [x] docs/35_product_rag_design.md criado
- [x] docs/contracts/rag_contract.md criado
- [x] Total: 168 tests, 20 arquivos

### Epic 12 -- RAG Evaluation & Retrieval Quality Gates (concluido)
- [x] src/evaluation/rag_eval_schemas.py -- RagEvalCase, RagRetrievalMetrics, RagEvalResult, RagQualityGateResult
- [x] src/evaluation/rag_eval.py -- run_rag_eval(), run_quality_gates(), format_eval_summary()
- [x] examples/rag_eval/golden_queries.json -- 16 golden queries (10 gaps + 6 negativos)
- [x] examples/rag_eval/expected_contexts.json -- chunk_ids esperados por query
- [x] 7 metricas: hit_at_k, source/product coverage, irrelevant/missing, top_1_match, precision
- [x] 6 quality gates: hit_at_3, top_1, zero_missing, irrelevant_limit, provenance, missing_explicit
- [x] 20 testes (golden, metricas, gates, provenance, brief compatibilidade)
- [x] docs/36_rag_evaluation.md criado
- [x] Total: 188 tests, 21 arquivos
- [x] Nenhuma alteracao em RAG, Briefing, Pipeline, Recommendation, Diagnosis
- [x] Nenhuma dependencia nova, embedding, Qdrant, LangGraph, LLM judge

### Epic 13 -- Embeddings + Vector Store Retrieval (concluido)
- [x] src/rag/embeddings.py -- EmbeddingProvider (abstract), MockEmbeddingProvider, SentenceTransformerProvider
- [x] src/rag/vector_store.py -- InMemoryVectorStore with cosine similarity + metadata filters
- [x] src/rag/semantic_retrieval.py -- semantic_retrieve() with metadata filters
- [x] src/rag/hybrid_retrieval.py -- hybrid_retrieve() with RRF fusion and lexical fallback
- [x] src/evaluation/rag_eval_schemas.py -- + RetrievalMode, ModeEvalResult, RagEvalComparison
- [x] src/evaluation/rag_eval.py -- + run_mode_eval(), run_comparison_eval(), format_comparison_summary()
- [x] 52 new tests (embeddings 11, semantic 15, hybrid 12, eval 14)
- [x] docs/37_embeddings_vector_store.md created
- [x] docs/contracts/rag_contract.md updated
- [x] Total: 236 tests, 25 arquivos
- [x] In-memory vector store (no external deps for tests)
- [x] Mock embedding provider (deterministic, no model download)
- [x] RAG Evaluation compares lexical/semantic/hybrid with regression detection
- [x] Action Brief unchanged -- works without vector store

### Epic 14 -- Reranking e Context Packing Deterministicos (concluido)
- [x] src/rag/reranking.py -- deterministic composite score (gap/tech boost + provenance/duplicate/irrelevant penalties), clamped to [0,1]
- [x] src/rag/context_packing.py -- dedup, classify by gap/tech, apply per-gap/per-tech/global limits, compute metrics
- [x] src/rag/schemas.py -- RerankingConfig, PackedContext, DroppedContext, PackingConfig, PackingResult, SupportingNvidiaContext
- [x] src/evaluation/rag_eval_schemas.py -- 2 new modes (HYBRID_RERANKED, HYBRID_RERANKED_PACKED), 8 new metric fields
- [x] src/evaluation/rag_eval.py -- 5-mode support, regression detection for all later modes
- [x] src/briefing/schemas.py -- 3 optional packed-context fields
- [x] src/briefing/action_brief.py -- accepts optional PackingResult, injects Supporting NVIDIA Context section
- [x] src/briefing/markdown_renderer.py -- renders Supporting NVIDIA Context section with score and provenance
- [x] 38 new tests (reranking 9, packing 13, eval 11, brief 5)
- [x] docs/38_rag_reranking_context_packing.md created
- [x] docs/contracts/rag_contract.md updated
- [x] Total: 276 tests, 29 arquivos

### Epic 14.1 -- Integrate RAG Reranking + Context Packing into Main Pipeline (concluido)
- [x] src/rag/rag_pipeline.py -- run_rag_pipeline() orchestration (hybrid retrieval -> rerank -> pack)
- [x] src/rag/schemas.py -- RagPipelineOutput schema
- [x] src/pipeline/run_pipeline.py -- Step 11 (RAG), rag_output field, optional RAG parameters
- [x] src/briefing/action_brief.py -- auto-extract packing_result from PipelineResult.rag_output
- [x] 10 new tests (pipeline with RAG, without RAG, empty index, brief section, dropped not in brief, motion unchanged, provenance, quality summary, backward compat, lexical mode)
- [x] docs/contracts/pipeline_output_contract.md updated (v3.0)
- [x] docs/contracts/rag_contract.md updated
- [x] docs/contracts/briefing_contract.md updated (v2.0)
- [x] Total: 286 tests, 30 arquivos
- [x] RAG integrated as optional Step 11 -- no impact on scoring, diagnosis, or recommendation

### Epic 15 -- Persistent Vector Store with Qdrant (concluido)
- [x] src/rag/vector_store.py -- VectorStore ABC extraida, InMemoryVectorStore herda dela
- [x] src/rag/qdrant_store.py -- QdrantStore(VectorStore) com lazy connection, payload rico, filtros server-side
- [x] src/rag/semantic_retrieval.py, hybrid_retrieval.py, rag_pipeline.py -- tipagem alterada para VectorStore (polimorfico)
- [x] src/evaluation/rag_eval.py -- tipagem alterada para VectorStore
- [x] tests/unit/test_qdrant_store.py -- 20 testes (sem Qdrant)
- [x] tests/integration/test_qdrant_rag_pipeline.py -- 9 testes (skippable)
- [x] .env.example -- +RAG_VECTOR_BACKEND, QDRANT_COLLECTION, QDRANT_VECTOR_SIZE
- [x] docker-compose.yml -- healthcheck no Qdrant
- [x] docs/39_qdrant_persistent_vector_store.md
- [x] docs/contracts/rag_contract.md -- + QdrantStore API + payload schema + invariants
- [x] Payload schema: chunk_id, source_id, source_title, source_url, product, gap_types, version, content_hash, collected_at, document_type, provenance
- [x] Filtros obrigatorios: product, gap_type, source_id, version, document_type
- [x] Total: 315 testes (306 unit + 9 integration skippable), 31 test files
- [x] Qdrant opcional -- RAG continua funcionando sem Qdrant

### Epic 16 -- CI/CD, Validation Automation & Quality Gates (concluido)
- [x] .github/workflows/ci.yml -- GitHub Actions CI (ruff, black, mypy, pytest)
- [x] .pre-commit-config.yaml -- pre-commit hooks (trailing-whitespace, end-of-file-fixer, check-yaml/toml/json, check-added-large-files, ruff, black)
- [x] Makefile -- targets: test, lint, format-check, typecheck, validate, rag-eval, ci
- [x] scripts/validate.sh -- local validation runner
- [x] scripts/check_scope.py -- detects sensitive area changes, requires contract/doc/EVALS updates
- [x] scripts/check_docs_closure.py -- verifies plan, ROADMAP, EVALS, Obsidian, Known Limitations before epic close
- [x] tests/unit/test_check_scope.py -- 7 tests
- [x] tests/unit/test_check_docs_closure.py -- 6 tests
- [x] docs/40_ci_cd_quality_gates.md -- design doc
- [x] AGENTS.md, README.md, EVALS.md, ROADMAP.md, DECISIONS.md updated
- [x] Obsidian vault backfill
- [x] Total: 329 tests (315 existing + 14 new), 34 test files
- [x] No changes to src/ or product tests

### Epic 17 -- Golden Eval Harness (End-to-End Pipeline Regression Detection) (concluido)
- [x] 7 JSON golden cases in examples/golden/
- [x] expected_outputs.json -- cross-check matching every case
- [x] examples/golden/README.md -- golden case documentation
- [x] tests/evals/helpers.py -- GoldenCase, load_golden_case, run_pipeline_on_case, run_pipeline_with_rag, 11 assert helpers
- [x] tests/evals/test_pipeline_golden.py -- 38 tests across 6 test classes + 3 cross-cutting checks
- [x] All golden evals run offline (MockEmbeddingProvider + InMemoryVectorStore -- no Qdrant, no sentence-transformers)
- [x] RAG golden cases verify motion stability, context-in-brief, context-not-in-evidence
- [x] docs/41_end_to_end_eval_harness.md
- [x] DECISIONS.md -- Decision 025
- [x] EVALS.md -- golden eval section
- [x] README.md -- updated test count, removed no eval harness limitation
- [x] Obsidian vault backfill
- [x] Total: 358 tests (329 pre-existing + 38 golden evals), 36 test files
- [x] No changes to src/ -- pure test infrastructure

### Epic 18 -- Automated Qdrant Corpus Ingestion (concluido)
- [x] scripts/ingest_nvidia_corpus.py -- script de ingestao automatizada
- [x] CLI com --dry-run, --recreate-collection, --skip-existing, --source-id, --product, --backend, --mock-embeddings, --report-path
- [x] Validacao de documentos (metadata obrigatoria, arquivo vazio)
- [x] content_hash (documento) e chunk_hash (chunk) via MD5 deterministico
- [x] Embeddings via SentenceTransformerProvider ou MockEmbeddingProvider
- [x] Extra opcional rag declarado para instalar sentence-transformers sem tornar RAG dependencia obrigatoria do core
- [x] Upsert em Qdrant com payload completo (provenance, hashes, versao, filtros)
- [x] Payload indexes automaticos (product, gap_types, source_id, version, document_type, content_hash)
- [x] Relatorio de ingestao com contadores
- [x] Idempotencia via chunk_hash + --skip-existing
- [x] Nenhuma chamada externa, nenhum scraping, nenhum crawler
- [x] src/rag/schemas.py -- +version, document_type, content_hash em RagChunk/RagSource
- [x] src/rag/vector_store.py -- +version, document_type, content_hash, chunk_hash, ingestion_run_id em VectorEntry
- [x] src/rag/qdrant_store.py -- payload indexes + novos campos no payload
- [x] data/nvidia_corpus/sources.yaml -- +version, document_type por source
- [x] tests/unit/test_ingest_nvidia_corpus.py -- 17 testes
- [x] tests/unit/test_rag_embeddings.py -- +1 teste para erro claro quando sentence-transformers nao esta instalado
- [x] tests/integration/test_qdrant_corpus_ingestion.py -- 3 testes (skippable)
- [x] docs/42_automated_qdrant_corpus_ingestion.md
- [x] Total: 448 tests (436 passing + 12 skippable), 39 test files
- [x] README / EVALS / ROADMAP / docs / Obsidian atualizados

### Epic 19 -- Automated NVIDIA Corpus Source Sync (concluido)
- [x] scripts/sync_nvidia_sources.py -- script de sync automatizado com allowlist
- [x] data/nvidia_corpus/source_allowlist.yaml -- allowlist versionada com 10 fontes + 1 bloqueada
- [x] data/nvidia_corpus/staging/, archive/, sync_reports/ -- diretorios de suporte
- [x] CLI com flags dry-run, source-id, product, promote, staging-only, report-path, fail-on-validation-error, max-documents, rate-limit-seconds
- [x] Fluxo completo: carregar allowlist, validar, baixar com rate limit e robots.txt, salvar em staging, comparar hash, promover
- [x] Seguranca: timeout, max-size, user-agent claro, sem cookies, sem login, sem follow de links
- [x] tests/unit/test_sync_nvidia_sources.py -- 49 testes mockados (zero chamadas externas)
- [x] docs/43_automated_nvidia_source_sync.md
- [x] Total: 424 tests (375 pre-existing + 49 novos), 38 test files
- [x] README / EVALS / ROADMAP / docs / Obsidian atualizados
- [x] Nenhuma alteracao em src/, nenhuma ingestao Qdrant, nenhuma dependencia nova

### Epic 20 -- Corpus Freshness, Versioning & Deprecation Policy (concluido)
- [x] docs/44_corpus_freshness_versioning_policy.md -- politica de versionamento, freshness, expiracao e deprecacao
- [x] data/nvidia_corpus/sources.yaml -- lifecycle metadata por source e versao ativa
- [x] data/nvidia_corpus/source_allowlist.yaml -- politica esperada de freshness por fonte permitida
- [x] scripts/audit_nvidia_corpus_freshness.py -- auditoria offline com JSON/Markdown, filtros e fail-on-stale/expired
- [x] scripts/ingest_nvidia_corpus.py -- preserva metadata de freshness/versioning no VectorEntry/payload
- [x] src/rag/ -- retrieval padrao filtra inactive/deprecated/superseded/expired
- [x] tests/unit/test_corpus_freshness_audit.py -- stale, expired, deprecated, superseded, missing metadata, duplicate active versions, fail flags, version promotion e retrieval filter
- [x] docs/contracts/rag_contract.md, README, EVALS, DECISIONS e Obsidian atualizados
- [x] Total validado: 447 tests (435 passed + 12 skipped)
- [x] Nenhum crawler amplo, nenhuma chamada externa, nenhuma dependencia nova

### Epic 21 - Scheduled Corpus Maintenance Workflow (concluido)
- [x] .github/workflows/corpus-maintenance.yml - workflow manual com defaults seguros e schedule semanal seguro
- [x] scripts/run_corpus_maintenance.py - orquestrador local para sync dry-run, freshness audit, ingest dry-run, ingestao real opcional, RAG evals e golden evals
- [x] Makefile - alvos corpus-maintenance-dry-run, corpus-maintenance-evals, corpus-maintenance-ingest
- [x] Reports em reports/corpus-maintenance/<run-id>/ e artifact corpus-maintenance-reports
- [x] Ingestao real exige run_ingestion=true; promocao exige promote_sources=true
- [x] Schedule nao promove fontes, nao ingere real, nao faz auto-commit
- [x] docs/45, README, EVALS, DECISIONS e Obsidian atualizados
- [x] Nenhum crawler amplo, nenhuma mudanca em retrieval/embeddings/scoring/diagnosis/recommendation/briefing

### Epic 22 - RAG / Action Brief Regression Dashboard (concluido)
- [x] scripts/build_regression_dashboard.py - consolida reports de manutencao em Markdown + JSON
- [x] data/regression_reports/latest_dashboard.md e .json gerados pelo comando local
- [x] Metricas consolidadas para ingestion, freshness, RAG evals, golden evals e Action Brief checks
- [x] Status PASS, WARN, FAIL com WARN nao bloqueante e FAIL bloqueante no workflow
- [x] .github/workflows/corpus-maintenance.yml escreve dashboard no Job Summary e publica artifact
- [x] Makefile - alvo regression-dashboard
- [x] tests/unit/test_regression_dashboard.py - 7 testes unitarios
- [x] docs/46_regression_dashboard.md, README, EVALS, ROADMAP e Obsidian atualizados
- [x] Nenhuma mudanca em retrieval, Qdrant ingestion, scoring, diagnosis, recommendation ou Action Brief logic

### Epic 23 - LLM/RAG Answer Quality Evaluation (concluido)
- [x] src/evaluation/answer_quality_schemas.py - schemas para casos, metricas, gates, claims e coverage checks
- [x] src/evaluation/answer_quality_eval.py - avaliador deterministico offline para StartupActionBrief
- [x] examples/answer_quality/golden_answer_quality_cases.json - 8 golden cases versionados
- [x] tests/evals/test_answer_quality_golden.py - 9 testes offline
- [x] Metricas: required sections, missing evidence, uncertainty, motion consistency, evidence/gap/technology IDs, unsupported claims, citation coverage, absolute language e PASS/WARN/FAIL
- [x] Quality gates bloqueantes para secoes, missing_evidence, uncertainty, technology sem gap, motion alterado, unsupported claims e IDs obrigatorios
- [x] Dashboard le answer_quality_eval_junit.xml opcional e expoe answer_quality_passed, failed cases, unsupported_claim_count, required_sections_missing, citation_coverage e status
- [x] docs/47_answer_quality_evaluation.md, README, EVALS, ROADMAP e Obsidian atualizados
- [x] Nenhuma chamada externa, nenhum LLM judge, nenhuma mudanca em scoring/diagnosis/recommendation/retrieval/Qdrant/recommended_motion

### Epic 23.1 - Answer Quality JUnit Report Integration (concluido)
- [x] make answer-quality-junit gera data/regression_reports/answer_quality_eval_junit.xml
- [x] scripts/run_corpus_maintenance.py executa Answer Quality JUnit quando run_evals=true
- [x] Dashboard extrai tests, failures, errors, skipped, failed cases, failure details e PASS/WARN/FAIL do XML
- [x] GitHub Actions publica o XML como artifact e mostra status/counters no Job Summary
- [x] tests/unit/test_regression_dashboard.py cobre JUnit PASS, failure, error, skipped e ausente
- [x] Nenhuma mudanca em metricas de Answer Quality, eval cases, RAG retrieval, Action Brief, scoring, diagnosis ou recommendation

### Epic 23.2 - Optional LLM Judge Adapter for Answer Quality (concluido)
- [x] src/evaluation/llm_judge_schemas.py - schemas para input, score, result, run report e provider config
- [x] src/evaluation/llm_judge_adapter.py - provider base, NullLLMJudgeProvider offline e runner agregador
- [x] src/evaluation/llm_judge_prompts.py - prompts/rubricas para faithfulness, relevancy, groundedness, completeness, uncertainty honesty e executive usefulness
- [x] scripts/run_answer_quality_llm_judge.py - runner manual que gera JSON/Markdown em data/regression_reports/
- [x] Dashboard mostra secao Optional LLM Judge quando report existir e mantem ausencia como INFO
- [x] tests/unit/test_llm_judge_adapter.py e dashboard cobrem provider offline, prompts, script e integracao opcional
- [x] Nenhuma chamada externa, chave de API, provider real, dependencia nova ou mudanca nos gates deterministas

### Product RAG (V3 -- futuro / backlog)
- Reranking cross-encoder (alternativa ao reranking deterministico)
- Ingestao automatizada de documentacao NVIDIA via crawler respeitando robots.txt

---

### Epic 24 -- CLI Demo End-to-End (concluido)
- [x] scripts/run_startup_radar_demo.py -- CLI com argparse (6 flags: input, output-dir, use-rag, rag-backend, run-answer-quality-eval, offline, format)
- [x] examples/demo/sample_startup_input.json -- startup ficticia Nexus AI Labs (HealthTech, 5 evidencias)
- [x] examples/demo/README.md -- documentacao do sample
- [x] docs/49_cli_demo_end_to_end.md -- design doc
- [x] Makefile -- 3 targets (demo-cli, demo-cli-offline, demo-cli-rag)
- [x] CLI reusa pipeline, briefing, RAG e eval existentes -- zero logica duplicada
- [x] Modo offline: MockEmbeddingProvider + InMemoryVectorStore, sem Qdrant
- [x] Modo RAG local: InMemoryVectorStore + MockEmbeddingProvider
- [x] Modo RAG Qdrant: QdrantStore com mensagem clara de erro se indisponivel
- [x] Answer quality eval opcional com caso generico (secoes, linguagem absoluta, tech-gap)
- [x] tests/integration/test_cli_demo.py -- 6 testes de integracao
- [x] README, ROADMAP, EVALS, DECISIONS e Obsidian atualizados
- [x] Nenhuma alteracao em scoring, diagnosis, recommendation, RAG retrieval, Qdrant ingestion ou eval metrics
- [x] Total: +6 testes (484 tests, 42 test files)

### Epic 25 -- Minimal FastAPI Demo API (concluido)
- [x] src/api/main.py -- FastAPI app with CORS, lifespan, router
- [x] src/api/schemas.py -- Pydantic request/response models
- [x] src/api/routes.py -- 6 endpoint handlers (thin, delegate to service)
- [x] src/api/service.py -- business logic reusing pipeline/briefing/eval
- [x] src/api/__init__.py -- package marker
- [x] src/main.py -- re-exports app from src/api/main.py (backward compat)
- [x] tests/integration/test_api_demo.py -- 9 integration tests
- [x] docs/50_minimal_fastapi_demo_api.md -- design doc
- [x] Endpoints: GET /health, GET /version, GET /rag/status, POST /brief, POST /brief/evaluate, GET /demo/artifacts
- [x] POST /brief reuses CLI/pipeline logic (zero duplication)
- [x] GET /rag/status resilient to Qdrant being offline
- [x] GET /demo/artifacts blocks path traversal
- [x] Makefile -- targets: api, api-dev, api-test
- [x] README, ROADMAP, EVALS, DECISIONS, Obsidian atualizados
- [x] Nenhuma alteracao em scoring, diagnosis, recommendation, retrieval, Qdrant ingestion ou eval metrics

### Epic 26 -- Minimal Demo UI (concluido)
- [x] frontend/ -- Vite + React + TypeScript local demo UI
- [x] frontend/src/api/client.ts -- helpers para GET /health, GET /rag/status, POST /brief, POST /brief/evaluate e GET /demo/artifacts
- [x] Componentes: StartupInputForm, BriefViewer, ScoreCards, GapTechnologyTable, EvidencePanel, RagStatusBadge e EvalStatusPanel
- [x] Botao Load example com startup ficticia local
- [x] UI gera Startup Action Brief via API e exibe Markdown, scorecards, gaps, tecnologias NVIDIA, evidencias, warnings e incertezas
- [x] UI mostra status RAG/Qdrant e trata Qdrant offline como warning/status
- [x] UI permite avaliacao opcional do brief
- [x] Makefile -- targets: ui-install, ui-dev, ui-build, demo-full
- [x] docs/51_minimal_demo_ui.md, README, ROADMAP e Obsidian atualizados
- [x] Nenhuma alteracao em API, scoring, diagnosis, recommendation, recommended_motion, RAG retrieval, Qdrant ingestion ou answer quality metrics

### Epic 26.1 -- Workspace Clarification Gate (concluido)
- [x] AGENTS.md -- secao Workspace Clarification Gate adicionada
- [x] When to ask: 10 situacoes definidas + 9 operacoes de alto risco
- [x] When not to ask: 5 situacoes (hotfix, padrao claro, ja respondido, etc.)
- [x] Limite de 3 perguntas por rodada com defaults recomendados
- [x] Fallback seguro se usuario nao responder (menor escopo, registrar suposicao)
- [x] Formato padronizado com prefixo "Perguntas bloqueantes antes de gerar:"
- [x] 7 exemplos (UI, API, Qdrant, dependency, docs, hotfix, passo obvio)
- [x] docs/52_workspace_clarification_gate.md criado
- [x] DECISIONS.md -- WSD-006
- [x] EVALS.md -- criterio de qualidade adicionado
- [x] README.md -- Clarification Gate mencionado nas regras de workspace
- [x] Obsidian vault backfill
- [x] Nenhum src/ ou tests/ alterado

### Epic 26.2 -- Workspace Output Validation Gate (concluido)
- [x] AGENTS.md -- secao Workspace Output Validation Gate adicionada
- [x] docs/53_workspace_output_validation_gate.md criado
- [x] src/validation/output_validation.py -- validadores para Action Brief, Markdown, dashboard e API responses
- [x] src/validation/output_validation_schemas.py -- resultado padrao PASS/WARN/FAIL
- [x] tests/unit/test_output_validation.py -- testes de brief valido, secoes faltantes, motion invalido, gap invalido, evidence/missing_evidence, dashboard e Markdown TODO
- [x] examples/validation/ -- fixtures pequenas para validacao manual
- [x] Makefile -- targets validate-output, validate-brief-output, validate-dashboard-output
- [x] README, EVALS, ROADMAP e Obsidian atualizados
- [x] Nenhuma alteracao em scoring, retrieval, recommendation, Action Brief generation, API/UI behavior ou dependencias

### Epic 27 -- Demo Acceptance & E2E Smoke Tests (concluido)
- [x] tests/integration/test_demo_acceptance.py -- 5 acceptance tests para health, RAG status sem Qdrant, sample brief, evaluate e path traversal
- [x] tests/e2e/test_demo_ui.spec.ts -- smoke Playwright para UI happy path e erro legivel de API offline
- [x] frontend/playwright.config.ts -- sobe API + Vite localmente e guarda trace/screenshot/video apenas em falha
- [x] Makefile -- targets: demo-acceptance, api-test, ui-build, ui-e2e, demo-full-check
- [x] docs/52_demo_acceptance.md -- cobertura automatizada e checklist manual fallback
- [x] README, EVALS, ROADMAP e Obsidian atualizados
- [x] Smoke offline nao exige Qdrant
- [x] Nenhuma alteracao em scoring, diagnosis, recommendation, recommended_motion, RAG retrieval, Qdrant ingestion ou Action Brief logic

### Epic 28 -- Documentation Mining & Final Product Backlog Consolidation (concluido)
- [x] docs/plans/2026-06-11_epic-28_documentation-mining-final-product-backlog.md -- plano salvo
- [x] docs/54_final_product_backlog.md -- backlog final consolidado para modo produto
- [x] Itens classificados em IMPLEMENTED_KEEP, IMPLEMENTED_NEEDS_HARDENING, PRODUCT_BACKLOG, REPLACE, DELETE, ARCHIVE e CONTRACT_OR_TEST
- [x] Politica documental final e tabela de poda documental criadas
- [x] Contradicoes documentais registradas
- [x] Proximo epic tecnico recomendado: Epic 29 -- Product Backend Foundation
- [x] Nenhuma mudanca funcional em codigo, API, UI, pipeline, RAG, scoring, recommendation, Qdrant ingestion ou workflows

### Epic 29 - Product Backend Foundation (concluido)
- [x] SQLite-first product database via PRODUCT_DB_URL
- [x] Transactional models for startups, evidence, analysis runs, scores, gaps, NVIDIA mappings, Action Briefs, and readiness checks
- [x] Product repositories and service integration with the existing pipeline
- [x] Persisted lifecycle: queued, running, completed, degraded, failed
- [x] Explicit degraded states and product/dependency health endpoints
- [x] Product routes for startups, analysis runs, and Action Brief retrieval
- [x] Product flow independent from data/demo_runs
- [x] docs/55_product_backend_foundation.md and product API contract
- [x] No changes to UI, scoring, recommendation, RAG retrieval, or Qdrant ingestion

### Epic 30 -- Product Backend Completion (concluido)
- [x] Alembic migrations with SQLite + PostgreSQL support
- [x] PATCH /startups/{id} with normalized_name recalculation
- [x] ReviewDecision (approve/reject/needs_more_evidence/monitor/contact/not_recommended)
- [x] GET /opportunities with filters, sorting, and pagination
- [x] ExportRecord for JSON and Markdown exports
- [x] PostgreSQL validation via skippable integration tests
- [x] Contracts updated, tests passing, demo routes preserved

## Em andamento / Proximos

### Epic 31 -- Product Simplification & Deletion Pass (concluído)
- [x] Inventory of demo/dead artifacts, docs, data, scripts, API, frontend
- [x] DELETE_NOW: generated artifacts deleted (data/demo_runs/latest, regression_reports, ingestion_reports, corpus test files)
- [x] .gitignore updated for generated data directories
- [x] ARCHIVE_HISTORY: demo docs, historical plans, and superseded notes archived with headers
- [x] README updated: demo no longer main flow; product API is primary
- [x] ROADMAP, EVALS, Obsidian updated
- [x] Regression test added: product services do not read data/demo_runs
- [x] Decision 034 registered: demo artifacts are not product sources
- [x] Nenhuma mudanca em pipeline, scoring, RAG, recommendation, database

### Epic 32 — Evidence & Claim Ledger (concluído)
- [x] ClaimRecord model (FK Startup + AnalysisRun)
- [x] Enums: ClaimType, SupportLevel, ClaimReviewStatus
- [x] ClaimRepository (CRUD, bulk, coverage, unsupported detection)
- [x] ClaimLedgerService (deterministic claim generation from persisted records)
- [x] 3 API endpoints (list claims, evidence coverage, review claim)
- [x] claim_summary injected in AnalysisRunRead
- [x] unsupported_claim_count + evidence_coverage in OpportunityListItem
- [x] 5 readiness checks in degraded.py
- [x] Alembic migration 0002
- [x] Unit tests (claim_repository 12, claim_ledger 9)
- [x] Integration tests (claim_api 9)
- [x] Docs: plan, module doc (58), contract
- [x] Validations passed (pytest, ruff, black, mypy)
- [x] ROADMAP, EVALS, DECISIONS, Obsidian vault updated

### Epic 34 — Startup Activation Dossier (concluído)
- [x] ActivationDossierRecord model (FK AnalysisRun, versioned, JSON + Markdown columns)
- [x] Alembic migration 0004 (c3d4e5f6a7b8)
- [x] ActivationDossierRepository (CRUD, versioning, get_latest, next_version, delete)
- [x] Pydantic schemas: ActivationDossierRead, ActivationDossierGenerateResponse, ActivationDossierMarkdownRead, ActivationDossierSummaryRead
- [x] ActivationDossierService (build, get, regenerate, markdown, summary)
- [x] Deterministic JSON dossier projecting: startup, scores, gaps, mappings, activation playbooks, claims, reviews, readiness checks
- [x] Deterministic Markdown renderer (11 template sections)
- [x] 3 API endpoints (POST generate, GET dossier, GET markdown)
- [x] Dossier summary injected into AnalysisRunRead and OpportunityListItem
- [x] 5 degraded-state codes for dossier readiness
- [x] Unit tests: repository 7, service 10 (all passing)
- [x] Integration tests: API 8 (all passing)
- [x] All 589 non-integration tests passing (no regression)
- [x] Docs: plan, module doc (60), contract
- [x] product_api_contract.md updated (v2.1)
- [x] Validations: pytest, ruff, black, mypy, scope, docs-closure
- [x] ROADMAP, DECISIONS, EVALS updated

### Epic 33 — NVIDIA Activation Playbook Library (concluído)
- [x] YAML source with 10 playbooks (inference, latency, agent governance, data, CV, voice, simulation, robotics, security, private deployment)
- [x] Pydantic schemas: ActivationPlaybook, ActivationPlaybookMatch, ActivationRecommendationSchema
- [x] Playbook loader with validation (unique IDs, required fields, valid motions/complexities)
- [x] ActivationRecommendationRecord model (FK AnalysisRun, JSON columns, indexes)
- [x] Alembic migration 0003 (rev a1b2c3d4e5f6 → b2c3d4e5f6a7)
- [x] ActivationRecommendationRepository (CRUD, replace, list, get_top)
- [x] ActivationPlaybookService (deterministic matching, confidence scoring, ranking, persist)
- [x] 4 readiness checks (NO_ACTIVATION_PLAYBOOK_MATCH, PLAYBOOK_LOW_EVIDENCE_SUPPORT, etc.)
- [x] 3 API endpoints (GET playbooks, GET/POST recommendations)
- [x] Opportunities endpoint enriched (top_activation_playbook, activation_confidence, activation_next_step)
- [x] Auto-generate activation in analysis run lifecycle
- [x] Unit tests (loader 13, matcher 9)
- [x] Integration tests (activation_api 8)
- [x] Docs: plan, module doc (59), contract
- [x] Validations passed (pytest 30/30, ruff, black, mypy, scope, docs-closure)
- [x] ROADMAP, EVALS, DECISIONS, Obsidian vault updated

### Epic 36 — Structured Output Reliability Layer (concluído)
- [x] `src/evaluation/structured_outputs.py` — core module: parse_json_output, repair_json_if_safe, validate_output, run_validation_with_repair, build_structured_output_result, readiness_check_payload_from_result, quality_metrics_from_results
- [x] 5 new degraded state codes in `src/services/product/degraded.py` (STRUCTURED_OUTPUT_INVALID, STRUCTURED_OUTPUT_REPAIRED, STRUCTURED_OUTPUT_RETRY_EXHAUSTED, STRUCTURED_OUTPUT_SCHEMA_DRIFT, STRUCTURED_OUTPUT_MISSING_REQUIRED_FIELD)
- [x] 6 new quality metric constants in `src/quality/constants.py` with thresholds
- [x] `src/quality/evaluators/structured_output_reliability.py` — evaluator querying readiness checks
- [x] Integrated evaluator into `src/quality/service.py`
- [x] Applied to Activation Dossier: DossierJsonSchema Pydantic model, validation in `_validate_dossier_json()`, readiness check creation on failure
- [x] `src/evaluation/llm_judge_instructor_adapter.py` — optional Instructor trial adapter with lazy import
- [x] `pyproject.toml` — added `[llm-judge]` extra with `instructor>=1.8,<2`
- [x] `tests/unit/test_structured_outputs.py` — 30 tests (parse, repair, validate, retry, metrics, readiness payload)
- [x] `tests/integration/test_structured_outputs.py` — 4 integration tests (dossier validation, quality metrics)
- [x] `docs/62_structured_output_reliability.md` — design doc with inventory, architecture, state codes, metrics
- [x] `docs/contracts/structured_output_contract.md` — contract with schemas, functions, invariants, examples
- [x] `EVALS.md` updated with test entries and coverage
- [x] `ROADMAP.md` updated with Epic 36 entries
- [x] All validations passing (pytest, ruff, black, mypy, scope, docs-closure)

### Epic 36.1 — Product Capability & Configuration Registry (concluído)
- [x] `src/services/product/capability_registry.py` — 25+ capability definitions across all categories
- [x] `src/services/product/config_registry.py` — 17+ config items with env var resolution, secret masking, extra checking
- [x] `src/services/product/readiness_service.py` — ProductReadinessService: list_capabilities, get_capability_status, validate_configuration, get_product_readiness, get_setup_checklist, get_optional_features_status, get_missing_configuration
- [x] `src/api/product_schemas.py` — 5 new schemas: ProductCapabilityRead, ProductConfigurationItemRead, ProductSetupChecklistRead, ProductReadinessRead, OptionalFeatureStatusRead
- [x] `src/api/product_routes.py` — 4 new GET endpoints: /product/capabilities, /product/configuration, /product/setup-checklist, /product/readiness
- [x] `.env.example` — 20 documented env vars with section headers and inline comments
- [x] `pyproject.toml` — `[llm-judge]` extra (shared with Epic 36)
- [x] `tests/unit/test_capability_registry.py` — 6 tests (required/optional/extras caps)
- [x] `tests/unit/test_config_registry.py` — 9 tests (config items, secrets masking, extras check)
- [x] `tests/unit/test_readiness_service.py` — 10 tests (capabilities, configuration, readiness report, optional features)
- [x] `tests/integration/test_product_readiness_api.py` — 9 integration tests (capabilities, configuration, setup-checklist, readiness endpoints)
- [x] `docs/63_product_capability_configuration_registry.md` — design doc
- [x] `docs/contracts/product_configuration_contract.md` — contract with capability/config definitions, readiness, API
- [x] `docs/contracts/product_api_contract.md` — updated with capability/configuration endpoints
- [x] `README.md` — Product Setup section added
- [x] `ROADMAP.md`, `EVALS.md` updated
- [x] All validations passing (pytest, ruff, black, mypy, scope, docs-closure)

### Epic 37 — Product UI Workspace & Setup Flow (concluido)
- [x] `docs/plans/2026-06-11_epic-37_product-ui-workspace-setup-flow.md` — plano aprovado
- [x] `docs/64_product_ui_workspace.md` — design doc
- [x] `frontend/src/api/types.ts` — tipos TypeScript alinhados aos schemas Pydantic
- [x] `frontend/src/api/client.ts` — fetch genérico com tratamento de erro
- [x] `frontend/src/api/product.ts` — funções para cada endpoint product
- [x] `frontend/src/App.tsx` — routing por estado local (setup, capabilities, startups, opportunities, analysisRun, dossier)
- [x] `frontend/src/components/SetupReadinessView.tsx` — readiness, setup checklist, blocking/optional config
- [x] `frontend/src/components/CapabilitiesView.tsx` — capabilities agrupadas por categoria com status visual
- [x] `frontend/src/components/StartupListView.tsx` — listar/criar startups
- [x] `frontend/src/components/StartupDetailPanel.tsx` — detalhe + edição básica + run analysis
- [x] `frontend/src/components/AnalysisRunDetailView.tsx` — scores, gaps, mappings, claims, quality, readiness checks
- [x] `frontend/src/components/OpportunitiesView.tsx` — tabela ranqueada com paginação
- [x] `frontend/src/components/DossierView.tsx` — Markdown + JSON raw + copy + regenerate
- [x] `frontend/src/components/QualitySummaryPanel.tsx` — métricas pass/fail
- [x] `frontend/src/components/ReviewForm.tsx` — review de analysis run e claims
- [x] `frontend/.env.example` — VITE_API_BASE_URL + VITE_APP_ENV
- [x] `Makefile` — alvo `ui-e2e-product` separado
- [x] `tests/e2e/test_product_ui.spec.ts` — Playwright E2E smoke tests
- [x] `README.md` — seção "Run the Product UI" atualizada
- [x] Sem react-router-dom, TanStack Query, mock como fluxo principal
- [x] UI consome Product API real, não lê data/demo_runs
- [x] Nenhuma alteração em scoring, RAG, Qdrant, recommendation central

### Epic 38 — End-to-End Product Acceptance & Release Hardening (concluído)
- [x] `docs/plans/2026-06-13_epic-38_end-to-end-product-acceptance-release-hardening.md` — plano
- [x] `docs/65_end_to_end_product_acceptance.md` — design doc
- [x] `docs/contracts/product_acceptance_contract.md` — contrato de aceitação
- [x] `tests/fixtures/product_golden_path/` — fixture golden (startup.json + expected.json)
- [x] `tests/acceptance/` — acceptance tests (golden path, no-demo-dependency, fixture shape)
- [x] `scripts/product_acceptance_report.py` — relatório de readiness
- [x] `Makefile` — targets: acceptance, acceptance-backend, prepare-release, product-readiness-report
- [x] `README.md` — seção Quickstart + Troubleshooting
- [x] `ROADMAP.md`, `EVALS.md`, `DECISIONS.md`, `AGENTS.md` — atualizados
- [x] `tests/e2e/test_product_ui.spec.ts` — E2E expandido (6 tests)
- [x] Frontend build passa (`npm run build`)
- [x] Nenhuma alteração em scoring, RAG, Qdrant, recommendation central

### Epic 39 — Project-Wide Error & Limitation Cleanup (concluído)
- [x] mypy: 5 errors fixed (structured_outputs.py, quality/service.py)
- [x] ruff: 73 errors → 0 (migrations excluded, 3 files fixed)
- [x] black: `.pytest_tmp*`, `node_modules/`, `.git/` excluded; 6 files reformatted
- [x] pyproject.toml: pytest markers added, sentence-transformers version fixed
- [x] Makefile: hierarchical targets (validate-fast, validate-full, test-unit, etc.)
- [x] scripts/validate.sh: marker filter updated
- [x] ERROR_LOG.md, DECISIONS.md, ROADMAP.md, README.md, EVALS.md, AGENTS.md updated
- [x] docs/66_project_wide_error_limitation_cleanup.md created
- [x] docs/plans/2026-06-13_epic-39_project-wide-error-limitation-cleanup.md created
- [x] All validations passing (pytest, ruff, black, mypy, scope, docs-closure)
- [x] Nenhuma alteração em scoring, RAG, Qdrant, recommendation central

### Later Backlog
- Documentation Pruning (consolidation of remaining early docs)
- Human-in-the-loop review implementation
- Professional exports
- LangGraph orchestration
- Cross-encoder reranking
- Optional real LLM judge provider
