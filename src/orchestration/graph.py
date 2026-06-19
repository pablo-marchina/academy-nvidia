"""LangGraph StateGraph for the product workflow.

Each domain node is wrapped to adapt the NodeResult protocol to LangGraph's
state-update protocol. Per-node tracing (node_run records) is preserved.
"""

from __future__ import annotations

from typing import Any

from src.orchestration import node_impl  # noqa: F401 — triggers @_register decorators
from src.orchestration.nodes import WORKFLOW_NODES
from src.orchestration.state import NodeStatus, ProductWorkflowState
from src.repositories.workflow import WorkflowRepository
from src.services.product.readiness_service import ProductReadinessService

LANGGRAPH_AVAILABLE: bool
try:
    from langgraph.graph import StateGraph, START, END  # noqa: I001

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class NodeExecutionError(Exception):
    """Raised when a LangGraph node execution fails."""

    def __init__(self, node_name: str, error_message: str) -> None:
        self.node_name = node_name
        self.error_message = error_message
        super().__init__(f"[{node_name}] {error_message}")


def _preflight_configuration_check(state: ProductWorkflowState) -> dict[str, Any]:
    """Validate that the workflow can proceed with the given configuration.

    Calls ProductReadinessService to check for missing capabilities.
    If not ready, raises NodeExecutionError with the blocking messages.
    """
    svc = ProductReadinessService()
    report = svc.get_product_readiness()

    if not report.ready:
        msg = "; ".join(report.user_messages) if report.user_messages else (
            "Product readiness checks failed"
        )
        raise NodeExecutionError("preflight_configuration_check", msg)

    return {
        "status": "initialized",
        "blockers": [],
        "current_node": "preflight_configuration_check",
        "completed_nodes": list(state.completed_nodes) + ["preflight_configuration_check"],
    }


def _finish(state: ProductWorkflowState) -> dict[str, Any]:
    """Finalize the workflow execution."""
    return {
        "status": "ready_for_execution",
        "current_node": "finish",
        "completed_nodes": list(state.completed_nodes) + ["finish"],
    }


def _make_langgraph_node(node_def: Any) -> Any:
    """Adapt a @_register node function to LangGraph's state-update protocol."""
    node_name = node_def.name
    node_fn = node_def.fn

    def wrapper(state: ProductWorkflowState) -> dict[str, Any]:
        _session = state.metadata_json.pop("_session", None)
        wf_repo = WorkflowRepository(_session) if _session else None
        node_run_id: str | None = None

        if wf_repo:
            input_snapshot = state.model_dump(mode="json")
            state.metadata_json["_session"] = _session
            node_run = wf_repo.create_node_run(
                workflow_run_id=state.workflow_id,
                node_name=node_name,
                input_snapshot=input_snapshot,
            )
            node_run_id = node_run.id
            wf_repo.update_node_run_status(node_run.id, status="running")

        result = node_fn(state)

        if wf_repo and node_run_id:
            status_map = {
                NodeStatus.COMPLETED: "completed",
                NodeStatus.DEGRADED: "degraded",
                NodeStatus.SKIPPED: "skipped",
            }
            wf_repo.update_node_run_status(
                node_run_id,
                status=status_map.get(result.status, "completed"),
                output_snapshot=result.state_updates,
                error_message=result.error_message,
            )

        if result.status == NodeStatus.FAILED:
            if wf_repo and node_run_id:
                wf_repo.update_node_run_status(
                    node_run_id, status="failed", error_message=result.error_message
                )
            raise NodeExecutionError(node_name, result.error_message or "Unknown error")

        updates: dict[str, Any] = dict(result.state_updates or {})
        updates["current_node"] = node_name
        updates["completed_nodes"] = list(state.completed_nodes) + [node_name]

        if result.status == NodeStatus.DEGRADED:
            updates["degraded_nodes"] = list(state.degraded_nodes) + [node_name]

        return updates

    return wrapper


def build_startup_radar_graph() -> Any | None:
    """Build and compile the minimal LangGraph workflow.

    Nodes: preflight_configuration_check → finish.
    This is the single source of truth for the workflow skeleton.
    """
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(state_schema=ProductWorkflowState)

    graph.add_node("preflight_configuration_check", _preflight_configuration_check)
    graph.add_node("finish", _finish)

    graph.add_edge(START, "preflight_configuration_check")
    graph.add_edge("preflight_configuration_check", "finish")
    graph.add_edge("finish", END)

    return graph.compile()


def build_workflow_graph() -> Any | None:
    """Build and compile the full LangGraph workflow for the product pipeline.

    Extends the minimal skeleton with all @_register domain nodes.
    """
    if not LANGGRAPH_AVAILABLE or not WORKFLOW_NODES:
        return None

    graph = StateGraph(state_schema=ProductWorkflowState)

    graph.add_node("preflight_configuration_check", _preflight_configuration_check)
    graph.add_node("finish", _finish)

    for node_def in WORKFLOW_NODES:
        graph.add_node(node_def.name, _make_langgraph_node(node_def))

    node_names = [node_def.name for node_def in WORKFLOW_NODES]
    graph.add_edge(START, "preflight_configuration_check")
    graph.add_edge("preflight_configuration_check", node_names[0])
    for i in range(len(node_names) - 1):
        graph.add_edge(node_names[i], node_names[i + 1])
    graph.add_edge(node_names[-1], "finish")
    graph.add_edge("finish", END)

    return graph.compile()
