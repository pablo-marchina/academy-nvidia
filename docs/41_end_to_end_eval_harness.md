# Golden Eval Harness — End-to-End Pipeline Regression Detection

## Objetivo

Detectar regressoes na pipeline completa (classificacao → scoring → diagnostico → recomendacao → brief) sem dependencia externa, LLM ou Qdrant.

## Arquitetura

```
examples/golden/
  startup_high_fit.json           # HealthTech AI com evidencias fortes
  startup_weak_evidence.json      # E-commerce sem sinais AI, zero evidencias
  startup_non_ai.json             # Consultoria, sem AI
  startup_no_rag_context.json     # AI Infrastructure com gaps diagnosticados
  startup_rag_supported.json      # AI company com gaps + RAG corpus
  startup_validate_manually.json  # Evidencia media, baixa confianca
  startup_monitor_or_discard.json # Poucos sinais AI, sem clientes
  expected_outputs.json           # Expectativas centralizadas (cross-check)
  README.md                       # Documentacao dos casos

tests/evals/
  __init__.py
  helpers.py                      # GoldenCase, load_golden_case, run_pipeline_*, 11 asserts
  test_pipeline_golden.py         # 38 testes: 6 classes + 3 cross-cutting
```

## Componentes

### GoldenCase
Dataclass que carrega `case_id`, `profile`, `evidence`, `expected` do JSON.

### Helpers
- `load_golden_case(path)` → `GoldenCase`
- `run_pipeline_on_case(case, chunk_index=None)` → `PipelineResult`
- `run_pipeline_with_rag(case)` → `tuple[PipelineResult, PipelineResult]` (sem RAG vs com RAG)

### Assert Helpers (11)
1. `assert_pipeline_contract` — campos obrigatorios no PipelineResult
2. `assert_expected_motion` — recommended_motion dentro da lista esperada
3. `assert_expected_gaps` — gaps detectados incluem os esperados
4. `assert_no_tech_without_gap` — gap nao detectado → 0 tecnologias
5. `assert_missing_evidence_propagates` — missing_evidence propaga corretamente
6. `assert_confidence_coherent` — sem HIGH evidence → composite nao HIGH
7. `assert_action_brief_sections` — secoes minimas + Executive Summary + Evidence
8. `assert_no_strong_rec_without_evidence` — approach_now requer HIGH evidence
9. `assert_rag_does_not_alter_motion` — RAG nao muda recommended_motion
10. `assert_rag_context_in_brief` — supporting_nvidia_context + packed_rag_contexts presentes
11. `assert_rag_context_not_in_evidence_used` — RAG content nao leak em evidence_used

### RAG nos Golden Cases
- `MockEmbeddingProvider` + `InMemoryVectorStore` = deterministico, offline, sem download
- Golden RAG cases comparam output com e sem RAG em um unico teste
- `build_default_index()` carrega corpus de `data/nvidia_corpus/` (10 documentos)

## Invariantes

Toda golden case verifica:
1. Pipeline contract (todos os campos)
2. Motion dentro da faixa esperada
3. Score dentro de [min_score, max_score]
4. Gaps esperados estao entre os detectados
5. Nenhuma recomendacao sem gap tem tecnologias
6. Missing evidence propaga de diagnosis → resultado
7. Confianca coerente (sem HIGH evidence → composite nao HIGH)
8. Brief tem secoes minimas
9. Markdown renderizado com secoes obrigatorias
10. Nenhum APPROACH_NOW sem HIGH evidence

Golden RAG adicionam:
11. RAG nao altera recommended_motion
12. Brief RAG tem supporting_nvidia_context e packed_rag_contexts
13. Conteudo RAG nao aparece em evidence_used

## Execucao

```bash
# Todos os golden evals
pytest tests/evals/ -v

# Apenas unitarios (excluindo golden evals)
pytest tests/unit/ -v
```

## Manutencao

Quando a pipeline mudar intencionalmente:

1. Execute `pytest tests/evals/` para ver quais casos falham
2. Para cada caso, rode o pipeline manualmente para ver o novo output
3. Atualize `expected_outputs.json` e o campo `expected` no JSON do caso
4. Execute `pytest tests/evals/` para confirmar que tudo passa

Nao altere os casos golden para "fazer o teste passar" — eles devem refletir o comportamento esperado do pipeline.
