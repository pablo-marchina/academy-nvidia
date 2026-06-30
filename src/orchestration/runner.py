from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from src.orchestration.graph import NodeExecutionError, build_workflow_graph, session_var
from src.orchestration.state import ProductWorkflowState, WorkflowStatus
from src.repositories.workflow import WorkflowRepository

try:
    from langgraph.types import Command

    _LANGGRAPH_COMMAND_AVAILABLE = True
except ImportError:
    _LANGGRAPH_COMMAND_AVAILABLE = False

_HAS_LANGGRAPH: bool | None = None


def _has_langgraph() -> bool:
    global _HAS_LANGGRAPH
    if _HAS_LANGGRAPH is not None:
        return _HAS_LANGGRAPH
    try:
        import langgraph  # noqa: F401

        _HAS_LANGGRAPH = True
    except ImportError:
        _HAS_LANGGRAPH = False
    return _HAS_LANGGRAPH


_POSTGRES_CHECKPOINTER: Any | None = None
_CHECKPOINTER_CACHE: dict[str, Any] = {}


def _build_postgres_checkpointer() -> Any | None:
    global _POSTGRES_CHECKPOINTER
    if _POSTGRES_CHECKPOINTER is not None:
        return _POSTGRES_CHECKPOINTER
    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from src.database.session import get_product_db_url

        url = get_product_db_url()
        if url and url.startswith("postgresql"):
            import psycopg
            from psycopg.rows import dict_row

            conn = psycopg.connect(url, autocommit=True, prepare_threshold=0, row_factory=dict_row)
            saver = PostgresSaver(conn)
            saver.setup()
            _POSTGRES_CHECKPOINTER = saver
            return saver
    except Exception:
        pass
    return None


def _build_checkpointer() -> Any | None:
    pg = _build_postgres_checkpointer()
    if pg is not None:
        return pg
    try:
        from langgraph.checkpoint.memory import MemorySaver

        return MemorySaver()
    except ImportError:
        return None


def _cache_checkpointer(thread_id: str, checkpointer: Any) -> None:
    _CHECKPOINTER_CACHE[thread_id] = checkpointer


