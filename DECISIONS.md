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

### Decision 026 — Corpus Lifecycle Filtering by Default

- **Context:** Automated source sync and Qdrant ingestion made it possible for the NVIDIA corpus to contain updated, stale, expired, deprecated, or superseded content. Without lifecycle metadata and default filtering, Product RAG could retrieve obsolete context.
- **Decision:** `data/nvidia_corpus/sources.yaml` becomes the authoritative lifecycle manifest for corpus versions. RAG ingestion and vector payloads preserve freshness/versioning metadata, and default retrieval excludes inactive, deprecated, superseded, and expired chunks.
- **Alternatives considered:** Keep only content hashes without lifecycle policy; rely on full Qdrant collection recreation; filter only in audit reports and leave retrieval unchanged.
- **Rationale:** Lifecycle-aware retrieval is safer than relying on manual collection cleanup. The audit script keeps stale/expired risks visible without adding crawler scope or external calls.
- **Risks:** Existing Qdrant collections should be reingested to receive lifecycle payload fields. Stale content is currently audit-warning only, not an automatic Action Brief warning.
- **Validation:** 11 unit tests cover stale, expired, deprecated, superseded, missing metadata, duplicate active versions, fail flags, version promotion, and default retrieval/vector-store filters.
- **Status:** Implementado no Epic 20.

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

### WSD-006 — Workspace Clarification Gate

- **Context:** O AGENTS.md já regulava planos, contratos, revisão e validação, mas a IA podia gerar código, arquitetura, docs grandes, frontend, API ou prompts baseados em suposição sem verificar ambiguidade com o usuário.
- **Decision:** Adicionar a seção "Workspace Clarification Gate" no AGENTS.md que instrui a IA a fazer perguntas de esclarecimento antes de gerar algo quando houver ambiguidade relevante. Define when to ask (10 situações), when not to ask (5 situações), limite de 3 perguntas, defaults recomendados, fallback seguro se o usuário não responder, e 7 exemplos.
- **Consequences:** IA pergunta antes de gerar frontend, API, arquitetura, contratos, dependências, workflows, docs grandes, épicos grandes, pipeline ou RAG. IA não pergunta para hotfixes, passos óbvios, padrões claros ou decisões já explícitas. Se o usuário não responder, assume menor escopo seguro.
- **Status:** Implementado no Epic 26.1.

### WSD-005 — Separação Workspace vs Produto

- **Context:** Havia confusão entre melhorias na área de trabalho de desenvolvimento vs funcionalidades do produto. Épicos misturavam docs e código.
- **Decision:** A área de trabalho de desenvolvimento (AGENTS.md, docs/plans/, docs/adr/, docs/contracts/, prompts/, Obsidian, ERROR_LOG, EVALS) é distinta da arquitetura do produto (src/, tests/). Épicos de workspace não alteram src/ ou tests/.
- **Consequences:** Separação clara de responsabilidades. ROADMAP distingue épicos de workspace vs produto.
- **Status:** Implementado no Epic 7.2.

---

### Decision 024 — CI/CD, Validation Automation & Quality Gates

- **Context:** The project had a rigorous manual quality process documented in AGENTS.md, contracts, and prompts, but zero automation of linting, type-checking, testing, or documentation consistency. All 4 validation commands (pytest, ruff, black, mypy) depended on developer/agent discipline.
- **Decision:** Add GitHub Actions CI (ruff, black, mypy, pytest on push/PR to main), pre-commit hooks (trailing-whitespace, end-of-file-fixer, check-yaml/toml/json, check-added-large-files, ruff, black), a Makefile with convenience targets, `scripts/validate.sh` for local validation, and two verification scripts (`check_scope.py` for contract/doc updates on sensitive changes, `check_docs_closure.py` for epic closure completeness).
- **Alternatives considered:** GitLab CI (not GitHub-native), Azure Pipelines (overkill for current stage), no automation (status quo — too error-prone), Nox/tox (premature — single Python version).
- **Rationale:** GitHub Actions is the natural CI platform for a GitHub-hosted project. Pre-commit hooks catch formatting/lint issues before they reach CI. The Makefile and validate.sh provide a single command for local validation. `check_scope.py` ensures contract/documentation discipline is maintained when product code changes. `check_docs_closure.py` formalizes the end-of-epic checklist.
- **Risks:** CI requires a `.github/` directory and workflow file that may conflict with non-GitHub workflows. Pre-commit hooks that are too aggressive may frustrate development. `check_scope.py` uses `git diff HEAD` which may behave unexpectedly during rebase.
- **Validation:** 13 new tests (7 check_scope, 6 check_docs_closure). CI passes on push to main. `make validate` completes with 0 errors. All 319 pre-existing tests pass unchanged.
- **Status:** Implementado no Epic 16.

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
- **Status:** Implementado no Epic 12. Estendido no Epic 13 com comparação multi-modo.

### Decision 020 — Embeddings + Vector Store com in-memory store e mock embeddings

