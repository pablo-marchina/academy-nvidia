# Product Configuration Contract

**Module:** `src/services/product/`
**Version:** 1.0
**Date:** 2026-06-13

## Purpose

Define the contract for capability registry, configuration registry, and
product readiness service.

## Capability Registry (`capability_registry.py`)

### `CapabilityDefinition`

```
capability_id: str          # Unique identifier
name: str                   # Human-readable name
description: str            # Functional description
category: CapabilityCategory
required: bool              # True = product cannot function without it
enabled_by_default: bool    # True = active without extra config
required_env_vars: list[str]
optional_env_vars: list[str]
required_extras: list[str]  # pip extras (e.g., "llm-judge")
required_services: list[str]
health_check_key: str
setup_instructions: str
failure_mode: str
user_visible: bool
documentation_ref: str
```

### Categories

`core`, `database`, `rag`, `evidence`, `claims`, `playbooks`, `dossier`,
`quality`, `structured_outputs`, `llm_judge`, `export`, `frontend`,
`developer_tools`

### Status

`available`, `unavailable`, `not_configured`, `missing_dependency`,
`degraded`, `disabled`, `experimental`

## Configuration Registry (`config_registry.py`)

### `ConfigItem`

```
key: str                    # Env var name
description: str            # Functional description
required_for: list[str]     # Capability IDs that depend on this
required: bool              # True = core requirement
secret: bool                # True = mask value in API responses
default: str                # Default value
current_value: str | None   # Resolved from environment
source: str                 # Always "env"
example: str
validation_rule: str
user_message: str
```

## Readiness Service (`readiness_service.py`)

### `ProductReadinessReport`

```
ready: bool
blocking_missing_config: list[dict]
optional_missing_config: list[dict]
unavailable_capabilities: list[dict]
degraded_capabilities: list[dict]
setup_checklist: list[dict]
user_messages: list[str]
```

### Methods

- `list_capabilities() -> list[ResolvedCapability]`
- `get_capability_status(id) -> ResolvedCapability | None`
- `list_required_configuration() -> list[dict]`
- `validate_configuration() -> list[dict]`
- `get_product_readiness() -> ProductReadinessReport`
- `get_setup_checklist() -> list[dict]`
- `get_missing_configuration() -> list[dict]`
- `get_optional_features_status() -> list[dict]`

## Invariants

1. Capability IDs are unique and never change once registered.
2. Status is computed at call time, never cached.
3. Required config missing → `ready=false` with blocking items listed.
4. Optional missing features never set `ready=false`.
5. Secrets are masked (`****`) in API responses.
6. No optional dependency is imported at module level.
7. `instructor` is never imported outside `llm_judge_instructor_adapter.py`.
8. Environment variables not in the registry are ignored.
9. The setup checklist always includes all required env vars.
10. Unknown extras return `False` from `is_extra_installed`.

## API Endpoints

### GET /product/capabilities

Returns `list[ProductCapabilityRead]`:
```
capability_id, name, description, category, required,
status, status_reason, required_env_vars, optional_env_vars,
required_extras, required_services, setup_instructions,
failure_mode, user_visible, documentation_ref
```

### GET /product/configuration

Returns `list[ProductConfigurationItemRead]`:
```
key, description, required, secret, default, current_value, is_set
```

### GET /product/setup-checklist

Returns `ProductSetupChecklistRead`:
```
items: [{key, description, is_set, required}]
total, completed, pending
```

### GET /product/readiness

Returns `ProductReadinessRead`:
```
ready, blocking_missing_config, optional_missing_config,
unavailable_capabilities, degraded_capabilities,
setup_checklist, user_messages
```

## Health Integration

- `GET /health/product` continues to exist for product DB health
- `GET /health/dependencies` continues to exist for dependency status
- `GET /product/readiness` is the comprehensive readiness overview
- Health endpoints are not replaced; they serve different granularity
