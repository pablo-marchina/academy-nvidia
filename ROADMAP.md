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

### Epic 10 — End-to-End CLI
- [ ] `radar analyze <startup-name> <url1> <url2> ...`
- [ ] Batch mode for multiple startups
- [ ] Report generation (markdown, JSON)

---

## 📋 Backlog (não iniciado)

### RAG Pipeline
- Ingestion + chunking + Qdrant
- Hybrid retrieval + reranking
- NVIDIA playbook retrieval

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
- CI/CD