- **Context:** O Product RAG (Epic 11) usava apenas retrieval lexical. Para suportar matching semântico era necessário adicionar embeddings e vector store sem aumentar a complexidade de setup (sem exigir servidor Qdrant, Docker, ou API keys).
- **Decision:** Criar `EmbeddingProvider` abstrato com duas implementações: `MockEmbeddingProvider` (determinístico, hash-based, sem dependências) para testes, e `SentenceTransformerProvider` (modelo `all-MiniLM-L6-v2`) para uso real. O vector store é `InMemoryVectorStore` (dict + cosine similarity em pure Python). O retrieval híbrido usa RRF (Reciprocal Rank Fusion) para combinar resultados léxicos e semânticos. A avaliação RAG foi estendida com `run_comparison_eval()` que executa golden queries nos 3 modos (lexical, semantic, hybrid) e detecta regressões críticas.
- **Alternatives considered:** Qdrant server-side (rejeitado por exigir Docker/setup), Chroma/FAISS (rejeitado por dependência extra), cross-encoder reranking (muito pesado para MVP), API-based embeddings OpenaAI/NVIDIA (exigiria API key).
- **Rationale:** In-memory store + mock embeddings permitem testes determinísticos sem dependências externas. A abstração `EmbeddingProvider` permite trocar o provider sem alterar o código de retrieval. RRF é simples, robusta e não requer calibração. A arquitetura está pronta para substituir o in-memory store por Qdrant em produção.
- **Risks:** Mock embeddings não capturam relações semânticas reais — testes com mock não garantem qualidade semântica em produção. Sentence-transformers (~500MB) pode ser pesado para CI/CD. Corpus pequeno (~50 chunks) pode não beneficiar muito de retrieval semântico.
- **Validation:** 52 novos testes (11 embeddings, 15 semantic retrieval, 12 hybrid retrieval, 14 multi-mode eval). Todos passam sem chamadas externas. semantic_retrieve com store vazio retorna []. hybrid_retrieve com store vazio cai para lexical. Filtros por product/gap_type/source_id funcionam. Provenance preservada. RAG Evaluation compara os 3 modos sem regressão.
- **Status:** Implementado no Epic 13.

### Decision 021 — Reranking determinístico e context packing sem LLM

- **Context:** O Epic 14 requeria adicionar reranking e context packing ao pipeline de RAG para melhorar a qualidade dos contextos fornecidos ao Action Brief, sem dependências externas, sem LLM, sem LangGraph e sem alterar scoring, diagnosis ou recommendation.
- **Decision:** Implementar reranking determinístico em `src/rag/reranking.py` usando score composto: `relevance × 0.3 + gap_match × 0.3 + tech_match × 0.2 - provenance_penalty - duplicate_penalty - irrelevant_penalty + known_source_boost`. Context packing em `src/rag/context_packing.py` com dedup, classificação por gap/tech, limites configuráveis (per-tech=2, per-gap=3, global=5) e métricas de qualidade. A avaliação RAG foi estendida com 2 novos modos (HYBRID_RERANKED e HYBRID_RERANKED_PACKED) e 8 novos campos métricos. O Action Brief é opcionalmente enriquecido com seção "Supporting NVIDIA Context" quando packing_result é fornecido.
- **Alternatives considered:** Cross-encoder reranking (rejeitado por exigir modelo carregado em memória), LLM judge para reranking (rejeitado por não-determinismo e custo), LangGraph para orquestração de packing (rejeitado por zero novas dependências), manter RAG sem reranking/packing (rejeitado porque contextos brutos têm ruído e duplicatas).
- **Rationale:** Score composto determinístico é auditável, testável e não requer GPU ou API. Limites de packing evitam que o Action Brief receba contextos irrelevantes ou duplicados. A conversão PackedContext para RetrievedContext na camada de avaliação preserva a compatibilidade com schemas existentes.
- **Risks:** Pesos fixos podem não ser ótimos para todos os gaps/tecnologias — mitigado por RerankingConfig configurável. Limites de packing podem descartar contextos relevantes em casos de borda — métricas de noise_reduction_score e provenance_coverage expõem trade-offs.
- **Validation:** 38 novos testes (9 reranking, 13 packing, 11 eval, 5 brief). Reranking sem gap/tech boost preserva ordem original. Packing respeita limites configurados. Eval 5-modes sem regressões não-críticas. Action Brief funciona sem packing_result.
- **Status:** Implementado no Epic 14.

### Decision 022 — Pipeline RAG Integration (Step 11)

- **Context:** Epic 14 delivered reranking and context packing as standalone modules. Epic 14.1 needed to integrate them into the main pipeline so that `StartupActionBrief` receives packed RAG context from the production flow — without external calls, LLM, LangGraph, or changes to scoring/diagnosis/recommendation.
- **Decision:** `run_rag_pipeline()` lives in `src/rag/rag_pipeline.py` — keeps RAG logic isolated. Called as Step 11 inside `run_full_pipeline()` with 5 optional parameters. `build_action_brief()` auto-extracts `packing_result` from `result.rag_output` — backward compatible.
- **Alternatives considered:** RAG as standalone function called externally (adds complexity for callers). Always-run RAG (violates optional constraint).
- **Rationale:** Single entry point; RAG optional via default None parameters; zero change to existing callers.
- **Risks:** RAG does NOT alter `recommended_motion`, scores, or `evidence_used`.
- **Validation:** 10 new tests (286 total). All legacy tests unchanged.
- **Status:** Implementado no Epic 14.1.

### Decision 023 — Qdrant Persistent Vector Store (Adapter Pattern)

- **Context:** O `InMemoryVectorStore` era funcional para desenvolvimento e testes, mas não persistia dados entre sessões. Qdrant já estava no `pyproject.toml` e no `docker-compose.yml`, mas não havia código de integração. As funções de retrieval tipavam `InMemoryVectorStore` diretamente, impedindo substituição por outro backend.
- **Decision:** Extrair interface `VectorStore(ABC)` de `InMemoryVectorStore`, criar `QdrantStore(VectorStore)` com lazy connection, payload rico (11 campos), e filtros server-side. Todas as funções de retrieval passam a aceitar `VectorStore` (polimórficas).
- **Alternatives considered:** Manter `InMemoryVectorStore` como tipo concreto e adicionar conversão ad-hoc (acoplamento maior). Usar composição (mais complexo, sem ganho).
- **Rationale:** Adapter pattern com ABC permite que o restante do código ignore o backend. Lazy connection evita dependência de Qdrant em import time. Payload rico prepara para ingestão futura.
- **Risks:** QdrantStore não faz fallback automático — caller precisa capturar `QdrantConnectionError`. Testes de integração requerem `QDRANT_TEST_URL`.
- **Validation:** 20 testes unitários (mock). 9 testes integração (skippable). 306 testes legados passam sem alteração.
- **Status:** Implementado no Epic 15.

