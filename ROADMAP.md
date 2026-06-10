# ROADMAP — Status Real (Junho 2026)

## ✅ Concluídos

### Epic 0 — Case Consolidation (concluído)
- [x] docs/00_case_plan.md
- [x] docs/08_demo_script.md
- [x] docs/09_user_workflow.md
- [x] ROADMAP.md
- [x] DECISIONS.md
- [x] README.md

### Epic 1 — Foundation (Scraping + Extraction)
- [x] Fetch public page (`src/scraping/fetcher.py`)
- [x] Parse HTML to clean text (`src/scraping/parser.py`)
- [x] Source policy (`src/scraping/source_policy.py`)
- [x] Structured extraction (`src/extraction/extractor.py`)
- [x] Pydantic schemas (`src/extraction/schemas.py`)
- [x] 14 unit tests

### Epic 2 — AI-native Classification
- [x] 5-level heuristic classifier (`src/classification/ai_native_classifier.py`)
- [x] Fact/Inference/Hypothesis separation
- [x] 10 unit tests covering all levels

### Epic 3 — Evidence Validation
- [x] Deterministic evidence validator (`src/validation/evidence_validator.py`)
- [x] Confidence recalibration per source type
- [x] 14 unit tests

### Epic 4 — Dual Scoring Engine
- [x] AI-Native Defensibility Score (`src/scoring/defensibility_score.py`, 6 dims)
- [x] NVIDIA Inception Fit Score (`src/scoring/inception_fit_score.py`, 4 dims)
- [x] Composite score with configurable weights
- [x] 6 + 6 + 9 = 21 unit tests with golden examples

### Epic 5 — Production AI Readiness
- [x] 4-dimension readiness scoring (`src/scoring/production_readiness.py`)
- [x] Evidence-aware confidence penalty
- [x] 6 unit tests

### Epic 6 — Composite Ranking + Motion Hints
- [x] Confidence-aware weighted ranking (`src/scoring/composite_ranking.py`)
- [x] Motion hints (immediate_outreach → not_recommended)
- [x] 9 unit tests

### Epic 7 — Gap Diagnosis + NVIDIA Mapping
- [x] 15 gap detectors (`src/diagnosis/gap_diagnosis.py`, 902 lines)
- [x] NVIDIA technology mapping matrix (`src/diagnosis/nvidia_mapping.py`, 228 lines)
- [x] Schemas tipados (EvidenceTag, GapWithEvidence, NvidiaTechnologyCandidate, GapDiagnosisResult)
- [x] Gaps inferidos marcados como INFERRED
- [x] Output inclui evidence_used e missing_evidence
- [x] Cobertura: 10/15 gaps testados individualmente
- [x] Coverage mapping: todos os 15 gaps têm ≥1 tecnologia NVIDIA
- [x] 14 + 6 + 1 = 21 unit tests

### Epic 7.1 — Architecture Utilization Audit + Pipeline Integration
- [x] Pipeline orchestrator (`src/pipeline/run_pipeline.py`, 7 steps)
- [x] Pipeline calls all 3 scores + composite ranking
- [x] 5 pipeline unit tests
- [x] AGENTS.md updated with closure checklist
- [x] README.md with Current Capabilities + Known Limitations
- [x] DECISIONS.md updated
- [x] EVALS.md with real coverage
- [x] docs/25_end_of_epic_closure.md
- [x] docs/26_architecture_utilization_audit.md
- [x] Obsidian vault backfill

### Epic 8 — Recommendation Engine (concluído)
- [x] Schemas tipados: SuggestedTechnicalExperiment, RecommendedNextAction, PerGapRecommendation, RecommendationResult
- [x] Engine determinístico sem RAG, LangGraph ou LLM
- [x] Action matrix com 4 ações (approach_now → not_recommended)
- [x] Prioridade e complexidade por gap + tecnologia
- [x] SuggestedTechnicalExperiment gerado apenas para APPROACH_NOW (14 templates)
- [x] 22 unit tests (ação, prioridade, experimentos, per-gap, integração)
- [x] NvidiaRecommendation antigo removido de src/extraction/schemas.py
- [x] docs/06_recommendation_logic.md reescrito

### Epic 7.2 — Development Workspace Quality System (concluído)
- [x] docs/plans/PLAN_TEMPLATE.md
- [x] docs/adr/ADR_TEMPLATE.md
- [x] docs/contracts/ — 6 contratos de desenvolvimento
- [x] docs/27_developer_rag_design.md
- [x] docs/28_development_workspace_quality.md
- [x] 7 prompts versionados
- [x] AGENTS.md com 10 regras de workspace
- [x] DECISIONS.md com 5 decisões de workspace
- [x] EVALS.md com critérios de qualidade do desenvolvimento
- [x] Obsidian — 5 notas em 02 Project Control/

