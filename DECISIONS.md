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

## Decision 012 — Pipeline Orchestrator como integrador determinístico

- Context: Os módulos de scoring (defensibility, inception fit, production readiness) foram implementados como funções independentes. Era necessário um orquestrador que as chamasse na ordem correta, consolidasse resultados e garantisse rastreabilidade.
- Decision: Criar `src/pipeline/run_pipeline.py` com `run_full_pipeline()` que executa 7 steps em sequência determinística: extração → classificação → validação → defensibility → inception fit → production readiness → composite ranking. O output é um `PipelineResult` Pydantic com todos os campos intermediários e finais.
- Alternatives considered: LangGraph graph, script ad hoc, cada módulo chamado manualmente.
- Rationale: Um orquestrador determinístico mantém a pipeline testável, rastreável e substituível por LangGraph no futuro sem mudar contratos.
- Risks: Pipeline pode crescer demais se não houver disciplina de separação.
- Validation: 5 testes unitários verificam ordem, campos obrigatórios e tratamento de evidência fraca.

## Decision 013 — Production AI Readiness como quarto pilar do Composite Score

- Context: O Composite Score original considerava apenas defensibility (α) e inception fit (β). Produção AI Readiness foi adicionada como dimensão independente para capturar maturidade operacional.
- Decision: O Composite Score agora usa 4 pilares com pesos fixos: defensibility 30%, inception fit 25%, production readiness 35%, classification 10%. Pesos redistribuem proporcionalmente quando um pilar está ausente.
- Alternatives considered: Manter apenas 2 scores, adicionar como bônus, média simples.
- Rationale: Production readiness é o melhor preditor de adoção real de infraestrutura NVIDIA. Peso maior reflete prioridade comercial.
- Risks: Startup early-stage sem produção será penalizada — mitigado pelo confidence penalty que sinaliza baixa confiança em vez de descartar.
- Validation: Testes de composite ranking verificam redistribuição de pesos e confidence penalty.

## Decision 014 — Gap Diagnosis como módulo independente (não integrado ao pipeline)

- Context: O diagnóstico de gaps técnicos (`src/diagnosis/gap_diagnosis.py`) é o maior arquivo do projeto (902 linhas, 15 detectores). Ele depende de todos os 3 scores e da classificação.
- Decision: Manter gap diagnosis como módulo independente chamável sob demanda, não integrado ao pipeline principal. A integração será feita quando o Recommendation Engine estiver pronto.
- Alternatives considered: Integrar imediatamente, fundir com o scoring.
- Rationale: Evitar acoplamento prematuro. O pipeline já expõe os dados necessários (scores, classification, validated_evidence) para que gap diagnosis os consuma quando for integrado.
- Risks: Módulo pode ficar obsoleto se não for revisado periodicamente.
- Validation: 9 testes unitários verificam detectores individuais. Coverage mapping testa que todos os 15 gaps têm ao menos uma tecnologia NVIDIA mapeada.

---

## Decisões do Workspace de Desenvolvimento

Estas decisões são sobre o **processo de desenvolvimento**, não sobre a arquitetura do produto.

### WSD-001 — Plan Artifacts Obrigatórios

- **Context:** Planos eram conversa temporária, sem versionamento. Não havia rastreabilidade do que foi planejado vs implementado.
- **Decision:** Todo plano não trivial deve ser salvo em `docs/plans/` antes do Build Mode. O template está em `docs/plans/PLAN_TEMPLATE.md`.
- **Consequences:** Planos são versionados e auditáveis. Custo adicional de ~5 minutos por plano para salvar o artifact.
- **Status:** Implementado no Epic 7.2.

### WSD-002 — Developer RAG como Memória de Desenvolvimento

- **Context:** O agente IA não tem memória persistente. Decisões, regras e contratos ficam espalhados e são esquecidos entre sessões.
- **Decision:** Criar uma fundação documental para Developer RAG (`docs/27_developer_rag_design.md`) com fontes indexáveis, fontes proibidas, regras de qualidade e critérios de avaliação. Implementação de vector DB é adiada.
- **Consequences:** Documentos estruturados e prontos para indexação futura. Nenhum código de RAG foi implementado.
- **Status:** Implementado no Epic 7.2.

### WSD-003 — Review Diff Obrigatório

