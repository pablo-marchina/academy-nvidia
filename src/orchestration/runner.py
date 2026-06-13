from __future__ import annotations

from typing import Any, cast

from sqlalchemy.orm import Session

from src.orchestration.nodes import WORKFLOW_NODES, NodeResult
from src.orchestration.state import NodeStatus, ProductWorkflowState, WorkflowStatus
from src.repositories.workflow import WorkflowRepository

_MAX_RETRY_DEFAULT = 1


_NON_RETRYABLE_ERRORS = ("LookupError", "ValueError", "TypeError", "AssertionError")


def _is_retryable(error_message: str) -> bool:
    for exc_name in _NON_RETRYABLE_ERRORS:
        if error_message and error_message.startswith(exc_name):
            return False
    return True


class WorkflowRunner:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = WorkflowRepository(session)

    def _dump_state(self, state: ProductWorkflowState) -> dict:
        _session_val = state.metadata_json.pop("_session", None)
        try:
            return state.model_dump(mode="json")
        finally:
            if _session_val is not None:
                state.metadata_json["_session"] = _session_val

    def run_workflow(
        self,
        state: ProductWorkflowState,
        *,
        max_retry: int = _MAX_RETRY_DEFAULT,
    ) -> ProductWorkflowState:
        state.metadata_json["_session"] = self.session
        self.repo.update_workflow_status(
            state.workflow_id,
            status=WorkflowStatus.RUNNING,
            current_node="",
            state_json=self._dump_state(state),
        )

        for node_def in WORKFLOW_NODES:
            if state.current_node and node_def.name not in state.current_node:
                pass

            state.current_node = node_def.name
            self.repo.update_workflow_status(
                state.workflow_id,
                status=WorkflowStatus.RUNNING,
                current_node=node_def.name,
                state_json=self._dump_state(state),
            )

            node_run = self.repo.create_node_run(
                workflow_run_id=state.workflow_id,
                node_name=node_def.name,
                input_snapshot=self._dump_state(state),
            )

            self.repo.update_node_run_status(node_run.id, status="running")
            result = self._execute_node_with_retry(node_def.fn, state, node_run.id, max_retry)

            if result.status == NodeStatus.FAILED:
                self.repo.update_node_run_status(
                    node_run.id,
                    status="failed",
                    output_snapshot=result.state_updates,
                    error_message=result.error_message,
                )
                state.failed_nodes.append(node_def.name)
                state.error_message = result.error_message
                if node_def.critical:
                    self.repo.fail_workflow(
                        state.workflow_id,
                        error_message=result.error_message
                        or f"Critical node failed: {node_def.name}",
                        state_json=self._dump_state(state),
                    )
                    return state
                continue

            if result.status == NodeStatus.DEGRADED:
                self.repo.update_node_run_status(
                    node_run.id,
                    status="degraded",
                    output_snapshot=result.state_updates,
                    error_message=result.error_message,
                )
                state.degraded_nodes.append(node_def.name)
            elif result.status == NodeStatus.SKIPPED:
                self.repo.update_node_run_status(
                    node_run.id,
                    status="skipped",
                    output_snapshot=result.state_updates,
                    error_message=result.error_message,
                )
            else:
                self.repo.update_node_run_status(
                    node_run.id,
                    status="completed",
                    output_snapshot=result.state_updates,
                )

            state.completed_nodes.append(node_def.name)
            for key, value in (result.state_updates or {}).items():
                if value is not None:
                    setattr(state, key, value)

            self.repo.update_workflow_status(
                state.workflow_id,
                status=WorkflowStatus.RUNNING,
                current_node=node_def.name,
                state_json=self._dump_state(state),
            )

        if state.failed_nodes and state.degraded_nodes:
            failed_list = ", ".join(state.failed_nodes)
            degraded_list = ", ".join(state.degraded_nodes)
            reason = f"Nodes failed: {failed_list}; degraded: {degraded_list}"
            self.repo.degrade_workflow(
                state.workflow_id, degraded_reason=reason, state_json=self._dump_state(state)
            )
        elif state.failed_nodes:
            self.repo.fail_workflow(
                state.workflow_id,
                error_message=state.error_message or "Non-critical node(s) failed",
                state_json=self._dump_state(state),
            )
        elif state.degraded_nodes:
            reason = f"Degraded nodes: {', '.join(state.degraded_nodes)}"
            self.repo.degrade_workflow(
                state.workflow_id, degraded_reason=reason, state_json=self._dump_state(state)
            )
        else:
            self.repo.complete_workflow(state.workflow_id, state_json=self._dump_state(state))

        state.metadata_json.pop("_session", None)
        return state

    def _execute_node_with_retry(
        self,
        node_fn: Any,
        state: ProductWorkflowState,
        node_run_id: str,
        max_retry: int,
    ) -> NodeResult:
        last_result = NodeResult(status=NodeStatus.FAILED, error_message="No execution attempt")
        for attempt in range(max_retry + 1):
            try:
                last_result = cast(NodeResult, node_fn(state))
                if last_result.status in (
                    NodeStatus.COMPLETED,
                    NodeStatus.SKIPPED,
                    NodeStatus.DEGRADED,
                ):
                    return last_result
                if last_result.status == NodeStatus.FAILED and not _is_retryable(
                    last_result.error_message or ""
                ):
                    return last_result
            except Exception as exc:
                last_result = NodeResult(
                    status=NodeStatus.FAILED, error_message=f"{type(exc).__name__}: {exc}"
                )

            if attempt < max_retry and _is_retryable(last_result.error_message or ""):
                self.repo.increment_node_retry(node_run_id)
        return last_result


def _has_langgraph() -> bool:
    try:
        __import__("langgraph")
        return True
    except ImportError:
        return False


def create_runner(session: Session) -> WorkflowRunner:
    return WorkflowRunner(session)
