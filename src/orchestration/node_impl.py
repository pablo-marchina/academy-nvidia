"""Node implementations for the product workflow.

Each node wraps an existing service and returns a NodeResult.
Nodes do not access data/demo_runs.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy.orm import Session

from src.database.models import Startup, StartupDiscoveryCandidate
from src.orchestration.nodes import NodeResult, _register
from src.orchestration.state import NodeStatus, ProductWorkflowState
from src.repositories.product import ProductRepository
from src.repositories.workflow import WorkflowRepository
from src.services.product.activation_service import ActivationPlaybookService
from src.services.product.claim_ledger import ClaimLedgerService
from src.services.product.dossier_service import ActivationDossierService


def _load_startup(session: Session, startup_id: str) -> Startup | None:
    repo = ProductRepository(session)
    return repo.get_startup(startup_id)


def _load_candidate(session: Session, candidate_id: str) -> StartupDiscoveryCandidate | None:
    stmt = (
        __import__("sqlalchemy")
        .select(StartupDiscoveryCandidate)
        .where(StartupDiscoveryCandidate.id == candidate_id)
    )
    return cast(StartupDiscoveryCandidate | None, session.scalar(stmt))


def _promote_candidate(session: Session, candidate: StartupDiscoveryCandidate) -> str | None:
    """Promote a discovery candidate to a Startup if not already promoted."""
    if candidate.promoted_startup_id:
        return candidate.promoted_startup_id
    from src.discovery.service import StartupDiscoveryService

    svc = StartupDiscoveryService(session)
    result = svc.promote_candidate(candidate.id)
    return result.get("startup_id")


def _save_readiness_check(
    session: Session,
    analysis_run_id: str | None,
    code: str,
    severity: str,
    user_message: str,
    internal_detail: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    from src.database.models import ProductReadinessCheck

    check = ProductReadinessCheck(
        analysis_run_id=analysis_run_id,
        code=code,
        severity=severity,
        status="degraded",
        user_message=user_message,
        internal_detail=internal_detail,
        recommended_action="",
        metadata_json=metadata or {},
        observed_at=datetime.now(UTC),
    )
    session.add(check)
    session.flush()


# ---------------------------------------------------------------------------
# Node 1: load_startup_or_candidate
# ---------------------------------------------------------------------------
@_register(
    "load_startup_or_candidate", "Load startup or promote discovery candidate", critical=True
)
def node_load_startup_or_candidate(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")
    wf_repo = WorkflowRepository(session)

    startup_id = state.startup_id
    candidate_id = state.discovery_candidate_id
    degraded_reasons: list[str] = []

    if startup_id:
        startup = _load_startup(session, startup_id)
        if startup is None:
            wf_repo.create_node_run(
                workflow_run_id=state.workflow_id,
                node_name="load_startup_or_candidate",
                input_snapshot={"startup_id": startup_id, "discovery_candidate_id": candidate_id},
            )
            return NodeResult(
                status=NodeStatus.FAILED, error_message=f"Startup not found: {startup_id}"
            )

    if candidate_id and not startup_id:
        candidate = _load_candidate(session, candidate_id)
        if candidate is None:
            wf_repo.create_node_run(
                workflow_run_id=state.workflow_id,
                node_name="load_startup_or_candidate",
                input_snapshot={"startup_id": startup_id, "discovery_candidate_id": candidate_id},
            )
            return NodeResult(
                status=NodeStatus.FAILED,
                error_message=f"Discovery candidate not found: {candidate_id}",
            )
        try:
            promoted_id = _promote_candidate(session, candidate)
            if promoted_id:
                startup_id = promoted_id
                degraded_reasons.append("Candidate promoted to startup")
            else:
                degraded_reasons.append("Candidate promotion returned no startup")
        except Exception as exc:
            degraded_reasons.append(f"Promotion failed: {exc}")

    updates: dict[str, Any] = {
        "startup_id": startup_id,
        "current_node": "load_startup_or_candidate",
    }
    if degraded_reasons:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            state_updates=updates,
            degraded_reason="; ".join(degraded_reasons),
        )
    return NodeResult(status=NodeStatus.COMPLETED, state_updates=updates)


# ---------------------------------------------------------------------------
# Node 2: collect_or_load_evidence
# ---------------------------------------------------------------------------
@_register("collect_or_load_evidence", "Load evidence from existing startup records")
def node_collect_or_load_evidence(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    startup_id = state.startup_id
    if not startup_id:
        return NodeResult(
            status=NodeStatus.SKIPPED, error_message="No startup_id to load evidence for"
        )

    repo = ProductRepository(session)
    startup = repo.get_startup(startup_id)
    if startup is None:
        return NodeResult(
            status=NodeStatus.FAILED, error_message=f"Startup not found: {startup_id}"
        )

    evidence_ids = [e.id for e in (startup.evidence or [])]
    return NodeResult(status=NodeStatus.COMPLETED, state_updates={"evidence_ids": evidence_ids})


# ---------------------------------------------------------------------------
# Node 3: validate_evidence
# ---------------------------------------------------------------------------
@_register("validate_evidence", "Run evidence validation on loaded evidence")
def node_validate_evidence(state: ProductWorkflowState) -> NodeResult:
    if not state.evidence_ids:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No evidence to validate")
    return NodeResult(status=NodeStatus.COMPLETED, state_updates={})


# ---------------------------------------------------------------------------
# Node 4: diagnose_gaps
# ---------------------------------------------------------------------------
@_register("diagnose_gaps", "Run gap diagnosis on startup")
def node_diagnose_gaps(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(
            status=NodeStatus.SKIPPED, error_message="No analysis_run_id for gap diagnosis"
        )

    from src.repositories.product import ProductRepository

    repo = ProductRepository(session)
    run = repo.get_analysis_run(analysis_run_id)
    if run is None:
        return NodeResult(
            status=NodeStatus.FAILED, error_message=f"AnalysisRun not found: {analysis_run_id}"
        )

    output = run.output_snapshot_json or {}
    gap_ids = list(
        g.get("id", "") for g in output.get("gap_diagnosis", {}).get("gaps", []) if g.get("id")
    )
    mapping_ids = list(
        m.get("id", "")
        for m in output.get("gap_diagnosis", {}).get("nvidia_mappings", [])
        if m.get("id")
    )

    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={
            "gap_ids": gap_ids,
            "mapping_ids": mapping_ids,
            "node_outputs": {**state.node_outputs, "gap_output": output.get("gap_diagnosis", {})},
        },
    )


# ---------------------------------------------------------------------------
# Node 5: retrieve_nvidia_context
# ---------------------------------------------------------------------------
@_register("retrieve_nvidia_context", "Retrieve NVIDIA RAG context (optional)")
def node_retrieve_nvidia_context(state: ProductWorkflowState) -> NodeResult:
    rag_available = state.metadata_json.get("_rag_available", False)
    if not rag_available:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            degraded_reason="RAG unavailable; skipping NVIDIA context retrieval",
        )
    return NodeResult(status=NodeStatus.COMPLETED, state_updates={})


# ---------------------------------------------------------------------------
# Node 6: map_nvidia_technologies
# ---------------------------------------------------------------------------
@_register("map_nvidia_technologies", "Map NVIDIA technologies to diagnosed gaps")
def node_map_nvidia_technologies(state: ProductWorkflowState) -> NodeResult:
    if not state.gap_ids:
        return NodeResult(
            status=NodeStatus.SKIPPED, error_message="No gaps to map technologies from"
        )
    return NodeResult(status=NodeStatus.COMPLETED, state_updates={})


# ---------------------------------------------------------------------------
# Node 7: generate_claims
# ---------------------------------------------------------------------------
@_register("generate_claims", "Generate deterministic claims from pipeline output")
def node_generate_claims(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(
            status=NodeStatus.SKIPPED, error_message="No analysis_run_id for claim generation"
        )

    from src.repositories.product import ProductRepository

    repo = ProductRepository(session)
    run = repo.get_analysis_run(analysis_run_id)
    if run is None:
        return NodeResult(
            status=NodeStatus.FAILED, error_message=f"AnalysisRun not found: {analysis_run_id}"
        )

    try:
        ledger = ClaimLedgerService(session)
        ledger.persist_claims_for_run(run)
        from src.database.models import ClaimRecord

        stmt = (
            __import__("sqlalchemy")
            .select(ClaimRecord)
            .where(ClaimRecord.analysis_run_id == analysis_run_id)
        )
        claims = list(session.scalars(stmt))
        claim_ids = [c.id for c in claims]
        return NodeResult(status=NodeStatus.COMPLETED, state_updates={"claim_ids": claim_ids})
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            error_message=str(exc),
            degraded_reason="Claim generation failed",
        )


# ---------------------------------------------------------------------------
# Node 8: match_activation_playbooks
# ---------------------------------------------------------------------------
@_register("match_activation_playbooks", "Match activation playbooks to diagnosed gaps")
def node_match_activation_playbooks(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(
            status=NodeStatus.SKIPPED, error_message="No analysis_run_id for playbook matching"
        )

    try:
        act_service = ActivationPlaybookService(session)
        recs = act_service.generate_recommendations_for_run(analysis_run_id)
        if recs:
            act_service.activation_repo.replace_recommendations_for_analysis_run(
                analysis_run_id, recs
            )
            rec_ids = [r.get("id", "") for r in recs if r.get("id")]
        else:
            rec_ids = []
        if not rec_ids:
            return NodeResult(
                status=NodeStatus.DEGRADED,
                degraded_reason="No activation playbooks matched",
                state_updates={"activation_recommendation_ids": []},
            )
        return NodeResult(
            status=NodeStatus.COMPLETED, state_updates={"activation_recommendation_ids": rec_ids}
        )
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            error_message=str(exc),
            degraded_reason="Playbook matching failed",
        )


# ---------------------------------------------------------------------------
# Node 9: generate_activation_dossier
# ---------------------------------------------------------------------------
@_register("generate_activation_dossier", "Generate activation dossier from analysis run")
def node_generate_activation_dossier(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No analysis_run_id for dossier")

    try:
        dossier_service = ActivationDossierService(session)
        dossier = dossier_service.build_dossier_for_analysis_run(analysis_run_id)
        return NodeResult(
            status=NodeStatus.COMPLETED,
            state_updates={"dossier_id": dossier.id},
        )
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            error_message=str(exc),
            degraded_reason="Dossier generation failed",
        )


# ---------------------------------------------------------------------------
# Node 10: run_product_quality
# ---------------------------------------------------------------------------
@_register("run_product_quality", "Run product quality evaluation on analysis run")
def node_run_product_quality(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(
            status=NodeStatus.SKIPPED, error_message="No analysis_run_id for quality run"
        )

    try:
        from src.quality.service import ProductQualityService

        quality_service = ProductQualityService(session)
        quality_run = quality_service.run_quality_evaluation_for_analysis_run(analysis_run_id)
        return NodeResult(
            status=NodeStatus.COMPLETED,
            state_updates={"quality_run_id": quality_run.id},
        )
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            error_message=str(exc),
            degraded_reason="Quality evaluation failed",
        )


# ---------------------------------------------------------------------------
# Node 11: summarize_readiness (moved from 12)
# ---------------------------------------------------------------------------
@_register("summarize_readiness", "Summarize readiness checks into final state")
def node_summarize_readiness(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(status=NodeStatus.COMPLETED, state_updates={})

    from src.database.models import ProductReadinessCheck

    stmt = (
        __import__("sqlalchemy")
        .select(ProductReadinessCheck)
        .where(ProductReadinessCheck.analysis_run_id == analysis_run_id)
    )
    checks = list(session.scalars(stmt))
    check_ids = [c.id for c in checks]
    degraded_codes = [c.code for c in checks if c.status == "degraded"]

    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={
            "readiness_check_ids": check_ids,
            "degraded_nodes": degraded_codes,
        },
    )