### Epic 9.1 — Integrate Diagnosis and Recommendation into Full Pipeline (concluído)
- [x] Pipeline estendido de 7 para 11 steps
- [x] `run_full_pipeline()` agora chama gap diagnosis, NVIDIA mapping e recommendation engine
- [x] `PipelineResult` inclui `gap_diagnosis` e `recommendation`
- [x] missing_evidence propagado de todos os módulos até o output final
- [x] Nenhuma tecnologia NVIDIA recomendada sem gap diagnosticado
- [x] Evidência fraca reduz força da recomendação (action != APPROACH_NOW)
- [x] 10 pipeline tests (5 existentes atualizados + 5 novos)
- [x] Total: 148 testes (138 + 10)
- [x] Contrato pipeline_output atualizado para v2.0
- [x] DECISIONS.md: Decision 016 registrada

---

## 🚧 Em andamento / Próximos

### Epic 10 — Startup Action Brief (concluído)
- [x] `src/briefing/` module with schemas, builder, and markdown renderer
- [x] `StartupActionBrief` Pydantic schema with 13 sections
- [x] `build_action_brief(PipelineResult) → StartupActionBrief`
- [x] `render_action_brief_markdown(brief) → str`
- [x] Verdict logic (high_priority → not_recommended)
- [x] Evidence-aware: uncertainties, missing_evidence preserved
- [x] No NVIDIA tech without diagnosed gap
- [x] 10 unit tests (high-fit, weak, no-gap, missing, markdown, JSON, schema)
- [x] `docs/16_briefing_template.md` reescrito
- [x] `docs/contracts/briefing_contract.md` criado
- [x] Total: 153 tests, 17 arquivos

### Epic 11 — Product RAG / Playbook Retrieval (concluído)
- [x] `data/nvidia_corpus/` com 10 documentos Markdown mapeados para 15 gaps e 14 experimentos
- [x] `src/rag/schemas.py` — RagSource, RagDocument, RagChunk, RetrievalQuery, RetrievedContext, PlaybookRetrievalResult
- [x] `src/rag/ingestion.py` — load_sources(), load_markdown_document(), chunk_document(), load_and_chunk_corpus()
- [x] `src/rag/retrieval.py` — ChunkIndex in-memory, retrieve(), retrieve_by_gap_type(), retrieve_by_technology()
- [x] `src/rag/playbook_retriever.py` — PlaybookRetriever.retrieve_for_gaps(), retrieve_for_brief()
- [x] Chunking determinístico por headings `##`, metadados preservados
- [x] Retrieval lexical sem embeddings, sem Qdrant, sem novas dependências
- [x] Provenance obrigatória: cada chunk carrega source_id, url, product
- [x] RAG enriquece mas nunca decide (brief funciona sem RAG)
- [x] `docs/35_product_rag_design.md` criado
- [x] `docs/contracts/rag_contract.md` criado
- [x] Total: 168 tests, 20 arquivos

### Epic 12 — RAG Evaluation & Retrieval Quality Gates (concluído)
- [x] `src/evaluation/rag_eval_schemas.py` — RagEvalCase, RagRetrievalMetrics, RagEvalResult, RagQualityGateResult
- [x] `src/evaluation/rag_eval.py` — run_rag_eval(), run_quality_gates(), format_eval_summary()
- [x] `examples/rag_eval/golden_queries.json` — 16 golden queries (10 gaps + 6 negativos)
- [x] `examples/rag_eval/expected_contexts.json` — chunk_ids esperados por query
- [x] 7 métricas: hit_at_k, source/product coverage, irrelevant/missing, top_1_match, precision
- [x] 6 quality gates: hit_at_3, top_1, zero_missing, irrelevant_limit, provenance, missing_explicit
- [x] 20 testes (golden, métricas, gates, provenance, brief compatibilidade)
- [x] `docs/36_rag_evaluation.md` criado
- [x] Total: 188 tests, 21 arquivos
- [x] Nenhuma alteração em RAG, Briefing, Pipeline, Recommendation, Diagnosis
- [x] Nenhuma dependência nova, embedding, Qdrant, LangGraph, LLM judge

