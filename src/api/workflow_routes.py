from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.product_schemas import (
    ProductWorkflowNodeRunRead,
    ProductWorkflowRunCreate,
    ProductWorkflowRunListResponse,
    ProductWorkflowRunRead,
)
from src.database.models import WorkflowNodeRun, WorkflowRun
from src.database.session import get_db_session
from src.orchestration.runner import _has_langgraph
from src.orchestration.service import WorkflowOrchestrationService
from src.repositories.workflow import WorkflowRepository

router = APIRouter(tags=["workflows"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.post(
    "/workflows/product-runs",
    response_model=ProductWorkflowRunRead,
    status_code=201,
)
def create_product_workflow_run(
    body: ProductWorkflowRunCreate,
    session: DbSession,
) -> ProductWorkflowRunRead:
    svc = WorkflowOrchestrationService(session)
    state = svc.create_and_run_workflow(
        startup_id=body.startup_id,
        discovery_candidate_id=body.discovery_candidate_id,
        analysis_run_id=body.analysis_run_id,
        use_rag=body.use_rag,
    )
    run = svc.repo.get_workflow_run(state.workflow_id)
    if run is None:
        raise HTTPException(status_code=500, detail="Workflow run not found after creation")
    node_runs = svc.repo.list_node_runs(state.workflow_id)
    return _workflow_run_read(run, node_runs)


@router.get(
    "/workflows/product-runs",
    response_model=ProductWorkflowRunListResponse,
)
def list_product_workflow_runs(
    session: DbSession,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    startup_id: str | None = Query(None),
) -> ProductWorkflowRunListResponse:
    svc = WorkflowOrchestrationService(session)
    items = svc.list_workflows(offset=offset, limit=limit, status=status, startup_id=startup_id)
    return ProductWorkflowRunListResponse(items=items, total=len(items), offset=offset, limit=limit)


@router.get(
    "/workflows/product-runs/{workflow_id}",
    response_model=ProductWorkflowRunRead,
)
def get_product_workflow_run(
    workflow_id: str,
    session: DbSession,
) -> ProductWorkflowRunRead:
    repo = WorkflowRepository(session)
    run = repo.get_workflow_run(workflow_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Workflow run not found: {workflow_id}")
    node_runs = repo.list_node_runs(workflow_id)
    return _workflow_run_read(run, node_runs)


@router.get(
    "/workflows/product-runs/{workflow_id}/nodes",
    response_model=list[ProductWorkflowNodeRunRead],
)
def list_workflow_node_runs(
    workflow_id: str,
    session: DbSession,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[ProductWorkflowNodeRunRead]:
    repo = WorkflowRepository(session)
    run = repo.get_workflow_run(workflow_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Workflow run not found: {workflow_id}")
    node_runs = repo.list_node_runs(workflow_id, offset=offset, limit=limit)
    return [
        ProductWorkflowNodeRunRead(
            id=nr.id,
            workflow_run_id=nr.workflow_run_id,
            node_name=nr.node_name,
            status=nr.status,
            started_at=nr.started_at,
            completed_at=nr.completed_at,
            error_message=nr.error_message,
            retry_count=nr.retry_count,
            created_at=nr.created_at,
        )
        for nr in node_runs
    ]


@router.get(
    "/analysis-runs/{analysis_run_id}/workflow",
    response_model=ProductWorkflowRunRead | None,
)
def get_workflow_for_analysis_run(
    analysis_run_id: str,
    session: DbSession,
) -> ProductWorkflowRunRead | None:
    repo = WorkflowRepository(session)
    run = repo.get_workflow_for_analysis_run(analysis_run_id)
    if run is None:
        raise HTTPException(
            status_code=404, detail=f"No workflow found for analysis run: {analysis_run_id}"
        )
    node_runs = repo.list_node_runs(run.id)
    return _workflow_run_read(run, node_runs)


@router.get("/workflows/langgraph-status")
def get_langgraph_status() -> dict[str, bool]:
    return {"langgraph_available": _has_langgraph()}


def _workflow_run_read(
    run: WorkflowRun,
    node_runs: list[WorkflowNodeRun],
) -> ProductWorkflowRunRead:
    return ProductWorkflowRunRead(
        id=run.id,
        startup_id=run.startup_id,
        discovery_candidate_id=run.discovery_candidate_id,
        analysis_run_id=run.analysis_run_id,
        status=run.status,
        current_node=run.current_node,
        graph_version=run.graph_version,
        error_message=run.error_message,
        degraded_reason=run.degraded_reason,
        state=run.state_json or {},
        nodes=[
            ProductWorkflowNodeRunRead(
                id=nr.id,
                workflow_run_id=nr.workflow_run_id,
                node_name=nr.node_name,
                status=nr.status,
                started_at=nr.started_at,
                completed_at=nr.completed_at,
                error_message=nr.error_message,
                retry_count=nr.retry_count,
                created_at=nr.created_at,
            )
            for nr in node_runs
        ],
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )
