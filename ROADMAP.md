# ROADMAP

## Phase 1 - Foundation

- Repository structure
- Core documentation
- Schemas
- Skills
- Prompts
- Obsidian vault
- Evaluation scaffolds
- Initial tests

## Phase 2 - Minimal Scraping

- Fetch a public page
- Extract clean text
- Save metadata
- Build an initial startup profile

## Phase 3 - Agents

- Search Planner
- Scraper Agent
- Extractor Agent
- Classifier Agent
- Evidence Validator

## Phase 4 - NVIDIA RAG

- Ingestion
- Chunking
- Qdrant integration
- Hybrid retrieval
- Reranking
- Citations

## Phase 5 - Recommendation

- Gap diagnosis
- NVIDIA mapping
- Prioritization
- Technical and business justification

## Phase 6 - Briefing and Interface

- Executive briefing
- Streamlit MVP
- Export paths

## Phase 7 - Differentiation

- AI-Native Defensibility Score
- Startup ranking
- Startup comparison
- Human-in-the-loop review

---

## Case Epics (sobreposição às fases técnicas)

Os épicos abaixo representam o plano de entrega do case final, do documento ao código. Eles não substituem as fases técnicas acima — as complementam, organizando a implementação em torno da proposta de valor do Radar.

### Epic 0 — Case Consolidation (concluído)

- [x] docs/00_case_plan.md
- [x] docs/08_demo_script.md atualizado
- [x] docs/09_user_workflow.md atualizado
- [x] ROADMAP.md atualizado
- [x] DECISIONS.md atualizado
- [x] README.md atualizado

### Epic 1 — Dual Scoring Engine

- AI-Native Defensibility Score (lógica, pesos, validação)
- NVIDIA Inception Fit Score
- Score composto com pesos configuráveis (α/β)
- Testes com golden examples
- Documentação dos algoritmos

### Epic 2 — Confidence-aware Ranking

- Algoritmo de ranking ponderado por confiança
- Badges de confiança (alta/média/baixa)
- Testes com cenários de evidência parcial
- Validação contra ranking manual

### Epic 3 — Suggested Technical Experiment

- Template de experimento
- Lógica de recomendação baseada em gap de maior prioridade
- Validação com arquiteto de soluções NVIDIA
- Testes de plausibilidade técnica

### Epic 4 — Startup Action Brief

- Montagem do brief completo (scores + gaps + experimento)
- Output em markdown e JSON
- Testes de completeza e acionabilidade
- Integração com pipeline existente

### Epic 5 — Demo Integration

- Script de demo funcional (CLI)
- Cenário único ponta-a-ponta
- Documentação de apresentação
- Preparação para validação com time NVIDIA
