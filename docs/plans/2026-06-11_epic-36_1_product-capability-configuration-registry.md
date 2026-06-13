# Epic 36.1 — Product Capability & Configuration Registry

## Goal
Create a central layer for product capabilities, feature flags, configuration requirements, and onboarding readiness so users can see everything they need to configure before using the product.

## Scope
- Capability registry with 25+ capabilities across all categories
- Configuration registry with all env vars, extras, and service dependencies
- ProductReadinessService to aggregate and report readiness
- 4 API endpoints: GET /product/capabilities, /product/configuration, /product/setup-checklist, /product/readiness
- Lazy imports for optional dependencies (instructor)
- pyproject.toml `llm-judge` extra
- Tests, docs, contract, README updates

## Out of Scope
- UI, auth/roles, MCP, TOON/JTON, new LLM provider
- Pipeline changes, scoring changes, RAG retrieval changes, Qdrant ingestion changes
- Making instructor required

## Files to Create
1. `src/services/product/capability_registry.py`
2. `src/services/product/config_registry.py`
3. `src/services/product/readiness_service.py`
4. `tests/unit/test_capability_registry.py`
5. `tests/unit/test_config_registry.py`
6. `tests/unit/test_readiness_service.py`
7. `tests/integration/test_product_readiness_api.py`
8. `docs/63_product_capability_configuration_registry.md`
9. `docs/contracts/product_configuration_contract.md`

## Files to Modify
1. `src/api/product_schemas.py` — add readiness/capability schemas
2. `src/api/product_routes.py` — add 4 endpoints
3. `pyproject.toml` — add `llm-judge` extra
4. `.env.example` — add documented vars
5. `docs/contracts/product_api_contract.md` — add endpoint docs
6. `README.md` — add Product Setup section
7. `ROADMAP.md` — add Epic 36.1
8. `EVALS.md` — add test entries

## Validation
- pytest (all tests pass)
- ruff check .
- black --check .
- mypy src
- python scripts/check_scope.py
- python scripts/check_docs_closure.py