### Epic 13 — Embeddings + Vector Store Retrieval (concluído)
- [x] `src/rag/embeddings.py` — EmbeddingProvider (abstract), MockEmbeddingProvider, SentenceTransformerProvider
- [x] `src/rag/vector_store.py` — InMemoryVectorStore with cosine similarity + metadata filters
- [x] `src/rag/semantic_retrieval.py` — semantic_retrieve() with metadata filters
- [x] `src/rag/hybrid_retrieval.py` — hybrid_retrieve() with RRF fusion and lexical fallback
- [x] `src/evaluation/rag_eval_schemas.py` — + RetrievalMode, ModeEvalResult, RagEvalComparison
- [x] `src/evaluation/rag_eval.py` — + run_mode_eval(), run_comparison_eval(), format_comparison_summary()
- [x] 52 new tests (embeddings 11, semantic 15, hybrid 12, eval 14)
- [x] `docs/37_embeddings_vector_store.md` created
- [x] `docs/contracts/rag_contract.md` updated
- [x] Total: 236 tests, 25 arquivos
- [x] In-memory vector store (no external deps for tests)
- [x] Mock embedding provider (deterministic, no model download)
- [x] RAG Evaluation compares lexical/semantic/hybrid with regression detection
- [x] Action Brief unchanged — works without vector store

### Epic 14 — Reranking e Context Packing Determinísticos (concluído)
- [x] `src/rag/reranking.py` — deterministic composite score (gap/tech boost + provenance/duplicate/irrelevant penalties), clamped to [0,1]
- [x] `src/rag/context_packing.py` — dedup, classify by gap/tech, apply per-gap/per-tech/global limits, compute metrics
- [x] `src/rag/schemas.py` — RerankingConfig, PackedContext, DroppedContext, PackingConfig, PackingResult, SupportingNvidiaContext
- [x] `src/evaluation/rag_eval_schemas.py` — 2 new modes (HYBRID_RERANKED, HYBRID_RERANKED_PACKED), 8 new metric fields
- [x] `src/evaluation/rag_eval.py` — 5-mode support, regression detection for all later modes
- [x] `src/briefing/schemas.py` — 3 optional packed-context fields
- [x] `src/briefing/action_brief.py` — accepts optional PackingResult, injects Supporting NVIDIA Context section
- [x] `src/briefing/markdown_renderer.py` — renders Supporting NVIDIA Context section with score and provenance
- [x] 38 new tests (reranking 9, packing 13, eval 11, brief 5)
- [x] `docs/38_rag_reranking_context_packing.md` created
- [x] `docs/contracts/rag_contract.md` updated
- [x] Total: 276 tests, 29 arquivos

### Epic 14.1 — Integrate RAG Reranking + Context Packing into Main Pipeline (concluído)
- [x] `src/rag/rag_pipeline.py` — `run_rag_pipeline()` orchestration (hybrid retrieval → rerank → pack)
- [x] `src/rag/schemas.py` — `RagPipelineOutput` schema
- [x] `src/pipeline/run_pipeline.py` — Step 11 (RAG), `rag_output` field, optional RAG parameters
- [x] `src/briefing/action_brief.py` — auto-extract packing_result from PipelineResult.rag_output
- [x] 10 new tests (pipeline with RAG, without RAG, empty index, brief section, dropped not in brief, motion unchanged, provenance, quality summary, backward compat, lexical mode)
- [x] `docs/contracts/pipeline_output_contract.md` updated (v3.0)
- [x] `docs/contracts/rag_contract.md` updated
- [x] `docs/contracts/briefing_contract.md` updated (v2.0)
- [x] Total: 286 tests, 30 arquivos
- [x] RAG integrated as optional Step 11 — no impact on scoring, diagnosis, or recommendation

### Epic 15 — Persistent Vector Store with Qdrant (concluído)
- [x] `src/rag/vector_store.py` — VectorStore ABC extraída, InMemoryVectorStore herda dela
- [x] `src/rag/qdrant_store.py` — QdrantStore(VectorStore) com lazy connection, payload rico, filtros server-side
- [x] `src/rag/semantic_retrieval.py`, `hybrid_retrieval.py`, `rag_pipeline.py` — tipagem alterada para VectorStore (polimórfico)
- [x] `src/evaluation/rag_eval.py` — tipagem alterada para VectorStore
- [x] `tests/unit/test_qdrant_store.py` — 20 testes (sem Qdrant)
- [x] `tests/integration/test_qdrant_rag_pipeline.py` — 9 testes (skippable)
- [x] `.env.example` — +RAG_VECTOR_BACKEND, QDRANT_COLLECTION, QDRANT_VECTOR_SIZE
- [x] `docker-compose.yml` — healthcheck no Qdrant
- [x] `docs/39_qdrant_persistent_vector_store.md`
- [x] `docs/contracts/rag_contract.md` — + QdrantStore API + payload schema + invariants
- [x] Payload schema: chunk_id, source_id, source_title, source_url, product, gap_types, version, content_hash, collected_at, document_type, provenance
- [x] Filtros obrigatórios: product, gap_type, source_id, version, document_type
- [x] Total: 315 testes (306 unit + 9 integration skippable), 31 test files
- [x] Qdrant opcional — RAG continua funcionando sem Qdrant

