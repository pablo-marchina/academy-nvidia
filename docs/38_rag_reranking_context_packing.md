# Documento 38 — Reranking Determinístico e Context Packing para RAG

**Data:** 2026-06-09
**Épico:** 14 — Reranking e Context Packing Determinísticos
**Status:** Implementado e validado

## Objetivo

Adicionar reranking determinístico (sem LLM) e context packing ao pipeline de RAG do produto, garantindo que o `ActionBrief` receba contextos NVIDIA limpos, organizados e relevantes.

## O que foi implementado

### 1. `src/rag/reranking.py` — Deterministic Reranking

Função `rerank_contexts(contexts, query, config)` que produz um score composto:

```
rerank_score = relevance × 0.3
             + gap_match × 0.3      # se o gap_type do query bate
             + tech_match × 0.2     # se a tecnologia do query aparece no product/content
             - provenance_penalty   # -0.5 se sem source_id ou url
             - duplicate_penalty    # -0.3 para segunda+ ocorrência
             - irrelevant_penalty   # -0.2 se gap não bate
             + known_source_boost   # +0.1 se source_id existe
```

- Score clamped a [0, 1]
- Configurável via `RerankingConfig`
- Determinístico: sem chamadas externas, sem LLM

### 2. `src/rag/context_packing.py` — Context Packing

Função `pack_contexts(contexts, query, config)`:

1. **Dedup**: remove chunks com mesmo `chunk_id`
2. **Classifica**: identifica `matched_gap` e `matched_technology` para cada chunk
3. **Agrupa e limita**: por gap → tecnologia, aplica `max_per_technology` (2), `max_per_gap` (3), `max_total` (5)
4. **Ordena**: gap_match > tech_match > score descendente
5. **Métricas**: provenance_coverage, gap_coverage, technology_coverage, context_budget_used, noise_reduction_score

Função `build_supporting_contexts(packing)` agrupa `PackedContext` por (gap, tech) para consumo pelo Action Brief.

### 3. Schemas (Epic 14)

- `RerankingConfig` — pesos do reranking
- `PackedContext` — `RetrievedContext` + `rerank_score`, `matched_gap`, `matched_technology`
- `DroppedContext` — `chunk_id`, `reason`, `rerank_score`
- `PackingConfig` — `max_total`, `max_per_technology`, `max_per_gap`
- `PackingResult` — `packed`, `dropped`, métricas
- `SupportingNvidiaContext` — agrupamento para Action Brief

### 4. Avaliação (Epic 14)

- `rag_eval_schemas.py`: 2 novos modos `HYBRID_RERANKED` e `HYBRID_RERANKED_PACKED`; 8 novos campos em `RagRetrievalMetrics`; `RagEvalComparison` agora tem 5 modos
- `rag_eval.py`: `run_mode_eval()` e `run_comparison_eval()` suportam todos os 5 modos; detecção de regressão cobre 4 modos posteriores

### 5. Action Brief

- `schemas.py`: `packed_rag_contexts`, `supporting_nvidia_context`, `dropped_contexts_debug` (opcionais)
- `action_brief.py`: `build_action_brief()` aceita `packing_result: PackingResult | None` (default None = RAG opcional); injeta seção "Supporting NVIDIA Context"
- `markdown_renderer.py`: renderiza a seção de contexto NVIDIA com score e proveniência

## Testes

| Arquivo | Testes | Cobre |
|---------|--------|-------|
| `tests/unit/test_rag_reranking.py` | 9 | gap/tech boost, provenance/duplicate/irrelevant penalties, empty, config, score range, order |
| `tests/unit/test_context_packing.py` | 13 | dedup, per-tech/per-gap/global limits, provenance, empty, dropped reasons, metrics, build_supporting |
| `tests/unit/test_rag_eval_reranking.py` | 11 | 5 modos, packed metrics, regression detection, backward compat |
| `tests/unit/test_action_brief_rag_context.py` | 5 | RAG-optional, context injection, empty default, motion unchanged |

Total: **38 novos testes**, 8 alterados. 276 testes no total, todos passando.

## Validação

- `pytest`: 276 passed
- `ruff check .`: apenas erros preexistentes (UP042 em schemas)
- `black --check .`: 95 files left unchanged
- `mypy src/`: Success: no issues found

## Decisões Arquiteturais

- **Sem LLM no reranking**: custo zero, determinístico, auditável
- **Packing agressivo**: limites baixos (2/3/5) forçam curadoria; configurável
- **Conversão PackedContext → RetrievedContext na eval**: evita quebrar schema existente
- **RAG permanece opcional**: `ActionBrief` funciona sem packing_result

## Próximos Passos

- Integrar reranking/packing no pipeline principal (fora da avaliação)
- Testar com SentenceTransformerProvider real
- Ajustar limites de packing baseado em dados reais