### Decision 025 — Golden Eval Harness (End-to-End Pipeline Regression Detection)

- **Context:** The project had 329 tests but zero end-to-end golden evaluations. Pipeline-level regressions (wrong motion, missing gaps, broken contracts) were only detectable by manual review. Changes to scoring, diagnosis, or recommendation logic had no automated guard against silent behavior change.
- **Decision:** Create a golden eval harness at `tests/evals/` with 7 versioned JSON golden cases covering the full output spectrum (high-fit, weak-evidence, non-AI, no-RAG-context, RAG-supported, validate-manually, monitor-or-discard). Each case stores expected `motion_in`, `min_score`/`max_score`, `expected_gaps`, `brief_min_sections`, and `has_approach_now`. Eleven assert helpers enforce pipeline contract, gap detection, motion range, missing-evidence propagation, confidence coherence, brief sections, no-tech-without-gap, no-strong-rec-without-evidence, and three RAG-specific invariants (motion stability, context-in-brief, context-not-in-evidence).
- **Alternatives considered:** Inline golden dicts in tests (not versioned, hard to review). Snapshot testing with `pytest-regtest` (external dependency, not needed for deterministic pipeline). Property-based testing with Hypothesis (overkill — pipeline outputs are deterministic, not random).
- **Rationale:** JSON golden cases are version-controllable, human-reviewable, language-agnostic, and loadable without Python. Offline execution uses `MockEmbeddingProvider` + `InMemoryVectorStore` so all 38 tests run in CI with no external dependencies. The `expected_outputs.json` cross-check ensures every golden case file has an expectation entry.
- **Risks:** Golden expectations must be updated when pipeline logic intentionally changes. Failing to update expectations on feature changes causes false CI failures. Mitigated by: per-case `motion_in` ranges (not single values) and `min_score`/`max_score` tolerances.
- **Validation:** 38 golden tests pass. 358 total tests (320 pre-existing + 38 new + 0 regression). Full CI passes offline. All 7 cases produce correct pipeline contract, motion, gaps, brief sections, and RAG invariants.
- **Status:** Implementado no Epic 17.

### Decision 026 - Scheduled Corpus Maintenance is Safe by Default

- **Context:** Source sync, freshness audit, Qdrant ingestion, RAG evals, and golden evals existed as separate manual steps. Running them manually made corpus maintenance error-prone, while automatic real ingestion or source promotion could publish bad corpus changes silently.
- **Decision:** Add a dedicated corpus maintenance workflow and local orchestrator with safe defaults: source sync dry-run enabled, freshness audit enabled, Qdrant ingest dry-run enabled, evals enabled, real ingestion disabled, source promotion disabled, collection recreation disabled, stale warnings non-blocking, expired sources blocking. Scheduled runs use only the safe path; real ingestion and promotion require explicit manual inputs.
- **Alternatives considered:** Put the sequence in CI (rejected because corpus maintenance is operational, not every PR validation), enable automatic ingestion on schedule (rejected because it can mutate Qdrant silently), use shell-only orchestration (rejected because Python gives structured summary reports and safer argument handling).
- **Rationale:** The workflow provides repeatable maintenance and artifacts while preserving human review for any corpus mutation. It keeps all source downloads allowlist-based and keeps Qdrant local to the runner.
- **Risks:** The new script has no dedicated unit tests because Epic 21 scope excludes `tests/`; mitigated by local safe execution, structured reports, and full repo quality gates. Real ingestion still depends on Docker/Qdrant availability when explicitly enabled.
- **Validation:** `scripts/run_corpus_maintenance.py` safe mode, `pytest`, `ruff check .`, `black --check .`, and `mypy src`.
- **Status:** Implementado no Epic 21.

---

## Decision 026 - CLI demo with argparse, no new dependencies

- **Context:** O projeto precisava de um modo simples de demonstrar o produto de ponta a ponta sem frontend. A pipeline, o briefing e o RAG já estavam prontos, mas não havia entry point unificado.
- **Decision:** Criar `scripts/run_startup_radar_demo.py` usando `argparse` (biblioteca padrão), sem Typer/Click ou qualquer dependência nova. A CLI é um orquestrador fino que reusa todas as funções existentes (`run_full_pipeline`, `build_action_brief`, `render_action_brief_markdown`, `evaluate_answer_quality`).
- **Alternatives considered:** Typer/Click (rejeitado para manter zero dependências novas), criar um endpoint FastAPI (fora do escopo — sem frontend), adicionar ao Makefile sem script (inviável para flags complexas).
- **Rationale:** `argparse` é o padrão já usado em todos os scripts do projeto (`ingest_nvidia_corpus.py`, `sync_nvidia_sources.py`, etc.). Zero dependência nova significa zero risco de conflito, zero tempo de instalação extra.
- **Risks:** CLI pode ficar frágil se a pipeline mudar a assinatura de `run_full_pipeline()`. Mitigado: os testes de integração detectam regressões.
- **Validation:** `make demo-cli`, `make demo-cli-offline`, `make demo-cli-rag` rodam sem erro. 6 testes de integração passam.
- **Status:** Implementado no Epic 24.

## Decision 026 — Minimal FastAPI Demo API (API Layer, Not Subprocess)

