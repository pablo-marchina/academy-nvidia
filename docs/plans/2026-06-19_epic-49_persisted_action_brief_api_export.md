# Epic 49 - Persisted Quantitative Action Brief API Export

## Objetivo
Expor o `action_brief` quantitativo persistido no `AnalysisRun` por API e export JSON, sem recalcular brief, ranking, RAG ou scoring.

## Escopo
- Ajustar `GET /analysis-runs/{run_id}/brief`.
- Criar `GET /analysis-runs/{run_id}/brief/export/json`.
- Usar schemas Pydantic para projetar apenas campos auditaveis ja persistidos.
- Ler `ActionBriefRecord.brief_json` e `AnalysisRun.output_snapshot_json["brief_metrics"]`.
- Cobrir comportamento de brief ausente, brief bloqueado, preservacao quantitativa e sanitizacao.

## Arquivos Planejados
- `src/api/product_routes.py`
- `src/api/product_schemas.py`
- `src/services/product/export_service.py`
- `tests/integration/test_product_workflow_api.py`
- `tests/unit/test_action_brief_export.py`
- `tests/acceptance/test_analysis_run_golden_path_api.py`

## Garantias
- Nenhum endpoint de consulta/export chama `generate_brief`, LangGraph, LLM, Qdrant, scraping ou recommendation engine.
- Nenhum threshold, score, ranking, filtro ou campo calculado novo sera introduzido.
- `brief_metrics` sera preservado a partir do snapshot persistido.
- Brief bloqueado sera retornado com `brief_status`, `blockers` e `audit_trail`.
- Brief ausente retornara 404 explicito.

## Validacao
- `python -m pytest tests/integration/test_product_workflow_api.py`
- `python -m pytest tests/unit/test_action_brief_export.py`
- `python -m pytest tests/acceptance/test_analysis_run_golden_path_api.py`
- `python -m mypy src/api src/repositories src/services`

## Risco Principal
Consumidores antigos de `GET /analysis-runs/{run_id}/brief` que esperavam o envelope com `brief_json`/`brief_markdown` precisarao consumir a nova projecao quantitativa. O envelope antigo permanece em `GET /analysis-runs/{run_id}` para reduzir impacto.
