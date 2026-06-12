> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Epic 14 — RAG Reranking + Context Packing

**Data**: 2026-06-09
**Status**: Aprovado e implementado

## Objetivo

Adicionar reranking determinístico e context packing para selecionar, ordenar e compactar os contextos RAG usados no Action Brief.

## Arquitetura

```
src/rag/
├── reranking.py                # rerank_contexts() + RerankingConfig
├── context_packing.py          # pack_contexts() + PackingResult
├── schemas.py                  # + RerankingConfig, PackedContext, DroppedContext, PackingResult, SupportingNvidiaContext
└── retrieval.py                # inalterado (lexical fallback mantido)

src/evaluation/
├── rag_eval_schemas.py         # + RetrievalMode.HYBRID_RERANKED, HYBRID_RERANKED_PACKED; +8 métricas
└── rag_eval.py                 # run_mode_eval suporta reranking/packing; 5-mode comparison

src/briefing/
├── schemas.py                  # + packed_rag_contexts, supporting_nvidia_context, dropped_contexts_debug
├── action_brief.py             # build_action_brief() aceita packing_result opcional
└── markdown_renderer.py        # renderiza Supporting NVIDIA Context
```

## Decisões

| Decisão | Escolha | Justificativa |
|---------|---------|---------------|
| Reranking | Score composto (retrieval + gap + tech + provenance) | Determinístico, sem LLM, sem chamadas externas |
| Context packing | Dedup + limites por gap/tech + global | Reduz ruído sem perder cobertura |
| Modo de avaliação | 5 modos (lexical, semantic, hybrid, reranked, packed) | Cobertura completa da pipeline |
| Brief integration | Campo opcional, default vazio | Brief funciona sem RAG |

