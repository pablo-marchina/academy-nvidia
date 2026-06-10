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
- Reranking deterministico usa pesos fixos (RerankingConfig) — pode nao ser otimo para todos os gaps/tecnologias
- Context packing tem limites configurados (per-tech=2, per-gap=3, global=5) — pode descartar contextos relevantes em casos de borda
- Sem cross-encoder reranking (backlog)
- Vector store e in-memory (sem persistencia entre sessoes — Qdrant-ready via QdrantStore adapter opcional no Epic 15)
- Recommendation Engine implementado e integrado ao pipeline (Epic 9.1)
- RAG pipeline integrado como Step 11 opcional — sem suporte a contextos multi-turno ou consultas interativas
- QdrantStore nao faz fallback automatico para in-memory em caso de erro de conexao (caller deve capturar QdrantConnectionError)
- Script de ingestao (Epic 18) usa MockEmbeddingProvider por padrao se sentence-transformers nao estiver instalado — embeddings reais requerem sentence-transformers

- Scores dependem da qualidade e cobertura das evidencias publicas disponiveis
- Confianca das evidencias e atribuida heuristicamente, nao por modelo aprendido
- Sistema nao prova uso interno real de AI — apenas estrutura sinais publicos
- `recommended_motion` e sugestao preliminar baseada em regras deterministicas

## Testes

- Zero testes de integracao (9 skippable no Epic 15)
- 38 golden evals automatizados (Epic 17) — cobrem pipeline completa offline
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
