# Epic 36.1 — Product Capability & Configuration Registry

## What
Central layer for product capabilities, feature flags, configuration requirements, and onboarding readiness. Users can see everything they need to configure before using the product.

## Capabilities (25+)
Covering all 13 categories: core, database, rag, evidence, claims, playbooks, dossier, quality, structured_outputs, llm_judge, export, frontend, developer_tools.

Each has: id, name, description, category, required, enabled_by_default, status, required_env_vars, optional_env_vars, required_extras, required_services, setup_instructions, failure_mode, failure_message, user_visible, documentation_ref.

## Configurations (17+)
Each has: key, description, required_for, required, secret, default, current_value, source, example, validation_rule, user_message.

## Readiness Service
- `get_product_readiness()` — comprehensive report with ready bool, blocking/optional/unavailable/degraded lists, setup checklist, user messages
- `validate_configuration()` — list of missing required config items
- `get_setup_checklist()` — checklist with progress
- `get_optional_features_status()` — optional features and their status

## API
- `GET /product/capabilities` — list all with status
- `GET /product/configuration` — list all config items
- `GET /product/setup-checklist` — checklist with progress
- `GET /product/readiness` — readiness report

## Key Design Decisions
- No DB dependency — env vars + importlib only
- Status computed per-call (always current)
- Required missing → ready=false
- Optional missing → ready=true with explanation
- Secrets masked (****) in API responses
- Instructor never imported at module level

## Test Results
- 6 capability registry tests
- 9 config registry tests
- 10 readiness service tests
- 9 integration API tests — all passing
