# Project Context — NVIDIA Startup AI Radar

## Visão do Produto
Plataforma multiagente que descobre startups brasileiras AI-native, coleta evidências públicas, estrutura dados, calcula scores quantitativos de maturidade AI-native e fit NVIDIA, usa RAG para gerar recomendações técnicas com fundamentação e produz briefings acionáveis para o programa NVIDIA Inception.

## Objetivo Final
Transformar o case/protótipo atual em um produto real, configurável, testado e pronto para uso. O produto deve rodar de ponta a ponta com configuração obrigatória antes da execução, sem demos, sem mocks, sem fallbacks silenciosos.

## Princípios Não Negociáveis
- Produto final **não pode ser demo** — toda execução deve ser real.
- **Configuração obrigatória** antes do primeiro uso (`config.toml` ou env vars validados).
- **PostgreSQL** é o banco relacional de produção.
- **Qdrant** é obrigatório para RAG em produção.
- **RAG** é obrigatório para qualquer recomendação NVIDIA.
- **LangGraph** orquestra o workflow principal.
- **Scraping** amplo, governado, rastreável, com rate limit explícito.
- Decisões **quantitativas** sempre que possível.
- Todo score expõe: features, pesos, confiança e incerteza.
- Toda recomendação tem: evidência, suporte RAG, confidence score, business impact, implementation complexity e next best action.
- Todo módulo implementado deve ser **usado, removido ou marcado como experimental**.
- **Sem fallback silencioso** em produção — toda falha deve ser explícita.
- **Sem segredos commitados** — .env, .venv, node_modules, caches, bancos locais no `.gitignore`.

## Arquitetura Esperada
```
[Scraping Layer] → [Entity Extraction] → [Enrichment Pipeline]
                                            ↓
                                    [Vector Store (Qdrant)]
                                            ↓
                              [RAG Recommender (LangGraph)]
                                            ↓
                                [Action Brief Generator]
                                            ↓
                                  [PostgreSQL (persistence)]
```

## Módulos Esperados
1. **Scraper** — coleta governada com rate limit e rastreabilidade
2. **Entity Extractor** — extração de entidades (startups, tech stack, funding)
3. **Enricher** — busca ativa por evidências complementares
4. **Scorer** — cálculo quantitativo de maturidade AI-native e fit NVIDIA
5. **RAG Engine** — retrieval augmented generation sobre Qdrant
6. **Recommender** — geração de recomendações NVIDIA com LangGraph
7. **Brief Generator** — produção de Action Brief estruturado
8. **Config/CLI** — configuração obrigatória e interface de linha de comando

## Critérios de Qualidade
- Testes automatizados (pytest) para todo módulo.
- Cobertura mínima de 70% no core.
- Validação de schemas Pydantic em toda borda do sistema.
- Rastreabilidade: toda evidência tem URL e timestamp.
- Auditabilidade: toda execução gera log estruturado.
- Integração contínua validada antes de cada commit.

## Como Agentes de IA Devem Trabalhar Neste Repositório
1. **Sempre comece lendo** `.ai/project_context.md` e `AGENTS.md` para entender visão, regras e workflow.
2. **Nunca pule o planejamento** — tarefas não triviais exigem plano salvo em `docs/plans/`.
3. **Respeite contratos** — leia `docs/contracts/` antes de alterar módulos.
4. **Escopo pequeno** — entregue o menor incremento útil a cada iteração.
5. **Valide antes de concluir** — rode `make validate` ou `scripts/validate.sh`.
6. **Nunca invente dados** — toda afirmação sobre startup precisa de fonte.
7. **Separe fato, inferência e hipótese** nos outputs.
8. **Registre decisões técnicas** em `DECISIONS.md`.
9. **Atualize documentação** (README, ROADMAP, EVALS, ERROR_LOG, Obsidian).
10. **Não mexa em frontend** antes da pipeline principal funcionar.
