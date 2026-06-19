# Plan: Human-in-the-Loop Checkpoint Persistence + E2E Test

## Objective

Complete the human-in-the-loop cycle by (1) writing an end-to-end test that validates interrupt, cache, and resume through the runner + agent graph, and (2) replacing the in-memory `_CHECKPOINTER_CACHE` with a PostgreSQL-backed checkpointer so checkpoints survive process restarts and work across multiple workers.

## Context Read

- `src/orchestration/runner.py`
- `src/orchestration/service.py`
- `src/api/product_routes.py`
- `src/agents/graph.py` (lines 1000–1200)
- `src/agents/state.py`
- `tests/unit/test_workflow_runner.py`
- `tests/unit/test_langgraph_product_graph.py` (checkpointer tests)
- `tests/integration/test_product_workflow_api.py`
- `docs/contracts/pipeline_output_contract.md`
- `pyproject.toml` (dependencies)

## Relevant Files

- `src/orchestration/runner.py` — `_CHECKPOINTER_CACHE`, `_build_checkpointer`, checkpointer usage
- `src/orchestration/service.py` — `submit_review` method (used as resume entry point)
- `src/database/models.py` — new `WorkflowCheckpoint` table (or reuse existing)
- `tests/unit/test_workflow_runner.py` — new E2E test class for interrupt/resume cycle
- `docs/contracts/pipeline_output_contract.md` — may need update for new checkpointer behavior

## Scope

- Write an E2E test that exercises the full runner + agent graph interrupt/resume cycle with mocked graph services.
- Replace `_CHECKPOINTER_CACHE` (module-level dict) with a SQLAlchemy-backed persistent checkpointer using the existing Postgres connection.
- Update `WorkflowRepository` or runner to save/load checkpoints from the database.
- Validate all existing tests still pass.

## Out of Scope

- No UI changes for manual human-in-the-loop workflow.
- No monitoring/alerting for stuck checkpoints.
- No migration scripts for existing checkpoints (cache starts empty).
- No changes to the `interrupt()` call site in `_needs_review`.

## Proposed Implementation

### Step 1 — E2E Test (runner level)

Add a test class `TestRunnerInterruptResume` in `tests/unit/test_workflow_runner.py` that:

1. Creates a `WorkflowRun` + `ProductWorkflowState` with `startup_id`.
2. Patches `src.orchestration.runner._try_build_agent_graph` to build a real `build_startup_radar_graph` with all services mocked (`MagicMock`).
3. Patches `src.agents.graph._run_quality_gates` to force routing to `needs_review`.
4. Calls `runner.run_workflow(state)`.
5. Asserts result is `AWAITING_REVIEW` with `_langgraph_thread_id` in metadata.
6. Reconstructs resume state from DB.
7. Calls `runner.resume_workflow(state, decision="approve")`.
8. Asserts result is `COMPLETED` (or `quality_passed`).

### Step 2 — Persistent Checkpointer

1. Add `langgraph-checkpoint-postgres` to `pyproject.toml` `[project.optional-dependencies]` under `agent-orchestration`.
2. Replace `_build_checkpointer()` / `_CHECKPOINTER_CACHE` / `_cache_checkpointer` / `_get_cached_checkpointer` in `runner.py` with a `PostgresSaver`-based approach that uses the runner's `self.session` (or a dedicated connection) to persist checkpoints.
3. Wire `PostgresSaver` setup into `run_workflow` and `resume_workflow` so the same checkpointer instance is used for both calls, matching the current cache pattern.
4. Update `WorkflowRepository` if needed for the checkpointer table.
5. Update tests: existing runner tests that patch `_try_build_agent_graph` still pass; the E2E test from Step 1 must pass with the persistent checkpointer.

### Step 3 — Validation

- `pytest tests/unit/test_workflow_runner.py` passes (including new E2E test).
- `pytest tests/integration/test_product_workflow_api.py` passes (resume integration tests).
- `pytest tests/unit/test_langgraph_product_graph.py -k checkpoint` passes (checkpointer unit tests).
- `ruff check .` passes.
- `mypy src` passes (or known pre-existing issues unchanged).

## Files to Create/Change

### Change
- `tests/unit/test_workflow_runner.py` — add `TestRunnerInterruptResume` E2E test class
- `src/orchestration/runner.py` — replace `_CHECKPOINTER_CACHE` with `PostgresSaver`
- `pyproject.toml` — add `langgraph-checkpoint-postgres` to `agent-orchestration` optional deps
- `docs/contracts/pipeline_output_contract.md` — note checkpointer persistence contract if needed

## Tests/Validations

```bash
pytest tests/unit/test_workflow_runner.py -v
pytest tests/unit/test_langgraph_product_graph.py -k checkpoint -v
pytest tests/integration/test_product_workflow_api.py -v
ruff check .
mypy src
```

## Risks

| Risk | Mitigation |
|------|-----------|
| `PostgresSaver` API incompatible with langgraph 1.1.10 | Pin compatible version; test `create` + `put` + `get_tuple` first; fall back to custom `BaseCheckpointSaver` if needed |
| Migration for checkpointer table needed | Use `PostgresSaver.setup()` which creates the table automatically |
| PostgresSaver needs its own connection pool, separate from SQLAlchemy | Pass the existing engine or connection; wrap in a singleton if needed |

## Definition of Done

- [ ] E2E test validates full interrupt -> cache -> resume -> complete cycle at the runner level.
- [ ] `_CHECKPOINTER_CACHE` removed, replaced by persistent checkpointer.
- [ ] All existing tests still pass.
- [ ] Ruff and mypy pass.

---

*Gerado em: 2026-06-16*
*Modo: Plan → Build → Review*
