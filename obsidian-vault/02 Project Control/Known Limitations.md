# Known Limitations

*Ultima revisao: Junho 2026*

## Pipeline

- Pipeline usa heuristicas deterministicas, nao LLM, para scoring e diagnostico
- Scraping coleta de uma unica URL publica — sem crawling em escala
- Gap Diagnosis existe mas nao esta integrado ao pipeline
- NVIDIA Mapping existe mas nao esta integrado ao pipeline

## RAG e Recomendacao

- NVIDIA RAG nao implementado (playbooks estaticos ou mocked)
- Recommendation Engine nao implementado
- Suggested Technical Experiment nao implementado

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
- Obsidian vault tem estrutura mas sem conteudo populado