- **Context:** O CLI demo (Epic 24) demonstra o sistema localmente, mas stakeholders e integradores precisam de uma interface HTTP programática. O projeto já tinha FastAPI/Uvicorn declarados em `pyproject.toml` e um `src/main.py` mínimo com apenas `GET /health`.
- **Decision:** Criar `src/api/` com FastAPI, reaproveitando a lógica da CLI/pipeline via chamadas diretas (não subprocess). Endpoints mínimos (6) sem autenticação, sem frontend, sem deploy cloud. A API é local/dev apenas.
- **Alternatives considered:** Subprocess chamando o script CLI (rejeitado — overhead, perda de tipos, erros opacos), Typer/Click CLI → HTTP bridge (desnecessário com FastAPI já instalado), adicionar autenticação/rate-limit (fora de escopo — apenas demo local).
- **Rationale:** Chamar `run_full_pipeline()`, `build_action_brief()` e `evaluate_answer_quality()` diretamente é a abordagem mais segura, testável e de manutenção simples. FastAPI já estava declarado como dependência. `src/main.py` existente foi convertido para re-exportar o app do novo pacote.
- **Risks:** Pipeline síncrona pode bloquear por vários segundos (aceitável para demo local — sem async). Qdrant offline poderia crashar a API — mitigado com `QdrantConnectionError` capturado e fallback gracioso.
- **Validation:** `make api` sobe. `make api-test` passa. Swagger em `/docs` funciona. Nenhuma lógica central foi duplicada.
- **Status:** Implementado no Epic 25.

---

## Decision 029 - SQLite-first transactional product persistence

- **Context:** Epic 28 identified product persistence and a product resource API as the highest-priority gap. PostgreSQL was selected conceptually in Decision 003 and is scaffolded in Docker Compose, but the repository had no implemented relational schema, repositories, or migrations.
- **Decision:** Epic 29 uses SQLAlchemy with `PRODUCT_DB_URL` and defaults to `sqlite:///data/product/product.db`. SQLite stores transactional product entities. Qdrant remains limited to embeddings, chunks, corpus documents, and retrieval metadata. Models use portable SQLAlchemy types and constraints so PostgreSQL can replace SQLite later without changing repository/service interfaces.
- **Alternatives considered:** Require PostgreSQL immediately; store product state in Qdrant; keep file artifacts under `data/demo_runs`.
- **Rationale:** SQLite provides a real persistent product flow with minimal operational setup and isolated tests. Requiring PostgreSQL now would add deployment complexity before the product resource model is stable.
- **Risks:** SQLite has limited concurrent-write capacity and the build currently uses `create_all` rather than versioned migrations.
- **Validation:** Product database, repository, service, API, lifecycle, failure, health, and demo-independence tests.
- **Future path:** Add versioned migrations and validate the same SQLAlchemy models against PostgreSQL before multi-user deployment.
- **Status:** Implemented in Epic 29.

---

---

## Decision 030 — Versioned Schema Migrations with Alembic

- **Context:** Epic 29 used `Base.metadata.create_all()` for schema creation, which is not versioned, auditable, or safe for iterative schema changes. The product schema needed 2 new tables (ReviewDecision, ExportRecord) and a safe migration path.
- **Decision:** Adopt Alembic as the migration tool. The initial migration (`0001_create_all_product_entities.py`) creates all 10 product tables. `env.py` reads `PRODUCT_DB_URL` from the environment (or config override) and uses `render_as_batch=True` for SQLite compatibility.
- **Alternatives considered:** Keep `create_all()` (no versioning), use raw SQL migration scripts (no integration with SQLAlchemy), use SQLAlchemy's `Migrate` (less maintained).
- **Rationale:** Alembic is the standard migration tool for SQLAlchemy. It supports both SQLite (batch mode) and PostgreSQL from the same `env.py`. Auto-generation reduces manual migration writing.
- **Risks:** Auto-generated migrations may need manual review for column type changes. Batch mode may produce SQL that looks different from PostgreSQL but achieves the same result.
- **Validation:** `alembic upgrade head` and `alembic downgrade -1` tested with SQLite. PostgreSQL validation via skippable integration tests.
- **Status:** Implemented in Epic 30.

---

## Decision 031 — PostgreSQL Validation via Skippable Integration Tests

- **Context:** SQLite is the default local database. PostgreSQL must be validated as a production path without becoming a required dev dependency.
- **Decision:** PostgreSQL validation is done via tests marked `@pytest.mark.integration` that require `PRODUCT_DB_TEST_URL`. They do not run in CI (`pytest -m "not integration"`). Documentation in `docs/contracts/product_db_migrations.md` explains how to run manually.
- **Alternatives considered:** Make PostgreSQL required (blocked by local dev simplicity), run PG tests in CI with service containers (too early before production deployment), skip validation entirely (risk of silent incompatibility).
- **Rationale:** Skippable tests document the expected PG behavior without blocking local development. The same models, SQLAlchemy types, and migration script work for both databases.
- **Validation:** `test_postgres_migration.py` — alembic upgrade, JSON column roundtrip, repository smoke test.
- **Status:** Implemented in Epic 30.

---

## Decision 032 — ReviewDecision as Append-Only Audit Log

- **Context:** Human review is needed for startup qualification. The review must not alter the underlying pipeline scores.
- **Decision:** `ReviewDecision` is an append-only table. Multiple reviews per analysis run are preserved. The latest review (by `created_at`) is the current status. Reviews do not recalculate scores or delete pipeline outputs.
- **Alternatives considered:** Single review per run (loses audit trail), review updates a score field (mixes human judgment with pipeline determinism), review deletes evidence (violates auditability).
- **Rationale:** Append-only preserves full decision history. The latest review is available for opportunities ranking.
- **Status:** Implemented in Epic 30.

---

## Decision 033 — ExportRecord from ActionBriefRecord, Not Demo Artifacts

- **Context:** Exports must come from persisted product records, not from `data/demo_runs` loose files.
- **Decision:** `ExportRecord` is generated from a persisted `ActionBriefRecord`. The path is stored relative to `PRODUCT_DATA_DIR/exports/`. Content hash (SHA256) enables regeneration detection.
- **Alternatives considered:** Generate from pipeline output directly (adds complexity), generate from demo artifacts (violates product mode), store full content in DB (bloat).
- **Rationale:** ActionBriefRecord already contains the validated brief JSON and Markdown. Relative paths keep the database portable. Content hash enables idempotent regeneration.
- **Status:** Implemented in Epic 30.

