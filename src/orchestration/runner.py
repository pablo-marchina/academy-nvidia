from __future__ import annotations

from typing import Any, cast

from sqlalchemy.orm import Session

from src.orchestration.graph import NodeExecutionError, build_workflow_graph
from src.orchestration.nodes import WORKFLOW_NODES, NodeResult
from src.orchestration.state import NodeStatus, ProductWorkflowState, WorkflowStatus
from src.repositories.workflow import WorkflowRepository

_MAX_RETRY_DEFAULT = 1

try:
    from langgraph.types import Command  # noqa: I001

    _LANGGRAPH_COMMAND_AVAILABLE = True
except ImportError:
    _LANGGRAPH_COMMAND_AVAILABLE = False

# Module-level singleton for the Postgres checkpointer (process-shared).
_POSTGRES_CHECKPOINTER: Any | None = None


def _build_postgres_checkpointer() -> Any | None:
    """Build a PostgresSaver if the database is PostgreSQL, else None."""
    global _POSTGRES_CHECKPOINTER
    if _POSTGRES_CHECKPOINTER is not None:
        return _POSTGRES_CHECKPOINTER
    try:
        from langgraph.checkpoint.postgres import PostgresSaver  # type: ignore[import-not-found]  # noqa: I001
        from src.database.session import get_product_db_url

        url = get_product_db_url()
        if url and url.startswith("postgresql"):
            import psycopg  # type: ignore[import-not-found]  # noqa: I001
            from psycopg.rows import dict_row  # type: ignore[import-not-found]  # noqa: I001

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
        from langgraph.checkpoint.memory import MemorySaver  # noqa: I001

        return MemorySaver()
    except ImportError:
        return None


def _try_build_agent_graph(
    *, checkpointer: Any = None, analysis_repository: Any = None
) -> Any | None:
    try:
        from src.agents.graph import build_startup_radar_graph  # noqa: I001

        rag_service = _try_build_rag_service()
        return build_startup_radar_graph(
            checkpointer=checkpointer,
            analysis_repository=analysis_repository,
            rag_service=rag_service,
        )
    except ImportError:
        return None


def _try_build_rag_service() -> Any | None:
    """Build a Qdrant-backed RagService if RAG_VECTOR_BACKEND=qdrant."""
    import os

    if os.environ.get("RAG_VECTOR_BACKEND", "").lower() != "qdrant":
        return None
    try:
        from src.rag.rag_service_factory import build_rag_service  # noqa: I001

        return build_rag_service()
    except Exception:
        return None


# Module-level cache for MemorySaver checkpointers keyed by thread_id.
# Ensures the same checkpointer instance is reused across run and resume calls,
# preserving checkpoint state without a database-backed checkpointer.
_CHECKPOINTER_CACHE: dict[str, Any] = {}


def _cache_checkpointer(thread_id: str, checkpointer: Any) -> None:
    _CHECKPOINTER_CACHE[thread_id] = checkpointer


def _get_cached_checkpointer(thread_id: str) -> Any | None:
    return _CHECKPOINTER_CACHE.get(thread_id)


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
            pipeline_version="agent_graph",
            corpus_version=None,
            config_snapshot={},
        )
        self.session.flush()
        return run.id

    def run_workflow(
        self,
        state: ProductWorkflowState,
        *,
        max_retry: int = _MAX_RETRY_DEFAULT,
    ) -> ProductWorkflowState:
        state.metadata_json["_session"] = self.session

        analysis_run_id = self._ensure_analysis_run(state)
        if analysis_run_id:
            state.analysis_run_id = analysis_run_id
            from src.services.product.workflow_persister import make_workflow_persister

            persister = make_workflow_persister(self.session)
        else:
            persister = None

        thread_id: str = state.analysis_run_id or state.workflow_id
        checkpointer = _get_cached_checkpointer(thread_id)
        if checkpointer is None:
            checkpointer = _build_checkpointer()
            if checkpointer is not None:
                _cache_checkpointer(thread_id, checkpointer)

        agent_graph = _try_build_agent_graph(
            checkpointer=checkpointer,
            analysis_repository=persister,
        )
        if agent_graph is not None:
            return self._run_with_langgraph(state, agent_graph, use_agent_graph=True)

        graph = build_workflow_graph()
        if graph is not None:
            return self._run_with_langgraph(state, graph, use_agent_graph=False)

        return self._run_sequential(state, max_retry=max_retry)

    def _run_with_langgraph(
        self,
        state: ProductWorkflowState,
        graph: Any,
        *,
        use_agent_graph: bool = False,
    ) -> ProductWorkflowState:
        self.repo.update_workflow_status(
            state.workflow_id,
            status=WorkflowStatus.RUNNING,
            current_node="",
            state_json=self._dump_state(state),
        )

        thread_id: str = state.analysis_run_id or state.workflow_id
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}

        _saved_session = state.metadata_json.pop("_session", None)
        try:
            input_data: dict[str, Any] = state.model_dump()
        finally:
            if _saved_session is not None:
                state.metadata_json["_session"] = _saved_session

        if use_agent_graph:
            input_data.setdefault("run_id", state.workflow_id)
            input_data.setdefault("executed_nodes", list(state.completed_nodes))
            input_data.setdefault("thread_id", thread_id)

        try:
            result = graph.invoke(input_data, config)
        except NodeExecutionError as exc:
            state.current_node = exc.node_name
            state.failed_nodes.append(exc.node_name)
            state.error_message = exc.error_message
            self.repo.fail_workflow(
                state.workflow_id,
                error_message=exc.error_message or f"Node failed: {exc.node_name}",
                state_json=self._dump_state(state),
            )
            state.metadata_json.pop("_session", None)
            return state

        if isinstance(result, dict) and "__interrupt__" in result:
            return self._handle_interrupt(state, result, thread_id)

        self._finalize_workflow(state, result)
        state.metadata_json.pop("_session", None)
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
            state = result  # type: ignore[unreachable]
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
        from src.services.product.workflow_persister import make_workflow_persister

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

        persister = make_workflow_persister(self.session)
        graph = _try_build_agent_graph(
            checkpointer=checkpointer,
            analysis_repository=persister,
        )
        if graph is None:
            msg = "Cannot resume — agent LangGraph graph is not available"
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
            state.current_node = exc.node_name
            state.failed_nodes.append(exc.node_name)
            state.error_message = exc.error_message
            self.repo.fail_workflow(
                state.workflow_id,
                error_message=exc.error_message or f"Node failed: {exc.node_name}",
                state_json=self._dump_state(state),
            )
            state.metadata_json.pop("_session", None)
            return state

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
        state.metadata_json.pop("_session", None)
        return state

    def _run_sequential(
        self,
        state: ProductWorkflowState,
        *,
        max_retry: int = _MAX_RETRY_DEFAULT,
    ) -> ProductWorkflowState:
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
