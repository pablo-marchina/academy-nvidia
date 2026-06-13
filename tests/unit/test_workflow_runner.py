from __future__ import annotations

from pathlib import Path

import pytest

import src.orchestration.node_impl  # noqa: F401 - populate WORKFLOW_NODES
from src.database.session import configure_product_database, reset_product_database_runtime
from src.orchestration.nodes import WORKFLOW_NODES
from src.orchestration.runner import WorkflowRunner, _has_langgraph, _is_retryable, create_runner
from src.orchestration.state import ProductWorkflowState
from src.repositories.workflow import WorkflowRepository


@pytest.fixture
def session(tmp_path: Path):
    runtime = configure_product_database(f"sqlite:///{(tmp_path / 'runner.db').as_posix()}")
    sess = runtime.session_factory()
    yield sess
    sess.close()
    reset_product_database_runtime()


@pytest.fixture
def runner(session) -> WorkflowRunner:
    return create_runner(session)


def test_workflow_nodes_are_registered() -> None:
    assert len(WORKFLOW_NODES) >= 11
    node_names = {n.name for n in WORKFLOW_NODES}
    expected = {
        "load_startup_or_candidate",
        "collect_or_load_evidence",
        "validate_evidence",
        "diagnose_gaps",
        "retrieve_nvidia_context",
        "map_nvidia_technologies",
        "generate_claims",
        "match_activation_playbooks",
        "generate_activation_dossier",
        "run_product_quality",
        "summarize_readiness",
    }
    assert node_names == expected


def test_workflow_nodes_have_required_fields() -> None:
    for node in WORKFLOW_NODES:
        assert node.name
        assert node.description
        assert node.critical is not None


def test_runner_runs_full_workflow_with_missing_startup(runner: WorkflowRunner, session) -> None:
    repo = WorkflowRepository(session)
    run = repo.create_workflow_run()
    session.commit()
    state = ProductWorkflowState(
        workflow_id=run.id,
        current_node="load_startup_or_candidate",
    )
    result_state = runner.run_workflow(state)
    assert result_state.workflow_id == run.id
    assert len(result_state.completed_nodes) == 11
    assert "load_startup_or_candidate" in result_state.completed_nodes
    assert result_state.error_message is None


def test_runner_has_langgraph_detection() -> None:
    result = _has_langgraph()
    assert isinstance(result, bool)


def test_retryable_error_detection() -> None:
    assert _is_retryable("RuntimeError: timeout")
    assert _is_retryable("Exception: generic error")
    assert not _is_retryable("ValueError: bad input")
    assert not _is_retryable("TypeError: wrong type")
    assert not _is_retryable("LookupError: not found")
    assert not _is_retryable("AssertionError: assert")
    assert _is_retryable("")
    assert not _is_retryable("ValueError")


def test_runner_executes_with_session(runner: WorkflowRunner, session) -> None:
    repo = WorkflowRepository(session)
    run = repo.create_workflow_run(startup_id="s-1")
    session.commit()
    state = ProductWorkflowState(
        workflow_id=run.id,
        startup_id="s-1",
        current_node="load_startup_or_candidate",
    )
    result = runner.run_workflow(state)
    assert result is not None
    assert isinstance(result, ProductWorkflowState)
