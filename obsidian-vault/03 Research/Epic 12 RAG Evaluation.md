# Epic 12 — RAG Evaluation & Retrieval Quality Gates

**Resumo:** Camada de avaliação offline para o Product RAG com golden queries, métricas determinísticas e quality gates.

## Entregas

- `src/evaluation/rag_eval_schemas.py` — RagEvalCase, RagRetrievalMetrics, RagEvalResult, RagQualityGateResult
- `src/evaluation/rag_eval.py` — run_rag_eval(), run_quality_gates(), format_eval_summary()
- `examples/rag_eval/golden_queries.json` — 16 golden queries
- `examples/rag_eval/expected_contexts.json` — chunk_ids esperados
- `tests/unit/test_rag_eval.py` — 20 testes
- `docs/36_rag_evaluation.md`

## Métricas (7)

hit_at_k, expected_source_coverage, expected_product_coverage, irrelevant_context_count, missing_context_count, top_1_expected_match, context_precision

## Quality Gates (6)

hit_at_3_for_critical, top_1_for_critical, zero_missing_for_known, irrelevant_below_limit, provenance_check, missing_context_explicit

## Decisões

- Avaliação determinística — sem LLM judge, sem embeddings, sem Qdrant
- Golden queries versionadas em JSON — referenciam source_ids do sources.yaml
- Reusa ChunkIndex sem modificações
- Nenhuma alteração em RAG, Briefing, Pipeline, Recommendation, Diagnosis

## Testes

- 20 testes (golden queries, métricas, gates, provenance, brief compatibilidade)
- Total do projeto: 188 testes, 21 arquivos