### Epic 16 — CI/CD, Validation Automation & Quality Gates (concluído)
- [x] `.github/workflows/ci.yml` — GitHub Actions CI (ruff, black, mypy, pytest)
- [x] `.pre-commit-config.yaml` — pre-commit hooks (trailing-whitespace, end-of-file-fixer, check-yaml/toml/json, check-added-large-files, ruff, black)
- [x] `Makefile` — targets: test, lint, format-check, typecheck, validate, rag-eval, ci
- [x] `scripts/validate.sh` — local validation runner
- [x] `scripts/check_scope.py` — detects sensitive area changes, requires contract/doc/EVALS updates
- [x] `scripts/check_docs_closure.py` — verifies plan, ROADMAP, EVALS, Obsidian, Known Limitations before epic close
- [x] `tests/unit/test_check_scope.py` — 7 tests
- [x] `tests/unit/test_check_docs_closure.py` — 6 tests
- [x] `docs/40_ci_cd_quality_gates.md` — design doc
- [x] `AGENTS.md`, `README.md`, `EVALS.md`, `ROADMAP.md`, `DECISIONS.md` updated
- [x] Obsidian vault backfill
- [x] Total: 329 tests (315 existing + 14 new), 34 test files
- [x] No changes to src/ or product tests

### Epic 17 — Golden Eval Harness (End-to-End Pipeline Regression Detection) (concluído)
- [x] 7 JSON golden cases in `examples/golden/` (high_fit, weak_evidence, non_ai, no_rag_context, rag_supported, validate_manually, monitor_or_discard)
- [x] `expected_outputs.json` — cross-check matching every case
- [x] `examples/golden/README.md` — golden case documentation
- [x] `tests/evals/helpers.py` — GoldenCase, load_golden_case, run_pipeline_on_case, run_pipeline_with_rag, 11 assert helpers
- [x] `tests/evals/test_pipeline_golden.py` — 38 tests across 6 test classes + 3 cross-cutting checks
- [x] All golden evals run offline (MockEmbeddingProvider + InMemoryVectorStore — no Qdrant, no sentence-transformers)
- [x] RAG golden cases verify motion stability, context-in-brief, context-not-in-evidence
- [x] `docs/41_end_to_end_eval_harness.md`
- [x] DECISIONS.md — Decision 025
- [x] EVALS.md — golden eval section
- [x] README.md — updated test count, removed "no eval harness" limitation
- [x] Obsidian vault backfill
- [x] Total: 358 tests (329 pre-existing + 38 golden evals), 36 test files
- [x] No changes to src/ — pure test infrastructure

### Epic 18 — Automated Qdrant Corpus Ingestion (concluído)
- [x] `scripts/ingest_nvidia_corpus.py` — script de ingestão automatizada
- [x] CLI com `--dry-run`, `--recreate-collection`, `--skip-existing`, `--source-id`, `--product`, `--backend`, `--mock-embeddings`, `--report-path`
- [x] Validação de documentos (metadata obrigatória, arquivo vazio)
- [x] content_hash (documento) e chunk_hash (chunk) via MD5 determinístico
- [x] Embeddings via SentenceTransformerProvider ou MockEmbeddingProvider
- [x] Upsert em Qdrant com payload completo (provenance, hashes, versão, filtros)
- [x] Payload indexes automáticos (product, gap_types, source_id, version, document_type, content_hash)
- [x] Relatório de ingestão com contadores
- [x] Idempotência via chunk_hash + --skip-existing
- [x] Nenhuma chamada externa, nenhum scraping, nenhum crawler
- [x] `src/rag/schemas.py` — +version, document_type, content_hash em RagChunk/RagSource
- [x] `src/rag/vector_store.py` — +version, document_type, content_hash, chunk_hash, ingestion_run_id em VectorEntry
- [x] `src/rag/qdrant_store.py` — payload indexes + novos campos no payload
- [x] `data/nvidia_corpus/sources.yaml` — +version, document_type por source
- [x] `tests/unit/test_ingest_nvidia_corpus.py` — 17 testes
- [x] `tests/integration/test_qdrant_corpus_ingestion.py` — 3 testes (skippable)
- [x] `docs/42_automated_qdrant_corpus_ingestion.md`
- [x] Total: 375 tests (358 pre-existing + 17 novos), 37 test files
- [x] README / EVALS / ROADMAP / docs / Obsidian atualizados

### Product RAG (V3 — futuro / backlog)
- Reranking cross-encoder (alternativa ao reranking determinístico)
- Ingestão automatizada de documentação NVIDIA via crawler respeitando robots.txt

---

## 📋 Backlog (não iniciado)

### Agents (LangGraph)
- Multi-agent orchestration graph
- Human-in-the-loop review

### Interface
- FastAPI endpoints
- Streamlit MVP
- Export paths

### Production Readiness
- Docker Compose
- PostgreSQL + Qdrant