def _get_cached_checkpointer(thread_id: str) -> Any | None:
    return _CHECKPOINTER_CACHE.get(thread_id)


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

    def _ensure_analysis_run(self, state: ProductWorkflowState) -> str | None:
        if state.analysis_run_id:
            return state.analysis_run_id
        if not state.startup_id:
            return None
        from src.repositories.product import ProductRepository

        repo = ProductRepository(self.session)
        run = repo.create_analysis_run(
            startup_id=state.startup_id,
            input_snapshot={},
            pipeline_version="orchestration_graph+v1",
            corpus_version=None,
            config_snapshot={},
        )
        self.session.flush()
        return run.id

    def run_workflow(self, state: ProductWorkflowState) -> ProductWorkflowState:
        analysis_run_id = self._ensure_analysis_run(state)
        if analysis_run_id:
            state.analysis_run_id = analysis_run_id

        graph = build_workflow_graph(checkpointer=None)
        if graph is None:
            state.error_message = (
                "LangGraph is not available. "
                "It is required to build the workflow graph."
            )
            self.repo.fail_workflow(
                state.workflow_id,
                error_message=state.error_message,
                state_json=self._dump_state(state),
            )
            return state

        return self._run_with_langgraph(state, graph)

    def _run_with_langgraph(
        self,
        state: ProductWorkflowState,
        graph: Any,
    ) -> ProductWorkflowState:
        self.repo.update_workflow_status(
            state.workflow_id,
            status=WorkflowStatus.RUNNING,
            current_node="",
            state_json=self._dump_state(state),
        )

        thread_id: str = state.analysis_run_id or state.workflow_id
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}

        input_data: dict[str, Any] = state.model_dump()

        token = session_var.set(self.session)
        try:
            result = graph.invoke(input_data, config)
        except NodeExecutionError as exc:
            session_var.reset(token)
            state.current_node = exc.node_name
            state.failed_nodes.append(exc.node_name)
            state.error_message = exc.error_message
            self.repo.fail_workflow(
                state.workflow_id,
                error_message=exc.error_message or f"Node failed: {exc.node_name}",
                state_json=self._dump_state(state),
            )
            return state

        session_var.reset(token)

        if isinstance(result, dict) and "__interrupt__" in result:
            return self._handle_interrupt(state, result, thread_id)

        self._finalize_workflow(state, result)
        return state

    def _handle_interrupt(
        self,
        state: ProductWorkflowState,
        result: dict[str, Any],
        thread_id: str,
    ) -> ProductWorkflowState:
        state_json: dict[str, Any] = self._dump_state(state)
        state_json.setdefault("metadata_json", {})["_langgraph_thread_id"] = thread_id

        interrupts = result.get("__interrupt__", [])
        if interrupts and hasattr(interrupts[0], "value"):
            state_json["review_payload"] = interrupts[0].value
            state_json["review_required"] = True

        self.repo.update_workflow_status(
            state.workflow_id,
            status=WorkflowStatus.AWAITING_REVIEW,
            current_node="needs_review",
            state_json=state_json,
        )
        state.status = WorkflowStatus.AWAITING_REVIEW
        return state

    def _finalize_workflow(
        self,
        state: ProductWorkflowState,
        result: Any,
    ) -> None:
        if isinstance(result, ProductWorkflowState):
            state = result
        elif isinstance(result, dict):
            for key, value in result.items():
                if hasattr(state, key):
                    setattr(state, key, value)

        state_json: dict[str, Any] = self._dump_state(state)
        if isinstance(result, dict):
            for key in ("review_payload", "review_decision", "review_required"):
                if key in result:
                    state_json[key] = result[key]

        if state.degraded_nodes:
            self.repo.degrade_workflow(
                state.workflow_id,
                degraded_reason=f"Degraded nodes: {', '.join(state.degraded_nodes)}",
                state_json=state_json,
            )
        else:
            self.repo.complete_workflow(state.workflow_id, state_json=state_json)

    def resume_workflow(
        self,
        state: ProductWorkflowState,
        *,
        decision: str,
        notes: str = "",
        reviewed_by: str = "",
    ) -> ProductWorkflowState:
        thread_id: str | None = state.metadata_json.get("_langgraph_thread_id")
        if not thread_id:
            msg = f"No checkpoint thread_id found for workflow {state.workflow_id}"
            raise RuntimeError(msg)

        checkpointer = _get_cached_checkpointer(thread_id)
        if checkpointer is None:
            msg = (
                f"Cannot resume workflow {state.workflow_id} — "
                f"no cached checkpointer for thread_id {thread_id}. "
                "Ensure the initial run completed with a checkpointer."
            )
            raise RuntimeError(msg)

        graph = build_workflow_graph(checkpointer=checkpointer)
        if graph is None:
            msg = "Cannot resume — LangGraph workflow graph is not available"
            raise RuntimeError(msg)

        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}

        self.repo.update_workflow_status(
            state.workflow_id,
            status=WorkflowStatus.RUNNING,
            current_node="needs_review",
            state_json=self._dump_state(state),
        )

        if not _LANGGRAPH_COMMAND_AVAILABLE:
            raise RuntimeError("langgraph.types.Command is not available")

        token = session_var.set(self.session)
        try:
            result = graph.invoke(
                Command(
                    resume=decision,
                    update={
                        "review_decision": decision,
                        "review_notes": notes,
                        "reviewed_by": reviewed_by,
                    },
                ),
                config,
            )
        except NodeExecutionError as exc:
            session_var.reset(token)
            state.current_node = exc.node_name
            state.failed_nodes.append(exc.node_name)
            state.error_message = exc.error_message
            self.repo.fail_workflow(
                state.workflow_id,
                error_message=exc.error_message or f"Node failed: {exc.node_name}",
                state_json=self._dump_state(state),
            )
            return state

        session_var.reset(token)

        if (
            decision == "approve"
            and isinstance(result, dict)
            and result.get("review_decision") == "approve"
            and "__interrupt__" in result
        ):
            result = dict(result)
            result.pop("__interrupt__", None)
            result["status"] = "human_review_approved"
            result["review_required"] = False

        if isinstance(result, dict) and "__interrupt__" in result:
            return self._handle_interrupt(state, result, thread_id)

        self._finalize_workflow(state, result)
        return state


def create_runner(session: Session) -> WorkflowRunner:
    return WorkflowRunner(session)