- **Context:** Não havia revisão sistemática do diff antes do commit. Mudanças fora de escopo, contratos quebrados e docs desatualizados passavam despercebidos.
- **Decision:** Review Diff é obrigatório antes de todo commit (prompt em `prompts/review_diff.md`). Verifica escopo, contratos, docs, testes, Obsidian, alucinações.
- **Consequences:** Reduz erros de commit. Adiciona ~2 minutos ao ciclo.
- **Status:** Implementado no Epic 7.2.

### WSD-004 — Contratos de Desenvolvimento

- **Context:** Módulos do produto não tinham contratos formais. A IA poderia assumir comportamentos que os módulos não implementam.
- **Decision:** Criar `docs/contracts/` com contratos para pipeline_output, evidence, scoring, diagnosis, recommendation e end_of_epic. Cada contrato define o que o módulo promete e o que NÃO promete.
- **Consequences:** Contratos reduzem ambiguidade. Precisam ser mantidos atualizados conforme os módulos evoluem.
- **Status:** Implementado no Epic 7.2.

### WSD-005 — Separação Workspace vs Produto

- **Context:** Havia confusão entre melhorias na área de trabalho de desenvolvimento vs funcionalidades do produto. Épicos misturavam docs e código.
- **Decision:** A área de trabalho de desenvolvimento (AGENTS.md, docs/plans/, docs/adr/, docs/contracts/, prompts/, Obsidian, ERROR_LOG, EVALS) é distinta da arquitetura do produto (src/, tests/). Épicos de workspace não alteram src/ ou tests/.
- **Consequences:** Separação clara de responsabilidades. ROADMAP distingue épicos de workspace vs produto.
- **Status:** Implementado no Epic 7.2.

---

## Decisões de Arquitetura do Produto (Suplementares)

### Decision 016 — Pipeline Completo com Diagnosis + Recommendation

- **Context:** Gap Diagnosis e Recommendation Engine foram implementados como módulos independentes (Decisions 014 e Epic 8). O pipeline orquestrador (`run_full_pipeline`) parava no composite ranking. Os módulos existiam mas não eram chamados.
- **Decision:** Integrar ambos os módulos no pipeline principal, adicionando 3 novos steps após o composite ranking: (8) Gap Diagnosis, (9) NVIDIA Technology Mapping, (10) Recommendation Engine. O `PipelineResult` agora inclui `gap_diagnosis` e `recommendation`.
- **Alternatives considered:** Manter separados (chamada externa pelo usuário), integrar via LangGraph, criar pipeline separado de diagnóstico.
- **Rationale:** O pipeline é o entry point único do sistema. Integrar diagnosis + recommendation completa o fluxo de ponta a ponta sem depender de chamadas manuais. A natureza determinística mantém testabilidade.
- **Risks:** Pipeline mais longo (11 steps) — compensado pela ausência de I/O nos novos steps. Módulos de diagnosis (902 linhas) e recommendation (414 linhas) são puramente determinísticos.
- **Validation:** 10 testes de pipeline (5 existentes + 5 novos) verificam ordem, shape, propagação de missing_evidence e ausência de recomendação sem gap.
- **Status:** Implementado no Epic 9.1.

### Decision 017 — Startup Action Brief como módulo de consolidação

- **Context:** O `PipelineResult` continha todos os dados brutos (scores, gaps, candidatos, recomendações, experimentos) mas não havia um formato executivo consolidado. O template existente (`docs/16_briefing_template.md`) era um esqueleto de 8 linhas sem schema ou código.
- **Decision:** Criar `src/briefing/` com schemas Pydantic (`StartupActionBrief`, `BriefVerdict`, `BriefSection`, `BriefEvidenceItem`, `BriefUncertainty`) e funções determinísticas (`build_action_brief`, `render_action_brief_markdown`). O brief é uma projeção do `PipelineResult` — nenhuma nova lógica de scoring, diagnosis ou recommendation é introduzida.
- **Alternatives considered:** Estender `PipelineResult` com mais campos, criar formato apenas Markdown sem schema, consolidar no próprio pipeline.
- **Rationale:** Módulo separado mantém pipeline enxuto. Schema Pydantic garante serialização JSON + Markdown. Verdict determinístico (confidence + motion + approach_now) evita alucinação.
- **Risks:** Brief pode duplicar informações do PipelineResult — mitigado pelo design de projeção (não cópia). Seções condicionais (Suggested Technical Experiment) podem estar ausentes em briefs de baixa confiança — comportamento esperado e documentado.
- **Validation:** 10 testes unitários cobrem high-fit, weak evidence, no gaps, missing evidence, tech blocking, uncertainties, markdown, schema, JSON.
- **Status:** Implementado no Epic 10.

