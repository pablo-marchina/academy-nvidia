# Epic 33 — NVIDIA Activation Playbook Library

**Date:** 2026-06-12
**Status:** Build — em execução

## Objetivo
Criar biblioteca de playbooks de ativação NVIDIA, fazer match determinístico com gaps detectados,
ranquear por confiança/prioridade, persistir recomendações e expor via API do produto.

## Escopo
### Dentro
- `src/config/playbooks/nvidia_activation_playbooks.yaml` — 10 playbooks de ativação
- `src/playbook/schemas.py` — ActivationPlaybook, ActivationPlaybookMatch, ActivationRecommendationSchema
- `src/playbook/loader.py` — load_playbooks() com validação de schema YAML
- `src/database/models.py` — ActivationRecommendationRecord (FK AnalysisRun, JSON columns, indexes)
- `migrations/versions/b2c3d4e5f6a7_create_activation_recommendations.py`
- `src/repositories/activation.py` — ActivationRecommendationRepository (CRUD, replace, list, get_top)
- `src/services/product/activation_service.py` — ActivationPlaybookService (matching, confidence, ranking, persist)
- `src/services/product/degraded.py` — 4 readiness checks (NO_ACTIVATION_PLAYBOOK_MATCH, etc.)
- `src/api/product_schemas.py` — ActivationPlaybookRead, ActivationRecommendationRead, GenerateResponse; OpportunityListItem com 4 campos de ativação
- `src/api/product_routes.py` — 3 endpoints: GET playbooks, GET/POST recommendations
- `src/services/product/service.py` — auto-generate activation no lifecycle do analysis run
- Testes unitários (loader, matcher/ranking) e integração (API)
- Documentação (plan, module doc, contract)

### Fora (v2)
- UI para visualização de playbooks
- LLM matching (além do determinístico)
- Feedback loop (aceitar/rejeitar recomendação)
- Notificação de match para NVIDIA team

## Decisões
- Playbook source em YAML (não persistido DB-first); PyYAML já instalado
- Matching v1 puramente determinístico: gap.type in playbook.target_gap_types
- Confiança: avg(gap_confidences) + mapping_boost + claim_boost - coverage_penalty - unsupported_penalty - degraded_penalty; clamped [0.0, 1.0]
- Prioridade: 1 (high conf + high value) a 4 (low conf)
- Idempotência via replace_recommendations_for_analysis_run (delete all + bulk create)
- Integração inline no lifecycle (sem job separado); erros silenciosos
- Opportunities enriquecido via ActivationRecommendationRepository O(1) por run_id

## Files
- `src/config/playbooks/nvidia_activation_playbooks.yaml`
- `src/playbook/__init__.py`, `src/playbook/schemas.py`, `src/playbook/loader.py`
- `src/database/models.py` — ActivationRecommendationRecord
- `migrations/versions/b2c3d4e5f6a7_create_activation_recommendations.py`
- `src/repositories/activation.py`
- `src/services/product/activation_service.py`
- `src/services/product/degraded.py`
- `src/api/product_schemas.py`
- `src/api/product_routes.py`
- `src/services/product/service.py`
- `tests/unit/test_activation_playbook_loader.py`
- `tests/unit/test_activation_playbook_matcher.py`
- `tests/integration/test_activation_api.py`

## Next
- Rodar validacoes (pytest, ruff, black, mypy, scope, docs-closure)
- Atualizar ROADMAP, EVALS, DECISIONS
- Atualizar Obsidian vault