---

## Decision 034 — Demo Artifacts Are Not Product Sources

- **Context:** Epics 29-30 implemented a complete product persistence layer. Legacy demo artifacts (data/demo_runs, demo API routes, demo CLI, demo UI) coexisted with the product flow, creating confusion about which path is primary.
- **Decision:** The product flow uses persisted product entities (startups, analysis runs, Action Brief records, reviews, exports) configured by `PRODUCT_DB_URL`. Demo artifacts are not sources for the product flow. Legacy demo code (CLI script, frontend, demo API routes) is preserved for backward-compatible smoke testing but is deprecated. Generated artifacts (data/demo_runs/latest, data/regression_reports, data/ingestion_reports) are deleted and gitignored.
- **Alternatives considered:** Keep demo as co-equal path (creates confusion), delete all demo code immediately (breaks integration tests), rewrite demo as product (out of scope).
- **Rationale:** Product persistence exists and is validated. Removing demo artifacts reduces complexity. Preserving legacy scripts avoids breaking existing workflows until product CLI/UI replacements exist.
- **Validation:** Product services never read `data/demo_runs` (regression test in `test_product_database.py`). Product API smoke tests pass. All core unit tests pass.
- **Status:** Implemented in Epic 31.

---

## Decision 035 — Claim Ledger Determinístico sem LLM Extraction (v1)

- **Context:** Epic 32 — Evidence & Claim Ledger. Claims precisam ser auditáveis e rastreáveis até suas evidências de origem. A pipeline produz registros estruturados (StartupEvidence, ScoreRecord, GapDiagnosisRecord, NvidiaMappingRecord) que contêm claims implícitas.
- **Decision:** A geração de claims na v1 é determinística: o ClaimLedgerService percorre registros persistidos e produz claims com mapping explícito de support level (confidence float → strong/medium/weak/unsupported). `evidence_refs` é armazenado como JSON column (não há tabela separada ClaimEvidenceLink). A idempotência é mantida via delete+regenerate de todas as claims de um AnalysisRun.
- **Alternatives considered:** LLM extraction de claims de texto livre (rejeitado — custo, não-determinismo, complexidade na v1). Tabela separada ClaimEvidenceLink (adiado para v2 — FK enforcement pesaria setup inicial). Update incremental (rejeitado — delete+regenerate é mais seguro e simples).
- **Rationale:** Geração determinística é testável, auditável e não depende de LLM. JSON column permite schema flexível sem migration extra. Delete+regenerate garante que claims refletem sempre o estado atual dos registros.
- **Risks:** JSON column sem FK enforcement permite dados inconsistentes via código mal escrito. Delete+regenerate causa janela de vazio (aceitável — operação rápida em um único AnalysisRun). Claims de uncertainty podem ser prolixas se muitas evidencias estiverem faltando.
- **Validation:** 12 testes unitários (ClaimRepository), 9 testes unitários (ClaimLedgerService), 9 testes de integração (API). Cobertura de evidencia calculada via confidence_to_float mapping.
- **Status:** Implementado no Epic 32.

## Decision 036 — Activation Playbook Source em YAML (não DB-first)

- **Context:** Epic 33 — NVIDIA Activation Playbook Library. Precisa-se de uma fonte de verdade para 10 playbooks de ativação. Playbooks mudam com frequência (novas tecnologias NVIDIA, motions, regras de matching).
- **Decision:** Playbook source é YAML em `src/config/playbooks/nvidia_activation_playbooks.yaml`. Loader com validação Pydantic carrega e valida os playbooks em runtime. Não há persistência DB-first dos playbooks — apenas das recomendações geradas (`ActivationRecommendationRecord`).
- **Alternatives considered:** DB-first com tabela de playbooks (rejeitado — playbooks mudam via deploy/CI, não via UI; YAML é mais simples de versionar e revisar). SQLite seed data (rejeitado — mistura schema com dados). JSON (rejeitado — YAML é mais legível para humanos).
- **Rationale:** YAML permite versionamento git, diff claro em PRs, sem migration DB para cada alteração de playbook. PyYAML já é dependência do projeto (usado em outros lugares). Validação no loader garante que YAML malformado não passa.
- **Risks:** Mudança de playbook requer deploy (não é hot-reload). YAML corrompido quebra o endpoint de listagem (log + fallback silencioso implementado).
- **Validation:** 13 testes unitários no loader cobrindo YAML válido, vazio, duplicado, campos obrigatórios ausentes, motions inválidos, complexities inválidas.
- **Status:** Implementado no Epic 33.

## Decision 037 — Matching Determinístico v1 (sem LLM)

- **Context:** Playbooks precisam fazer match com gaps detectados para gerar recomendações. Opção de usar LLM ou embedding similarity para matching mais flexível.
- **Decision:** Matching v1 é puramente determinístico: um playbook matcha se pelo menos um `target_gap_type` está presente entre os gaps detectados (detected=True) do analysis_run. Gaps não detectados são ignorados.
- **Alternatives considered:** LLM matching (rejeitado — custo, latência, não-determinismo na v1). Embedding similarity (rejeitado — complexidade, necessidade de sentence-transformers em runtime, overkill para 10 playbooks).
- **Rationale:** Determinístico é testável, auditável e não depende de LLM. 10 playbooks × ~15 gap types = escopo pequeno o suficiente para matching exato.
- **Risks:** Matching determinístico não captura gaps semanticamente similares (ex: "voice_need" vs "audio_processing"). Adiado para v2 com LLM/embedding fallback.
- **Validation:** 9 testes unitários cobrindo matching por gap, sem gap, gap não detectado, confidence boost/penalty, prioridade, idempotência.
- **Status:** Implementado no Epic 33.

## Decision 038 — Confidence com Fórmula Fixa (sem aprendizado)

