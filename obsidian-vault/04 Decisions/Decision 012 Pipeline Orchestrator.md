---
type: decision
date: 2026-06
area: architecture
status: implemented
---

# Decision 012 — Pipeline Orchestrator como integrador deterministico

## Contexto
Modulos de scoring implementados como funcoes independentes. Necessario orquestrador que as chame na ordem correta e consolide resultados.

## Decisao
Criar `src/pipeline/run_pipeline.py` com `run_full_pipeline()` de 7 steps deterministicos.

## Alternativas consideradas
- LangGraph graph (complexidade prematura)
- Script ad hoc (sem rastreabilidade)
- Cada modulo chamado manualmente (erro humano)

## Consequencias
- Pipeline testavel e rastreavel
- Substituivel por LangGraph no futuro sem mudar contratos
- 5 testes unitarios de integracao

## Links
- [[../03 Research/Epic 7.1 Pipeline]]
- [DECISIONS.md](../../DECISIONS.md)
