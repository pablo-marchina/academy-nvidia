# LangGraph Orchestration Layer

## Status
Implemented (Epic 41)

## Purpose
Stateful orchestration layer for product analysis workflows. Supports both LangGraph (optional extra) and deterministic sequential fallback.

## Architecture

```
POST /workflows/product-runs
         │
         ▼
WorkflowOrchestrationService
    create_and_run_workflow()
         │
         ▼
WorkflowRunner.run_workflow()
    ┌──────────────────────────┐
    │ Iterate WORKFLOW_NODES   │
    │  11 nodes total          │
    │  sequential execution    │
    │  per-node retry (max 1)  │
    └──────────┬───────────────┘
               │
               ▼
WorkflowRepository
    - create_workflow_run()
    - create_node_run()
    - update_workflow_status()
    - complete/fail/degrade
```

## Components

| Module | Responsibility |
|---|---|
| `state.py` | `ProductWorkflowState` — 19 fields tracking IDs, status, errors |
| `nodes.py` | `NodeResult`, `NodeDefinition`, `@_register` decorator, `WORKFLOW_NODES` list |
| `node_impl.py` | 11 node implementations wrapping existing services |
| `runner.py` | `WorkflowRunner` — sequential executor with retry policy |
| `service.py` | `WorkflowOrchestrationService` — create, run, query workflows |

## 11 Workflow Nodes

1. `load_startup_or_candidate` (critical)
2. `collect_or_load_evidence`
3. `validate_evidence`
4. `diagnose_gaps`
5. `retrieve_nvidia_context`
6. `map_nvidia_technologies`
7. `generate_claims`
8. `match_activation_playbooks`
9. `generate_activation_dossier`
10. `run_product_quality`
11. `summarize_readiness`

## Fallback Behavior

When LangGraph is not installed:
- `_has_langgraph()` returns `False`
- `WorkflowRunner` executes nodes deterministically in sequence
- Capability registry shows `agent_orchestration` as missing dependency

## Retry Policy

- Max 1 retry per node
- No retry for `LookupError`, `ValueError`, `TypeError`, `AssertionError`
- Retryable errors: `ConnectionError`, `TimeoutError`, `RuntimeError`, generic `Exception`

## Database Models

- `WorkflowRun` — workflow-level state, status, error tracking
- `WorkflowNodeRun` — per-node tracing with input/output snapshots

## Degraded States

| Code | Severity | Trigger |
|---|---|---|
| `WORKFLOW_NODE_FAILED` | error | Node returns FAILED status |
| `WORKFLOW_DEGRADED` | warning | Degraded nodes present |
| `WORKFLOW_RAG_SKIPPED` | warning | RAG unavailable |
| `WORKFLOW_QUALITY_FAILED` | error | Quality run fails |
| `WORKFLOW_DOSSIER_MISSING` | warning | Dossier generation skipped |
| `WORKFLOW_DISCOVERY_PROMOTION_FAILED` | warning | Candidate promotion error |