- **Context:** Recomendações precisam de confidence score para priorização. Opção de usar ML ou feedback loop para calibrar confidence.
- **Decision:** Confidence calculado por fórmula fixa: avg(gap_confidences) + mapping_boost + claim_boost - coverage_penalty - unsupported_penalty - degraded_penalty; clamped [0.0, 1.0]. Conversão para string: >= 0.7 high, >= 0.4 medium, < 0.4 low.
- **Alternatives considered:** ML model (rejeitado — sem dados históricos de feedback na v1). Regressão logística (rejeitado — complexidade desnecessária). Threshold ajustável por playbook (adiado — fórmula única é suficiente para v1).
- **Rationale:** Fórmula fixa é transparente, testável e não depende de dados históricos. Penalties e boosts são baseados em heurísticas de domínio (mapping NVIDIA aumenta confiança, claims não suportadas diminuem).
- **Risks:** Fórmula pode não refletir maturidade real da startup (adiado — feedback loop v2). Penalties podem ser muito agressivos para startups early-stage (aceitável — é conservador por design).
- **Validation:** Testes unitários cobrem boost com mapping, penalty com unsupported claims, prioridade ordenada.
- **Status:** Implementado no Epic 33.

## Decision 040 — Dossier Versioned and Deterministic (no LLM)

- **Context:** Epic 34 — Startup Activation Dossier. Precisa-se de um artifact consolidado que projete todos os registros persistidos de um AnalysisRun (scores, gaps, mappings, activation, claims, reviews, readiness) em um JSON + Markdown versionado.
- **Decision:** Dossier é deterministico (sem LLM), idempotente (POST retorna existente por default), versionado (versão 1..N por analysis_run), e honesto sobre dados ausentes (missing → uncertainty explícita). Readiness checks viram risks não-bloqueantes.
- **Alternatives considered:** LLM-summarized dossier (rejeitado — não-determinismo, custo, latência). Generated-on-read (rejeitado — sem versionamento, sem snapshot). Always-regenerate (rejeitado — sem idempotência, sem preservação de histórico).
- **Rationale:** Determinismo garante auditabilidade e testabilidade. Versionamento permite rastrear mudanças ao longo do tempo. Honestidade sobre missing data é consistente com evidence-first design do projeto.
- **Risks:** Dossier pode ficar grande se analysis_run tiver muitos registros (aceitável — JSON + Markdown armazenados em colunas text). idempotência pode mascarar dados desatualizados — mitigado por force_new_version explícito.
- **Validation:** Repository testa CRUD e versionamento. Service testa build de minimo a completo, incertezas, risks, review conditions, markdown. API testa idempotência, force new version, 404, summary injection.
- **Status:** Implementado no Epic 34.

---

## Decision 039 — Idempotência via replace_recommendations_for_analysis_run

- **Context:** Geração de recomendações pode ser chamada múltiplas vezes (manual via POST + automática no lifecycle). Precisa ser idempotente.
- **Decision:** `ActivationRecommendationRepository.replace_recommendations_for_analysis_run` executa delete de todas as recomendações existentes do analysis_run + bulk create das novas. Tudo na mesma transação.
- **Alternatives considered:** Upsert por playbook_id (rejeitado — playbooks podem ser removidos, upsert deixaria órfãos). Soft-delete + insert (rejeitado — complexidade desnecessária).
- **Rationale:** Delete+regenerate é o padrão já usado no Claim Ledger (Epic 32). É simples, correto e testado. Transação única garante atomicidade.
- **Risks:** Janela de vazio entre delete e insert (aceitável — operação rápida em um único analysis_run). Perda de revisões anteriores (aceitável — v1 não tem histórico).
- **Validation:** Teste de idempotência na integração: duas chamadas POST geram mesmo número de recomendações.
- **Status:** Implementado no Epic 33.

---

## Decision 041 — Structured Output Reliability Layer (Epic 36)

- **Context:** Dossier JSON validation was a simple try/except with no retry, no repair, no structured failure tracking, no quality metrics. Multiple modules parse JSON from various sources with inconsistent error handling.
- **Decision:** Create a centralized `structured_outputs.py` module with: `parse_json_output()` (safe parse with error capture), `repair_json_if_safe()` (deterministic structural repair), `validate_output()` (Pydantic validation with `ValidationError` → structured details), `run_validation_with_repair()` (retry up to 1 with repair), `build_structured_output_result()` (unified result with degraded states), `readiness_check_payload_from_result()`, `quality_metrics_from_results()`. Add 5 degraded state codes to degraded.py, 6 quality metric constants, and an evaluator in quality/evaluators/. Integration: Activation Dossier gets `DossierJsonSchema` + `_validate_dossier_json()` + readiness check on failure.
- **Alternatives considered:** Keep per-module try/except (rejected — inconsistent, no metrics). Use pydantic.TypeAdapter everywhere (good but not enough — needs retry/repair/readiness). Use instructor for all outputs (rejected — optional dependency, adds latency, too early).
- **Rationale:** Centralization ensures consistent failure handling across all structured output consumers. Retry with repair handles the most common failure patterns (trailing commas, truncated JSON). Readiness checks make failures observable in the product dashboard. Quality metrics enable regression detection over time.
- **Risks:** Repair is conservative by design — complex structural issues are not fixed. Retry max 1 prevents infinite loops. Instructor trial is optional and gated behind `[llm-judge]` extra.
- **Validation:** 34 tests covering parse, repair, validate, retry, metrics, readiness payload, and dossier integration. 4 integration tests for dossier validation + quality metrics.
- **Status:** Implementado no Epic 36.

## Decision 042 — Capability & Configuration Registry (Epic 36.1)

