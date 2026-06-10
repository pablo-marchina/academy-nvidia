# Known Limitations

*Ultima revisao: Junho 2026*

## Pipeline

- Pipeline usa heuristicas deterministicas, nao LLM, para scoring e diagnostico
- Scraping coleta de uma unica URL publica — sem crawling em escala
- Gap Diagnosis existe mas nao esta integrado ao pipeline
- NVIDIA Mapping existe mas nao esta integrado ao pipeline

## RAG e Recomendacao

- Product RAG Epic 13: semantic/hybrid retrieval usa MockEmbeddingProvider nos testes (nao captura relacoes semanticas reais)
- SentenceTransformerProvider requer sentence-transformers (~500MB) — nao instalado por padrao
- Sem cross-encoder reranking (deferred para backlog)
- Vector store e in-memory (sem persistencia entre sessoes — Qdrant-ready)
- Recommendation Engine implementado (Epic 8) mas nao integrado ao pipeline

## Qualidade

- Scores dependem da qualidade e cobertura das evidencias publicas disponiveis
- Confianca das evidencias e atribuida heuristicamente, nao por modelo aprendido
- Sistema nao prova uso interno real de AI — apenas estrutura sinais publicos
- `recommended_motion` e sugestao preliminar baseada em regras deterministicas

## Testes

- Zero testes de integracao
- Zero evals automatizados
- `config/settings.py` sem testes

## Infraestrutura

- Sem human-in-the-loop implementado
- Sem Docker Compose
- Sem banco de dados conectado
- Sem CI/CD

## Documentacao

- Scoring docs incompletas (inception fit, production readiness, composite ranking sem docs individuais)
- Obsidian vault tem estrutura mas sem conteudo populado (parcialmente resolvido no Epic 7.2)

## Workspace de Desenvolvimento

- Developer RAG implementado apenas como fundacao documental — sem vector DB
- Prompts de workflow criados no Epic 7.2 mas ainda nao testados em uso real
- Plan artifacts obrigatorios a partir do Epic 7.2 — epicos anteriores nao tem planos versionados
- Contratos de desenvolvimento criados no Epic 7.2 — precisam ser mantidos atualizados com o codigo
