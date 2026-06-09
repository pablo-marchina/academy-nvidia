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

---

## 🚧 Em andamento / Próximos

### Epic 8 — Startup Action Brief
- [ ] Brief template (markdown + JSON output)
- [ ] Consolidate scores + gaps + experiment into single output
- [ ] CLI entry point

### Epic 9 — End-to-End CLI
- [ ] `radar analyze <startup-name> <url1> <url2> ...`
- [ ] Batch mode for multiple startups
- [ ] Report generation (markdown, JSON)

---

## 📋 Backlog (não iniciado)

### RAG Pipeline
- Ingestion + chunking + Qdrant
- Hybrid retrieval + reranking
- NVIDIA playbook retrieval

### Recommendation Engine
- Gap → technology mapping integrated in pipeline
- Technical experiment suggestion
- Business justification

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