### Decision 018 — Product RAG minimalista e determinístico

- **Context:** O Epic 11 requeria um módulo de RAG para recuperar snippets de documentação NVIDIA para enriquecer Startup Action Briefs. Havia restrições de zero novas dependências, zero embeddings, zero chamadas externas, zero alterações nos módulos existentes.
- **Decision:** Criar `src/rag/` como módulo independente com chunking determinístico por headings `##`, índice in-memory lexical por gap_type e technology name, scoring baseado em keyword match ratio, e orquestração via PlaybookRetriever. Corpus manual de 10 documentos Markdown em `data/nvidia_corpus/`. RAG enriquece mas nunca decide — o Action Brief funciona normalmente sem contexto RAG.
- **Alternatives considered:** Qdrant com embeddings (rejeitado por excesso de complexidade), LangGraph para orquestração (rejeitado por zero novas dependências), scraping automatizado da docs.nvidia.com (rejeitado por risco de violação de robots.txt), integração no pipeline principal (rejeitado para preservar separação de responsabilidades).
- **Rationale:** Abordagem minimalista permite testar o valor do RAG antes de investir em embeddings, vector DB e scraping. O corpus é versionado e testável. A separação em módulo próprio garante que pipeline, scoring, diagnosis, recommendation e briefing permanecem inalterados.
- **Risks:** Corpus manual pode desatualizar. Retrieval lexical perde contexto semântico. Sem embeddings, não há matching difuso (sinônimos, paráfrases).
- **Validation:** 15 testes unitários (4 ingestion + 6 retrieval + 5 playbook). Corpus verificado contra `_TECH_MATRIX` e `_EXPERIMENT_TEMPLATES`. Brief funciona sem RAG (testado).
- **Status:** Implementado no Epic 11.

### Decision 019 — RAG Evaluation offline com golden queries e quality gates

- **Context:** O Product RAG (Epic 11) foi implementado sem nenhuma camada de avaliação. Não era possível medir se o retrieval retornava o contexto correto para cada gap ou tecnologia. O Epic 12 exigia uma camada de avaliação offline, determinística, sem embeddings, sem Qdrant, sem LLM judge.
- **Decision:** Criar `src/evaluation/rag_eval.py` + `src/evaluation/rag_eval_schemas.py` com 7 métricas determinísticas (hit_at_k, source/product coverage, irrelevant/missing count, top_1_match, precision), 6 quality gates, e dataset de 16 golden queries versionado em `examples/rag_eval/`. A avaliação reusa o `ChunkIndex` existente sem modificá-lo. O RAG Evaluation é um módulo independente que não altera pipeline, scoring, diagnosis, recommendation ou briefing.
- **Alternatives considered:** LLM judge (rejeitado por não-determinismo), Qdrant + reranking (fora de escopo), integrar no pipeline (rejeitado para preservar separação), avaliação manual (não reproduzível).
- **Rationale:** Golden queries e métricas determinísticas garantem que a qualidade do retrieval é medida de forma reproduzível e testável. Quality gates fornecem um ponto de falha explícito se o RAG degradar. A separação em módulo próprio mantém o RAG evaluation independente.
- **Risks:** Golden queries podem desatualizar se o corpus mudar. Métricas puramente lexicais não detectam degradação semântica. Quality gates podem ser muito rigorosos ou muito laxos.
- **Validation:** 20 testes unitários (golden queries, métricas, gates, provenance, brief compatibilidade). Todas as 16 golden queries passam com o corpus atual. Quality gates falham com índice vazio ou sem proveniência.
- **Status:** Implementado no Epic 12.

---

ADRs (Architectural Decision Records) individuais estão em `docs/adr/`. Cada ADR cobre uma decisão específica. Decisões neste arquivo são consolidadas para visão geral.
