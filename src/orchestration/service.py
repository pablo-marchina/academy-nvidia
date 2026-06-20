from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from src.orchestration.runner import WorkflowRunner, _has_langgraph
from src.orchestration.state import ProductWorkflowState
from src.repositories.workflow import WorkflowRepository


class WorkflowOrchestrationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = WorkflowRepository(session)

    def create_and_run_workflow(
        self,
        *,
        startup_id: str | None = None,
        discovery_candidate_id: str | None = None,
        analysis_run_id: str | None = None,
        use_rag: bool = False,
        graph_version: str = "1.0",
    ) -> ProductWorkflowState:
        has_lg = _has_langgraph()

        workflow_run = self.repo.create_workflow_run(
            startup_id=startup_id,
            discovery_candidate_id=discovery_candidate_id,
            analysis_run_id=analysis_run_id,
            graph_version=graph_version,
            state_json={
                "startup_id": startup_id,
                "discovery_candidate_id": discovery_candidate_id,
                "analysis_run_id": analysis_run_id,
            },
        )

        state = ProductWorkflowState(
            workflow_id=workflow_run.id,
            startup_id=startup_id,
            discovery_candidate_id=discovery_candidate_id,
            analysis_run_id=analysis_run_id,
            metadata_json={
                "_rag_available": use_rag,
                "_langgraph_available": has_lg,
            },
        )

        runner = WorkflowRunner(self.session)
        final_state = runner.run_workflow(state)
        self.session.commit()
        return final_state

    def get_workflow_state(self, workflow_id: str) -> ProductWorkflowState | None:
        run = self.repo.get_workflow_run(workflow_id)
        if run is None:
            return None
        state_data = dict(run.state_json or {})
        state_data["workflow_id"] = run.id
        state_data["startup_id"] = run.startup_id
        state_data["current_node"] = run.current_node
        return ProductWorkflowState(**state_data)

    def list_workflows(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        status: str | None = None,
        startup_id: str | None = None,
    ) -> list[dict[str, Any]]:
        runs = self.repo.list_workflow_runs(
            offset=offset,
            limit=limit,
            status=status,
            startup_id=startup_id,
        )
        return [
            {
                "id": r.id,
                "startup_id": r.startup_id,
                "discovery_candidate_id": r.discovery_candidate_id,
                "analysis_run_id": r.analysis_run_id,
                "status": r.status,
                "current_node": r.current_node,
                "graph_version": r.graph_version,
                "error_message": r.error_message,
                "degraded_reason": r.degraded_reason,
                "started_at": r.started_at,
                "completed_at": r.completed_at,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in runs
        ]

    def get_review_payload(self, workflow_id: str) -> dict[str, Any] | None:
        run = self.repo.get_workflow_run(workflow_id)
        if run is None:
            return None
        state: dict[str, Any] = run.state_json or {}
        return state.get("review_payload")

    def submit_review(
        self,
        workflow_id: str,
        *,
        decision: str,
        reviewer: str,
        notes: str,
        resume: bool = False,
    ) -> dict[str, Any]:
        run = self.repo.get_workflow_run(workflow_id)
        if run is None:
            raise LookupError(f"Workflow run not found: {workflow_id}")

        state_data: dict[str, Any] = dict(run.state_json or {})
        now = datetime.now(UTC).isoformat()
        state_data.update(
            {
                "review_decision": decision,
                "reviewer": reviewer,
                "reviewed_by": reviewer,
                "review_notes": notes,
                "reviewed_at": now,
                "review_required": False,
            }
        )
        run.state_json = state_data
        self.session.flush()

        if not resume:
            self.session.commit()
            return {
                "workflow_id": workflow_id,
                "decision": decision,
                "reviewer": reviewer,
                "notes": notes,
                "created_at": now,
            }

        state_data["workflow_id"] = run.id
        state_data["startup_id"] = run.startup_id
        state_data["current_node"] = run.current_node
        workflow_state = ProductWorkflowState(**state_data)

        runner = WorkflowRunner(self.session)
        runner.resume_workflow(workflow_state, decision=decision, notes=notes, reviewed_by=reviewer)
        self.session.commit()

        return {
            "workflow_id": workflow_id,
            "decision": decision,
            "reviewer": reviewer,
            "notes": notes,
            "created_at": now,
        }
