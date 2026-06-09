# DECISIONS

## Decision 001 - Use LangGraph for multi-agent orchestration

- Context: The project needs modular agent workflows with explicit state transitions and future human review points.
- Decision: Use LangGraph as the workflow orchestration layer.
- Alternatives considered: Plain Python pipelines, custom orchestrator, other agent frameworks.
- Rationale: LangGraph fits graph-based orchestration and makes future agent state explicit.
- Risks: Framework complexity before agents are mature.
- Validation: Confirm that the final workflow remains inspectable, typed, and testable.

## Decision 002 - Use Pydantic for schemas

- Context: Structured outputs must be validated and traceable.
- Decision: Use Pydantic models and enums as the source of truth for core data contracts.
- Alternatives considered: Dataclasses, raw dictionaries, Marshmallow.
- Rationale: Pydantic offers strong validation and clear JSON-oriented models.
- Risks: Schema drift between docs and code.
- Validation: Keep schema docs and unit tests aligned with the models.

## Decision 003 - Use PostgreSQL for structured data

- Context: Startup profiles, evidence metadata, and recommendations require reliable structured persistence.
- Decision: Use PostgreSQL as the relational data store.
- Alternatives considered: SQLite, MySQL, document databases.
- Rationale: PostgreSQL is production-friendly and matches the project's expected growth.
- Risks: More setup than a local lightweight database.
- Validation: Keep the initial schema simple and verify local Docker startup.

## Decision 004 - Use Qdrant for vector storage

- Context: NVIDIA knowledge retrieval will require chunk embeddings and vector search.
- Decision: Use Qdrant as the vector database.
- Alternatives considered: pgvector, Weaviate, Chroma.
- Rationale: Qdrant is focused, well-supported, and easy to scaffold locally.
- Risks: Early architectural commitment before retrieval requirements settle.
- Validation: Evaluate retrieval quality and operational simplicity during the RAG phase.

## Decision 005 - Use Obsidian as research wiki and the repo as production

- Context: The team needs a flexible research workspace without mixing draft notes into production artifacts.
- Decision: Use Obsidian for capture and the repository for versioned production assets.
- Alternatives considered: Keeping everything in markdown under docs, external wiki tools.
- Rationale: Obsidian supports rapid capture while the repo stays clean and reviewable.
- Risks: Notes may diverge from production artifacts if not curated.
- Validation: Use regular promotion from vault notes into repo docs and examples.

## Decision 006 - Use versioned skills for AI work

- Context: The project depends on repeatable AI behaviors with explicit criteria.
- Decision: Store reusable skills in versioned files under `skills/`.
- Alternatives considered: Ad hoc prompts only, external prompt libraries.
- Rationale: Versioned skills improve consistency, reviewability, and reuse.
- Risks: Skill sprawl if not curated.
- Validation: Review skills during agent implementation and keep only active, useful ones.

## Decision 007 - Use AI-Native Defensibility Score as a differentiator

- Context: NVIDIA needs more than binary startup classification.
- Decision: Add an explicit defensibility lens as part of the long-term evaluation model.
- Alternatives considered: Simpler maturity-only scoring, purely qualitative ranking.
- Rationale: Defensibility helps distinguish durable startups from superficial wrappers.
- Risks: Score inflation or weak grounding without strong evidence.
- Validation: Require explicit criteria and compare manual scoring outcomes.

## Decision 008 - Use Spec -> Build -> Critique -> Eval -> Commit

- Context: The project must stay controlled and auditable while using AI heavily.
- Decision: Adopt a mandatory delivery loop of Spec, Build, Critique, Eval, and Commit readiness.
- Alternatives considered: Build-first, informal review, ad hoc iteration.
- Rationale: The loop enforces discipline and reduces premature complexity.
- Risks: Slower early iteration if applied too rigidly.
- Validation: Track whether the workflow improves clarity, testability, and decision quality.

## Decision 009 — Dual Scoring Engine combina Defensibility + Inception Fit

- Context: O case final posiciona o Radar como plataforma de Opportunity Intelligence com scoring duplo. Um score único não capturaria a nuance entre "startup defensível" e "startup com fit comercial NVIDIA".
- Decision: Adotar dois scores separados (AI-Native Defensibility Score 0-100 e NVIDIA Inception Fit Score 0-100) combinados em um score composto com pesos α (defensibility) e β (inception fit) configuráveis por contexto (hunter mode vs quality mode).
- Alternatives considered: Score único híbrido, apenas Defensibility Score, apenas Inception Fit Score, classificação qualitativa sem score.
- Rationale: Dois scores separados evitam falsa precisão, permitem que o usuário NVIDIA pondere conforme objetivo (prospecção vs qualidade) e expõem trade-offs claros.
- Risks: Scores podem ser mal interpretados se apresentados sem contexto de confiança. Calibração inicial pode não refletir julgamento de especialista.
- Validation: Comparar scores com avaliação manual de especialista NVIDIA em 10 startups. Ajustar pesos até correlação ≥0,7.

## Decision 010 — Confidence-aware Ranking com bandeira explícita

- Context: Evidência pública sobre startups brasileiras é frequentemente incompleta. Um ranking que ignora essa incerteza engana o usuário.
- Decision: O ranking pondera scores por confiança das evidências (cobertura de fontes, consistência, proporção fato/inferência, recência) e exibe badges visuais: 🟢 Alta (≥70%), 🟡 Média (40-69%), 🔴 Baixa (<40%). Startups com baixa confiança nunca são descartadas, mas nunca são superestimadas.
- Alternatives considered: Ranking sem ponderação, threshold mínimo para entrar no ranking, esconder startups com baixa confiança.
- Rationale: Startups promissoras com pouca evidência pública não devem ser ignoradas, mas o usuário precisa saber que o diagnóstico é frágil.
- Risks: Usuário pode ignorar badges e tratar scores como precisos. Badges podem ser muito conservadores no início.
- Validation: Testar ranking com cenários de evidência parcial e verificar se badges correspondem ao julgamento humano de confiança.

## Decision 011 — Suggested Technical Experiment é hipotético e acionável

- Context: O grande diferencial do Radar frente a ferramentas de inteligência tradicionais é entregar não apenas diagnóstico, mas um experimento técnico concreto que a startup pode executar.
- Decision: O experimento é explicitamente hipotético (não é diagnóstico nem promessa), mas deve ser específico, mensurável e acionável. Segue template fixo: título, gap alvo, hipótese, métrica, duração estimada, tecnologia NVIDIA envolvida, próximo passo concreto.
- Alternatives considered: Não incluir experimento, incluir apenas link para documentação NVIDIA, recomendar ação comercial genérica.
- Rationale: Um experimento concreto é o gancho técnico-comercial mais forte para o time NVIDIA iniciar uma conversa. Ele demonstra aplicação prática da tecnologia.
- Risks: Experimento pode ser tecnicamente inválido se baseado em inferência fraca. Pode soar como presunção se não for claramente marcado como hipótese.
- Validation: Revisão por arquiteto de soluções NVIDIA em 70%+ dos casos. Template exige que todo experimento explicite sua hipótese e métrica.