- **Context:** The product has no central registry for what features exist, which are enabled/configured, what env vars are required, what optional deps are missing, or whether the product is ready to use. Users and developers had to read `.env.example` and source code to understand configuration requirements.
- **Decision:** Create a capability registry (25+ capabilities across 13 categories) and a configuration registry (17+ env vars) in `src/services/product/`, plus a `ProductReadinessService` that aggregates status from both registries and produces a readiness report. Expose via 4 API endpoints: `GET /product/capabilities`, `/product/configuration`, `/product/setup-checklist`, `/product/readiness`. Each capability has `id`, `name`, `description`, `category`, `required`, `enabled_by_default`, `status`, `required_env_vars`, `optional_env_vars`, `required_extras`, `required_services`, `health_check_key`, `setup_instructions`, `failure_mode`, `user_visible`, `documentation_ref`. Status is computed at call time from environment + extras.
- **Alternatives considered:** Static YAML/JSON config file (rejected — cannot compute status dynamically from env). DB-backed registry (rejected — overkill before first product user). Feature flags library like `flipper` or `waffle` (rejected — avoid new dependency, Python env-driven is sufficient). Merge into health endpoints (rejected — different granularity: health = binary, readiness = diagnostic).
- **Rationale:** No-DB design keeps it simple — env vars + importlib are sufficient for v1. Per-call computation guarantees status is always current. Required vs optional distinction lets users see what's blocking without frustration. API endpoints give both CLI (curl) and UI consumers the same data.
- **Risks:** Environment-driven status means config changes require restart. `not_configured` for optional features may confuse users — mitigated by clear `status_reason` and `user_messages`. New capabilities must be registered manually (no auto-discovery).
- **Validation:** 6 capability registry tests (required/optional/extras caps), 9 config registry tests (items, secrets, extras), 10 readiness service tests (capabilities, config, report, optional features), 9 integration tests (4 endpoints, field presence, blocking behavior).
- **Status:** Implementado no Epic 36.1.

---

## Decision 043 — Product UI Routing & Stack (Epic 37)

- **Context:** The product needs a first usable web UI that consumes the Product API (readiness, capabilities, startups, analysis, dossier, opportunities, review/quality). The existing demo UI was a standalone proof-of-concept with no connection to the Product backend.
- **Decision:** Build the Product UI using React 19 + Vite 7 + TypeScript 5.9 (confirmed by user, no new dependencies). Use state-based routing in `App.tsx` (no react-router-dom). Use native `fetch` for API calls (no TanStack Query). No mock as main flow — UI consumes real Product API. Edit startup limited to name/sector/website (not a CRM). E2E tests (`make ui-e2e-product`) kept separate from `make validate`. Demo UI preserved but deprecated.
- **Alternatives considered:** react-router-dom (rejected — escopo pequeno demais para justificar dependência extra). TanStack Query (rejected — não estava no projeto, fetch nativo suficiente). Mock-first development (rejected — user explicitly required real API consumption).
- **Rationale:** State-based routing is simpler for 7 views; no dependency cost. Native fetch keeps the bundle minimal. Real API first avoids maintaining parallel mock logic. Minimal startup editing aligns with "not a CRM" constraint. Separate E2E avoids blocking `make validate` with browser/driver requirements.
- **Risks:** State-based routing may need refactoring if views exceed ~15. No retry/caching layer in fetch means UI handles all error states explicitly.
- **Validation:** `npm run build` passes (tsc + vite build, 0 erros, 0 warnings). Playwright smoke tests at `tests/e2e/test_product_ui.spec.ts` (readiness, capabilities). Alvo `make ui-e2e-product` separado do validate.
- **Status:** Implementado no Epic 37.

---

---

## Decision 044 — Product Golden Path Acceptance (Epic 38)

- **Context:** The product has backend, API, quality layer, dossier, playbooks, claims, and UI. There was no end-to-end acceptance test proving the full flow works. Individual integration tests existed but no unified Product Golden Path.
- **Decision:** Create a Product Golden Path acceptance test suite at `tests/acceptance/` using `@pytest.mark.acceptance`. The golden path validates 17 sequential steps: readiness → capabilities → startup CRUD → analysis run → claims → activation recommendations → dossier → quality → opportunities → export. A fixture at `tests/fixtures/product_golden_path/` provides a controlled input. A separate guard (`test_no_demo_dependency.py`) ensures no step reads `data/demo_runs`. Acceptance tests run via `make acceptance` (separate from `make validate`).
- **Alternatives considered:** Extend existing `integration` tests (rejected — mixing integration with acceptance dilutes purpose). Add Playwright-only acceptance (rejected — too slow, couples to UI). Add to `make validate` (rejected — acceptance should not block fast local dev).
- **Rationale:** FastAPI TestClient acceptance tests are fast (~5 seconds), deterministic, and test real product API logic. The `acceptance` marker keeps them separate from unit and integration tests. The golden fixture is small, explicit, and version-controlled.
- **Risks:** Acceptance tests may duplicate existing integration test logic. Mitigated: acceptance tests focus on the *full flow sequence*, integration tests on individual endpoint edge cases.
- **Validation:** `make acceptance` passes. `make prepare-release` runs validate + acceptance + ui-build. `make validate` does not include acceptance tests.
- **Status:** Implementado no Epic 38.

---

## Decision 045 — Validate Targets Restructuring (Epic 39)

- **Context:** `make validate` was a monolithic target that ran lint + format-check + typecheck + all tests. There was no fast path for quick validation, no filtered test targets, and no distinction between unit/integration/acceptance/e2e. CI ran `pytest` without marker filtering.
- **Decision:** Split `make validate` into hierarchical targets. `validate-fast` = lint + format-check + typecheck + unit tests (excludes integration, acceptance, e2e, slow, optional, external_service). `validate-full` = validate-fast + docs validation + frontend lint/build. `prepare-release` = validate-full + acceptance. Added pytest markers: `unit`, `integration`, `acceptance`, `e2e`, `slow`, `optional`, `external_service`.
- **Alternatives considered:** Keep `make validate` monolithic (rejected — too slow for iterative dev). Remove slow tests from default (rejected — CI should still catch them). No markers (rejected — no isolation).
- **Rationale:** Hierarchical targets match the speed-to-confidence tradeoff. Fast path (<60s) for local iteration, full path for pre-release. Markers let developers run exactly what they need.
- **Risks:** validate-fast may miss integration regressions — mitigated by CI running broader tests. New markers require developer discipline to tag tests correctly.
- **Validation:** `make lint`, `make format-check`, `make typecheck`, `make validate-fast` all pass. 773 total tests collected, validate-fast runs only unit tests.
- **Status:** Implementado no Epic 39.

