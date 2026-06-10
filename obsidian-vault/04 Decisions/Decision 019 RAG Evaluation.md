# Decision 019 — RAG Evaluation offline com golden queries e quality gates

**Status:** Implementado no Epic 12
**Data:** 2026-06-09

## Contexto

Product RAG (Epic 11) foi implementado sem camada de avaliação. Não era possível medir se o retrieval retornava o contexto correto para cada gap/tecnologia.

## Decisão

Criar `src/evaluation/rag_eval.py` + `rag_eval_schemas.py` com:
- 7 métricas determinísticas (hit_at_k, source/product coverage, irrelevant/missing count, top_1_match, precision)
- 6 quality gates
- 16 golden queries em `examples/rag_eval/golden_queries.json`

Avaliação reusa ChunkIndex sem modificá-lo. Módulo independente que não altera pipeline, scoring, diagnosis, recommendation ou briefing.

## Alternativas consideradas

- **LLM judge:** Rejeitado por não-determinismo
- **Qdrant + reranking:** Fora de escopo
- **Integrar no pipeline:** Rejeitado para preservar separação
- **Avaliação manual:** Não reproduzível

## Riscos

- Golden queries podem desatualizar se corpus mudar
- Métricas lexicais não detectam degradação semântica
- Quality gates podem ser muito rigorosos/laxos

## Validação

- 20 testes unitários
- 16 golden queries passam com corpus atual
- Quality gates falham com índice vazio ou sem proveniência
