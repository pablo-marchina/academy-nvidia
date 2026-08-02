from __future__ import annotations

from src.database.session import configure_product_database, reset_product_database_runtime
from src.orchestration.service import WorkflowOrchestrationService
from src.orchestration.state import WorkflowStatus
from src.repositories.workflow import WorkflowRepository


def test_enqueue_claim_and_attach_analysis_workflow(monkeypatch) -> None:
    monkeypatch.setenv("APP_MODE", "test")
    reset_product_database_runtime()
    runtime = configure_product_database("sqlite:///:memory:")

    with runtime.session_factory() as session:
        service = WorkflowOrchestrationService(session)
        queued = service.enqueue_workflow(startup_id="startup-test", use_rag=True)
        assert queued.status == WorkflowStatus.QUEUED
        workflow_id = queued.id

    with runtime.session_factory() as session:
        repo = WorkflowRepository(session)
        claimed = repo.claim_next_queued_workflow()
        assert claimed is not None
        assert claimed.id == workflow_id
        assert claimed.status == WorkflowStatus.RUNNING
        attached = repo.attach_analysis_run(workflow_id, "analysis-test")
        assert attached is not None
        assert attached.analysis_run_id == "analysis-test"
        assert attached.state_json["analysis_run_id"] == "analysis-test"
        session.commit()

    with runtime.session_factory() as session:
        persisted = WorkflowRepository(session).get_workflow_run(workflow_id)
        assert persisted is not None
        assert persisted.analysis_run_id == "analysis-test"
        assert WorkflowRepository(session).claim_next_queued_workflow() is None

    reset_product_database_runtime()


def test_enqueue_requires_a_target(monkeypatch) -> None:
    monkeypatch.setenv("APP_MODE", "test")
    reset_product_database_runtime()
    runtime = configure_product_database("sqlite:///:memory:")

    with runtime.session_factory() as session:
        service = WorkflowOrchestrationService(session)
        try:
            service.enqueue_workflow(use_rag=True)
        except ValueError as exc:
            assert "required" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("enqueue_workflow should reject a targetless workflow")

    reset_product_database_runtime()