---

---

## Decision 046 — Startup Discovery Engine (Epic 40)

- **Context:** The product had no upstream discovery layer. Startups had to be created manually via the API with no automated candidate intake, signal detection, duplicate prevention, or multi-source ingestion.
- **Decision:** Build a multi-source startup discovery engine with: source registry (JSON), signal detection (keyword-based, no LLM), dedup (normalized_name + domain), DiscoveryRun lifecycle (queued/running/completed/degraded/failed), Candidate management, URL list importer (httpx + BeautifulSoup), and promotion to Startup records with evidence migration.
- **Alternatives considered:** Scraping-first approach with broad crawler (rejected — "no scraping agressivo" rule). Google Custom Search / SerpAPI (rejected — paid, not allowed by rules). LLM-based classification (rejected — no LLM dependency for discovery). Single monolithic importer (rejected — modularity requirement).
- **Rationale:** Source-agnostic JSON registry allows adding new sources without code changes. Keyword-based signal detection works offline with zero API cost. Dedup by normalized_name + domain prevents duplicate Startups from any source. DiscoveryRun lifecycle with degraded states ensures partial failures don't block progress. Promotion-to-Startup creates evidence records from detected signals.
- **Risks:** Signal detection is keyword-only and will miss context-dependent AI usage. No broad crawling means discovery depends on user-provided seeds and curated source lists. URL list importer may hit rate limits or blocked domains.
- **Validation:** 55 total tests (41 unit + 14 integration) covering signals, dedup, repository CRUD, and API endpoints. All 57 existing tests continue to pass.
- **Status:** Implementado no Epic 40.

---

---

## Decision 047 — LangGraph Orchestration Layer (Epic 41)

- **Context:** The product needed a stateful orchestration layer for the 11-step product analysis workflow (load startup, collect evidence, validate, diagnose gaps, retrieve NVIDIA context, map technologies, generate claims, match playbooks, generate dossier, run quality, summarize readiness). Existing services were independent with no coordination layer.
- **Decision:** Build a sequential workflow runner with LangGraph as an optional extra (`[agent-orchestration]`). The runner executes nodes deterministically with per-node retry (max 1), persists state to `WorkflowRun`/`WorkflowNodeRun` models, and provides a full REST API. LangGraph is not required for operation — the fallback runner provides identical deterministic behavior.
- **Alternatives considered:** LangGraph as a core dependency (rejected — violates FPB-029 which classifies multi-agent orchestration as P3). Pure LangGraph with no fallback (rejected — LangGraph may not be needed). Rewriting existing services as nodes (rejected — "serviços existentes não devem ser reescritos; nodes apenas wrappers").
- **Rationale:** Optional LangGraph keeps core installation lean. Nodes wrap existing services via `@_register` decorator without modifying them. Retry policy (max 1, non-retryable for LookupError/ValueError/TypeError/AssertionError) avoids infinite loops. Sequential execution guarantees deterministic output. `_dump_state` helper strips non-serializable `_session` key before JSON serialization.
- **Risks:** Synchronous execution blocks the request thread for the full 11-node workflow. LangGraph extra may drift from the fallback runner if not kept in sync. Node implementations duplicate session management boilerplate.
- **Validation:** 36 tests (24 unit + 12 integration) covering state, repository, runner, and API. `ruff`, `black`, `mypy` (1 pre-existing error). All pre-existing tests continue to pass.
- **Status:** Implementado no Epic 41.

---

## Decision 048 — Hybrid RAG: BM25 Local, NoOp Reranker, No Qdrant Sparse

- **Context:** Epic 42 required adding sparse retrieval, deterministic query planning, fusion, reranking, and citation packaging to the RAG module. Options included: using Qdrant sparse vectors, adding external reranker APIs, or building local pure-Python alternatives.
- **Decision:** Sparse retrieval uses local BM25 over the existing ChunkIndex (pure Python, no Qdrant sparse vectors — avoids reingestion). Reranking uses NoOpReranker as default with OptionalCrossEncoderReranker (lazy-loaded via sentence-transformers, an existing optional dep) as an opt-in upgrade. Fusion defaults to RRF with configurable dense/sparse weights. Query planner is deterministic string/keyword logic — no LLM. Citation packaging is a pure projection of RagEvidenceChunk — no new DB models.
- **Alternatives considered:** Qdrant sparse vectors (rejected — requires reingestion of the entire collection). Cohere/API reranker (rejected — paid, adds external dependency). LLM query planner (rejected — non-deterministic, no need for v1). Ragas integration (noted as optional future step).
- **Rationale:** Local BM25 avoids any reingestion of the existing Qdrant collection. NoOpReranker makes the non-reranked path zero-cost and always available. CrossEncoder loads on first use — no startup penalty. Deterministic query planner keeps retrieval testable and reproducible.
- **Risks:** BM25 over lexical-only index may not add much value over existing keyword retrieval. Mitigated: configurable fusion weights let users tune the hybrid blend. CrossEncoder model download (~2GB) may fail in constrained environments. Mitigated: silent fallback to NoOp with log warning.
- **Validation:** 31 unit tests covering all modules. All 775 pre-existing tests unchanged.
- **Status:** Implementado no Epic 42.

---

ADRs (Architectural Decision Records) individuais estão em `docs/adr/`. Cada ADR cobre uma decisão específica. Decisões neste arquivo são consolidadas para visão geral.
