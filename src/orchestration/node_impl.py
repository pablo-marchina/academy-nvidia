"""Node implementations for the product workflow.

Each node wraps an existing service and returns a NodeResult.
Single complete pipeline with 19 nodes.
"""

from __future__ import annotations

import os
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

LANGGRAPH_AVAILABLE: bool
try:
    from langgraph.types import interrupt

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


def _load_startup(session: Session, startup_id: str) -> Startup | None:
    repo = ProductRepository(session)
    return repo.get_startup(startup_id)


def _load_candidate(session: Session, candidate_id: str) -> StartupDiscoveryCandidate | None:
    stmt = (
        __import__("sqlalchemy").select(StartupDiscoveryCandidate).where(StartupDiscoveryCandidate.id == candidate_id)
    )
    return cast(StartupDiscoveryCandidate | None, session.scalar(stmt))


def _promote_candidate(session: Session, candidate: StartupDiscoveryCandidate) -> str | None:
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
@_register("load_startup_or_candidate", "Load startup or promote discovery candidate", critical=True)
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
            return NodeResult(status=NodeStatus.FAILED, error_message=f"Startup not found: {startup_id}")

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
# Node 2: plan_search
# ---------------------------------------------------------------------------
@_register("plan_search", "Build search plan from startup name")
def node_plan_search(state: ProductWorkflowState) -> NodeResult:
    startup_name = ""
    if state.startup_id:
        session = state.metadata_json.get("_session")
        if session:
            from src.repositories.product import ProductRepository

            repo = ProductRepository(session)
            startup = repo.get_startup(state.startup_id)
            if startup:
                startup_name = startup.name
    if not startup_name and state.metadata_json.get("startup_name"):
        startup_name = state.metadata_json["startup_name"]

    if not startup_name:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            degraded_reason="No startup name available for search planning",
            state_updates={"search_plan": []},
        )

    from src.agents.search_planner import build_search_plan

    plan = build_search_plan(startup_name)
    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={"search_plan": plan},
    )


# ---------------------------------------------------------------------------
# Node 3: collect_sources
# ---------------------------------------------------------------------------
@_register("collect_sources", "Collect evidence from governed sources", critical=False)
def node_collect_sources(state: ProductWorkflowState) -> NodeResult:
    if not state.search_plan:
        return NodeResult(
            status=NodeStatus.SKIPPED,
            error_message="No search plan to collect sources from",
        )

    startup_name = ""
    website_url = ""
    if state.startup_id:
        session = state.metadata_json.get("_session")
        if session:
            from src.repositories.product import ProductRepository

            repo = ProductRepository(session)
            startup = repo.get_startup(state.startup_id)
            if startup:
                startup_name = startup.name
                website_url = startup.website or ""

    run_id = state.analysis_run_id or state.workflow_id

    from src.agents.scraper_agent import collect_governed_sources

    evidence_items, errors = collect_governed_sources(
        startup_name=startup_name,
        website_url=website_url,
        run_id=run_id,
    )

    updates: dict = {"raw_evidence": evidence_items}
    if errors:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            degraded_reason=f"Source collection had errors: {'; '.join(errors[:5])}",
            state_updates=updates,
        )
    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates=updates,
    )


# ---------------------------------------------------------------------------
# Node 4: extract_profile
# ---------------------------------------------------------------------------
@_register("extract_profile", "Extract structured profile from raw evidence")
def node_extract_profile(state: ProductWorkflowState) -> NodeResult:
    raw_evidence = state.raw_evidence
    if not raw_evidence:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No raw evidence to extract profile from")

    startup_name = ""
    session = state.metadata_json.get("_session")
    if session and state.startup_id:
        from src.repositories.product import ProductRepository

        repo = ProductRepository(session)
        startup = repo.get_startup(state.startup_id)
        if startup:
            startup_name = startup.name

    from src.agents.extractor_agent import extract_profiles_from_candidates

    run_id = state.analysis_run_id or state.workflow_id
    result = extract_profiles_from_candidates(
        raw_evidence_candidates=raw_evidence,
        startup_name=startup_name,
        startup_id=state.startup_id,
        run_id=run_id,
    )

    errors = result.get("errors", [])
    return NodeResult(
        status=NodeStatus.COMPLETED if not errors else NodeStatus.DEGRADED,
        state_updates={
            "evidence_items": result.get("evidence_items", []),
            "startup_profile": result.get("startup_profile", {}),
        },
        degraded_reason="; ".join(errors[:5]) if errors else None,
    )


# ---------------------------------------------------------------------------
# Node 5: validate_evidence
# ---------------------------------------------------------------------------
@_register("validate_evidence", "Validate evidence items using deterministic rules")
def node_validate_evidence(state: ProductWorkflowState) -> NodeResult:
    evidence_items = state.evidence_items
    if not evidence_items:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No evidence to validate")

    from src.extraction.schemas import Evidence
    from src.validation.evidence_validator import validate_evidence_batch

    evidence_objs = []
    parse_errors = []
    for ev_dict in evidence_items:
        try:
            evidence_objs.append(Evidence.model_validate(ev_dict))
        except Exception as exc:
            parse_errors.append(str(exc))

    if not evidence_objs:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            degraded_reason="No valid evidence objects could be parsed",
        )

    validated = validate_evidence_batch(evidence_objs)
    return NodeResult(
        status=NodeStatus.COMPLETED if not parse_errors else NodeStatus.DEGRADED,
        state_updates={
            "validated_evidence": [v.model_dump(mode="json") for v in validated],
        },
        degraded_reason="; ".join(parse_errors[:5]) if parse_errors else None,
    )


# ---------------------------------------------------------------------------
# Node 6: score_startup
# ---------------------------------------------------------------------------
@_register("score_startup", "Score startup using probabilistic evidence-weighted scoring")
def node_score_startup(state: ProductWorkflowState) -> NodeResult:
    profile = state.startup_profile
    if not profile:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No startup profile to score")

    validated = state.node_outputs.get("validated_evidence", [])
    run_id = state.analysis_run_id or state.workflow_id

    from src.classification.ai_native_classifier import classify_ai_native
    from src.extraction.schemas import StartupProfile

    try:
        profile_obj = StartupProfile.model_validate(profile)
        classification = classify_ai_native(profile_obj)
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            state_updates={"scores": {"error": str(exc)}},
            degraded_reason=f"Classification failed: {exc}",
        )

    errors: list[str] = []

    features: list[dict[str, object]] = []
    evidence_ids_used: list[str] = []

    for ev in validated:
        ev_id = ev.get("id") or ev.get("evidence_id", "")
        if ev_id:
            evidence_ids_used.append(ev_id)
        source_reliability = float(ev.get("source_reliability", 0.5))
        relevance = float(ev.get("relevance", 0.5))
        features.append({
            "name": f"evidence_{ev_id or len(features)}",
            "value": (source_reliability + relevance) / 2,
            "weight": 1.0,
            "evidence_ids": (ev_id,) if ev_id else (),
        })

    classification_confidence = float(getattr(classification, "confidence", 0.5).value if hasattr(getattr(classification, "confidence", None), "value") else 0.5)
    features.append({
        "name": "ai_classification",
        "value": classification_confidence,
        "weight": 2.0,
        "evidence_ids": (),
    })

    from src.decisioning.evidence_weighted_scorer import WeightedFeature, score_features
    from src.decisioning.uncertainty_estimator import estimate_uncertainty
    from src.config.loader import ConfigLoaderService

    wf_list = [WeightedFeature(**f) for f in features]
    scores_result = score_features(wf_list)

    evidence_count = len(evidence_ids_used)
    uncertainty = estimate_uncertainty(
        evidence_count=evidence_count,
        source_diversity=max(1, len(set(ev.get("source", "") for ev in validated))),
    )

    cfg = ConfigLoaderService()
    scoring_cfg = cfg.scoring()
    section_scores: dict[str, float] = {}
    try:
        base = scores_result.get("score", 0.5)
        weights_map = {
            "defensibility": scoring_cfg.defensibility.model_dump() if hasattr(scoring_cfg, 'defensibility') else {},
            "inception_fit": scoring_cfg.inception_fit.model_dump() if hasattr(scoring_cfg, 'inception_fit') else {},
            "production_readiness": scoring_cfg.production_readiness.model_dump() if hasattr(scoring_cfg, 'production_readiness') else {},
            "opportunity": scoring_cfg.opportunity_score.model_dump() if hasattr(scoring_cfg, 'opportunity_score') else {},
        }
        for section, w in weights_map.items():
            section_scores[section] = round(base * sum(w.values()) / max(1, len(w)), 4)
    except Exception:
        section_scores = {"defensibility": 0.5, "inception_fit": 0.5, "production_readiness": 0.5, "opportunity": 0.5}

    scores = {
        "probabilistic_score": scores_result.get("score", 0.5),
        "confidence": scores_result.get("confidence", 0.5),
        "uncertainty": uncertainty,
        "evidence_count": evidence_count,
        "feature_count": len(features),
        "classification": classification.classification.value if hasattr(classification.classification, "value") else str(classification.classification),
        "classification_confidence": classification_confidence,
        "defensibility": section_scores.get("defensibility", 0.5),
        "inception_fit": section_scores.get("inception_fit", 0.5),
        "production_readiness": section_scores.get("production_readiness", 0.5),
        "sections": section_scores,
    }

    return NodeResult(
        status=NodeStatus.COMPLETED if not errors else NodeStatus.DEGRADED,
        state_updates={
            "scores": scores,
            "classification_result": classification.model_dump(mode="json"),
        },
        degraded_reason="; ".join(errors[:5]) if errors else None,
    )


# ---------------------------------------------------------------------------
# Node 7: diagnose_gaps
# ---------------------------------------------------------------------------
@_register("diagnose_gaps", "Run gap diagnosis on startup")
def node_diagnose_gaps(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No analysis_run_id for gap diagnosis")

    from src.repositories.product import ProductRepository

    repo = ProductRepository(session)
    run = repo.get_analysis_run(analysis_run_id)
    if run is None:
        return NodeResult(status=NodeStatus.FAILED, error_message=f"AnalysisRun not found: {analysis_run_id}")

    output = run.output_snapshot_json or {}
    gap_ids = list(g.get("id", "") for g in output.get("gap_diagnosis", {}).get("gaps", []) if g.get("id"))
    mapping_ids = list(
        m.get("id", "") for m in output.get("gap_diagnosis", {}).get("nvidia_mappings", []) if m.get("id")
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
# Node 8: retrieve_nvidia_context
# ---------------------------------------------------------------------------
@_register("retrieve_nvidia_context", "Retrieve NVIDIA RAG context for diagnosed gaps")
def node_retrieve_nvidia_context(state: ProductWorkflowState) -> NodeResult:
    gap_ids = state.gap_ids
    if not gap_ids:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No gaps to retrieve context for")

    try:
        from src.rag.rag_service_factory import build_rag_service

        rag_service = build_rag_service()
    except Exception as exc:
        if os.environ.get("APP_MODE", "").lower() == "product":
            return NodeResult(status=NodeStatus.FAILED, error_message=f"RAG service unavailable: {exc}")
        return NodeResult(
            status=NodeStatus.DEGRADED,
            degraded_reason=f"RAG service unavailable; using deterministic mapping fallback",
        )

    try:
        from src.rag.schemas import RetrievalQuery

        queries = [RetrievalQuery(text=f"NVIDIA technology for gap: {gid}") for gid in gap_ids]
        contexts = rag_service(queries) if hasattr(rag_service, "__call__") else []
        return NodeResult(
            status=NodeStatus.COMPLETED,
            state_updates={"nvidia_contexts": contexts},
        )
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            degraded_reason=f"RAG retrieval failed: {exc}",
        )


# ---------------------------------------------------------------------------
# Node 9: map_nvidia_technologies
# ---------------------------------------------------------------------------
@_register("map_nvidia_technologies", "Map NVIDIA technologies to diagnosed gaps")
def node_map_nvidia_technologies(state: ProductWorkflowState) -> NodeResult:
    gap_ids = state.gap_ids
    if not gap_ids:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No gaps to map technologies from")

    from src.diagnosis.nvidia_mapping import map_gap_to_technologies
    from src.extraction.schemas import TechnicalGap

    mappings = []
    errors = []
    for gap_id in gap_ids:
        try:
            tg = TechnicalGap(gap_id)
            techs = map_gap_to_technologies(tg)
            mappings.extend([
                {"gap_id": gap_id, "technology": t[0], "justification": t[1]}
                for t in techs
            ])
        except (ValueError, KeyError) as exc:
            errors.append(f"Gap '{gap_id}': {exc}")
            mappings.append({"gap_id": gap_id, "technology": "unknown", "justification": ""})

    return NodeResult(
        status=NodeStatus.COMPLETED if not errors else NodeStatus.DEGRADED,
        state_updates={"nvidia_mappings": mappings},
        degraded_reason="; ".join(errors[:5]) if errors else None,
    )


# ---------------------------------------------------------------------------
# Node 10: rank_recommendations
# ---------------------------------------------------------------------------
@_register("rank_recommendations", "Rank and build NVIDIA recommendations from gaps and mappings")
def node_rank_recommendations(state: ProductWorkflowState) -> NodeResult:
    gap_ids = state.gap_ids
    if not gap_ids:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No gaps to build recommendations from")

    startup_name = state.startup_profile.get("startup_name", "unknown")
    run_id = state.analysis_run_id or state.workflow_id

    from src.extraction.schemas import StartupProfile
    from src.recommendation.recommendation_engine import build_recommendations

    try:
        profile = StartupProfile.model_validate(state.startup_profile) if state.startup_profile else None
    except Exception:
        profile = None

    from src.classification.ai_native_classifier import classify_ai_native
    from src.diagnosis.schemas import GapDiagnosisResult
    from src.validation.evidence_validator import ValidatedEvidence

    classification = None
    validated_objs: list[ValidatedEvidence] = []
    if profile:
        classification = classify_ai_native(profile)
        for ev_dict in state.node_outputs.get("validated_evidence", []):
            try:
                validated_objs.append(ValidatedEvidence.model_validate(ev_dict))
            except Exception:
                pass

    gap_diag = GapDiagnosisResult(diagnosed_gaps=[], nvidia_technology_candidates=[], missing_evidence=[])

    # Use probabilistic scores from state instead of computing deterministic scoring
    prob_score = state.scores.get("probabilistic_score", 0.5) if state.scores else 0.5

    result = build_recommendations(
        startup_name=startup_name,
        profile=profile,
        classification=classification,
        validated_evidence=validated_objs,
        defensibility=None,
        inception_fit=None,
        production_readiness=None,
        composite=None,
        final_priority_score=prob_score,
        recommended_motion="assess",
        gap_diagnosis=gap_diag,
        rag_context=None,
    )

    rec_lines = [result.reasoning] if result.reasoning else []
    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={"recommendations": rec_lines},
    )


# ---------------------------------------------------------------------------
# Node 11: generate_brief
# ---------------------------------------------------------------------------
@_register("generate_brief", "Generate executive briefing from pipeline output")
def node_generate_brief(state: ProductWorkflowState) -> NodeResult:
    run_id = state.analysis_run_id or state.workflow_id

    brief_state = {
        "run_id": run_id,
        "startup_id": state.startup_id,
        "scores": state.scores,
        "claims": [],
        "evidence_items": state.evidence_items,
        "rag_contexts": state.nvidia_contexts,
        "nvidia_recommendations": state.nvidia_mappings,
        "gap_diagnosis_summary": {"gaps": [{"id": gid} for gid in state.gap_ids]},
        "accepted_evidence_items": state.node_outputs.get("validated_evidence", []),
        "blockers": state.blockers,
        "executed_nodes": state.completed_nodes,
    }

    from src.briefing.quantitative_brief import build_quantitative_brief

    brief = build_quantitative_brief(brief_state)
    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={"brief": brief},
    )


# ---------------------------------------------------------------------------
# Node 12: run_quality_gates
# ---------------------------------------------------------------------------
@_register("run_quality_gates", "Run quality gates on pipeline output")
def node_run_quality_gates(state: ProductWorkflowState) -> NodeResult:
    gates: dict[str, bool | str] = {}
    failures: list[str] = []

    has_evidence = len(state.evidence_items) > 0
    gates["evidence_collected"] = has_evidence
    if not has_evidence:
        failures.append("No evidence collected")

    has_profile = bool(state.startup_profile)
    gates["profile_extracted"] = has_profile
    if not has_profile:
        failures.append("No startup profile extracted")

    has_scores = bool(state.scores)
    gates["scoring_complete"] = has_scores

    has_gaps = len(state.gap_ids) > 0
    gates["gaps_diagnosed"] = has_gaps
    if not has_gaps:
        failures.append("No gaps diagnosed")

    has_mappings = len(state.nvidia_mappings) > 0
    gates["technologies_mapped"] = has_mappings

    has_recommendations = len(state.recommendations) > 0
    gates["recommendations_generated"] = has_recommendations

    has_brief = bool(state.brief)
    gates["brief_generated"] = has_brief
    if not has_brief:
        failures.append("No brief generated")

    status = "passed" if not failures else ("degraded" if has_evidence else "failed")
    return NodeResult(
        status=NodeStatus.COMPLETED if status == "passed" else NodeStatus.DEGRADED,
        state_updates={
            "quality_gates_result": {
                "status": status,
                "gates": gates,
                "failures": failures,
            }
        },
        degraded_reason="; ".join(failures) if failures else None,
    )


# ---------------------------------------------------------------------------
# Node 13: generate_claims
# ---------------------------------------------------------------------------
@_register("generate_claims", "Generate deterministic claims from pipeline output")
def node_generate_claims(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No analysis_run_id for claim generation")

    from src.repositories.product import ProductRepository

    repo = ProductRepository(session)
    run = repo.get_analysis_run(analysis_run_id)
    if run is None:
        return NodeResult(status=NodeStatus.FAILED, error_message=f"AnalysisRun not found: {analysis_run_id}")

    try:
        ledger = ClaimLedgerService(session)
        ledger.persist_claims_for_run(run)
        from src.database.models import ClaimRecord

        stmt = __import__("sqlalchemy").select(ClaimRecord).where(ClaimRecord.analysis_run_id == analysis_run_id)
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
# Node 14: match_activation_playbooks
# ---------------------------------------------------------------------------
@_register("match_activation_playbooks", "Match activation playbooks to diagnosed gaps")
def node_match_activation_playbooks(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No analysis_run_id for playbook matching")

    try:
        act_service = ActivationPlaybookService(session)
        recs = act_service.generate_recommendations_for_run(analysis_run_id)
        if recs:
            act_service.activation_repo.replace_recommendations_for_analysis_run(analysis_run_id, recs)
            rec_ids = [r.get("id", "") for r in recs if r.get("id")]
        else:
            rec_ids = []
        if not rec_ids:
            return NodeResult(
                status=NodeStatus.DEGRADED,
                degraded_reason="No activation playbooks matched",
                state_updates={"activation_recommendation_ids": []},
            )
        return NodeResult(status=NodeStatus.COMPLETED, state_updates={"activation_recommendation_ids": rec_ids})
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            error_message=str(exc),
            degraded_reason="Playbook matching failed",
        )


# ---------------------------------------------------------------------------
# Node 15: generate_activation_dossier
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
# Node 16: run_product_quality
# ---------------------------------------------------------------------------
@_register("run_product_quality", "Run product quality evaluation on analysis run")
def node_run_product_quality(state: ProductWorkflowState) -> NodeResult:
    session = cast(Session | None, state.metadata_json.get("_session"))
    if session is None:
        return NodeResult(status=NodeStatus.FAILED, error_message="No database session available")

    analysis_run_id = state.analysis_run_id
    if not analysis_run_id:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No analysis_run_id for quality run")

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
# Node 17: summarize_readiness
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


# ---------------------------------------------------------------------------
# Node 18: needs_review (human-in-the-loop)
# ---------------------------------------------------------------------------
@_register("needs_review", "Human-in-the-loop review node", critical=False)
def node_needs_review(state: ProductWorkflowState) -> NodeResult:
    if not LANGGRAPH_AVAILABLE:
        return NodeResult(status=NodeStatus.COMPLETED, state_updates={"review_required": False})

    review_data = {
        "startup_id": state.startup_id,
        "analysis_run_id": state.analysis_run_id,
        "gaps_found": len(state.gap_ids),
        "mappings_found": len(state.nvidia_mappings),
        "recommendations_found": len(state.recommendations),
        "evidence_count": len(state.evidence_items),
        "quality_gates": state.quality_gates_result,
    }

    try:
        decision = interrupt(review_data)
        return NodeResult(
            status=NodeStatus.COMPLETED,
            state_updates={
                "review_payload": review_data,
                "review_required": True,
                "review_decision": decision if isinstance(decision, str) else "",
            },
        )
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            state_updates={"review_required": False},
            degraded_reason=f"Review interrupt failed: {exc}",
        )


# ---------------------------------------------------------------------------
# Node 19: apply_feedback_weights
# ---------------------------------------------------------------------------
@_register("apply_feedback_weights", "Adjust scoring weights from human review feedback", critical=False)
def node_apply_feedback_weights(state: ProductWorkflowState) -> NodeResult:
    from src.decisioning.feedback_learner import apply_feedback_weight

    feedback_counts = state.feedback_counts
    if not feedback_counts:
        return NodeResult(status=NodeStatus.SKIPPED, state_updates={"iteration_count": state.iteration_count})

    from src.config.loader import ConfigLoaderService

    cfg = ConfigLoaderService()
    adjusted: dict[str, float] = {}

    base_pool: dict[str, float] = {}
    base_pool.update(cfg.priority_score_weights())
    base_pool.update(cfg.scoring().opportunity_score.model_dump())
    base_pool.update(cfg.scoring().production_readiness.model_dump())
    base_pool.update(cfg.scoring().defensibility.model_dump())
    base_pool.update(cfg.scoring().inception_fit.model_dump())

    for key, counts in feedback_counts.items():
        base = base_pool.get(key)
        if base is None:
            continue
        adjusted[key] = apply_feedback_weight(
            base,
            positive=counts.get("positive", 0),
            negative=counts.get("negative", 0),
        )

    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={
            "adjusted_weights": adjusted,
            "feedback_counts": {},
            "iteration_count": state.iteration_count + 1,
        },
    )


# ---------------------------------------------------------------------------
# Node 20: enhance_contexts_with_techniques
# ---------------------------------------------------------------------------
@_register("enhance_contexts_with_techniques", "Enhance NVIDIA contexts using hybrid RAG techniques")
def node_enhance_contexts_with_techniques(state: ProductWorkflowState) -> NodeResult:
    nvidia_contexts = state.nvidia_contexts
    if not nvidia_contexts:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No NVIDIA contexts to enhance")

    from src.rag.schemas import RetrievedContext
    from src.rag.technique_runner import run_techniques_hybrid

    try:
        contexts = [RetrievedContext.model_validate(c) if isinstance(c, dict) else c for c in nvidia_contexts]
    except Exception:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            state_updates={"technique_results": []},
            degraded_reason="Could not parse nvidia_contexts as RetrievedContext",
        )

    try:
        import yaml
        from pathlib import Path

        cfg_path = Path("config/techniques.yaml")
        if cfg_path.exists():
            with cfg_path.open(encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            group_config = raw.get("groups", [])
        else:
            group_config = []
    except Exception:
        group_config = []

    try:
        result = run_techniques_hybrid(contexts, group_config=group_config)
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            state_updates={"technique_results": []},
            degraded_reason=f"Technique runner failed: {exc}",
        )

    enhanced_contexts = result.get("contexts", contexts)
    technique_results = result.get("results", [])
    succeeded = [r for r in technique_results if r.get("success")]
    failed = [r for r in technique_results if not r.get("success")]

    return NodeResult(
        status=NodeStatus.COMPLETED if not failed else NodeStatus.DEGRADED,
        state_updates={
            "nvidia_contexts": [c.model_dump(mode="json") for c in enhanced_contexts],
            "technique_results": technique_results,
        },
        degraded_reason=f"{len(failed)} techniques failed: {', '.join(r['technique'] for r in failed[:5])}" if failed else None,
    )


# ---------------------------------------------------------------------------
# Node 21: score_with_evidence_weighting
# ---------------------------------------------------------------------------
@_register("score_with_evidence_weighting", "Score startup using evidence-weighted probabilistic scoring")
def node_score_with_evidence_weighting(state: ProductWorkflowState) -> NodeResult:
    evidence_items = state.evidence_items
    if not evidence_items:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No evidence items to score")

    from src.decisioning.evidence_weighted_scorer import WeightedFeature, score_features
    from src.decisioning.uncertainty_estimator import estimate_uncertainty
    from src.config.loader import ConfigLoaderService

    cfg = ConfigLoaderService()
    scoring_cfg = cfg.scoring()

    features: list[WeightedFeature] = []
    evidence_ids_used: list[str] = []

    for ev in evidence_items:
        ev_id = ev.get("id") or ev.get("evidence_id", "")
        if ev_id:
            evidence_ids_used.append(ev_id)
        source_reliability = ev.get("source_reliability", 0.5)
        relevance = ev.get("relevance", 0.5)
        features.append(WeightedFeature(
            name=f"evidence_{ev_id or len(features)}",
            value=(float(source_reliability) + float(relevance)) / 2,
            weight=1.0,
            evidence_ids=(ev_id,) if ev_id else (),
        ))

    if state.startup_profile:
        profile_confidence = state.startup_profile.get("confidence", 0.5)
        features.append(WeightedFeature(
            name="profile_confidence",
            value=float(profile_confidence),
            weight=2.0,
        ))

    scores = score_features(features)
    evidence_count = len(evidence_ids_used)
    uncertainty = estimate_uncertainty(
        evidence_count=evidence_count,
        contradiction_count=0,
        source_diversity=max(1, len(set(ev.get("source", "") for ev in evidence_items))),
    )

    # Compute per-section scores using config weights
    section_scores: dict[str, float] = {}
    try:
        weights_def = scoring_cfg.defensibility.model_dump() if hasattr(scoring_cfg, 'defensibility') else {}
        weights_inception = scoring_cfg.inception_fit.model_dump() if hasattr(scoring_cfg, 'inception_fit') else {}
        weights_prod = scoring_cfg.production_readiness.model_dump() if hasattr(scoring_cfg, 'production_readiness') else {}
        weights_opp = scoring_cfg.opportunity_score.model_dump() if hasattr(scoring_cfg, 'opportunity_score') else {}

        base_score = scores.get("score", 0.5)
        section_scores = {
            "defensibility": base_score * sum(weights_def.values()) / max(1, len(weights_def)),
            "inception_fit": base_score * sum(weights_inception.values()) / max(1, len(weights_inception)),
            "production_readiness": base_score * sum(weights_prod.values()) / max(1, len(weights_prod)),
            "opportunity": base_score * sum(weights_opp.values()) / max(1, len(weights_opp)),
        }
    except Exception:
        section_scores = {
            "defensibility": scores.get("score", 0.5),
            "inception_fit": scores.get("score", 0.5),
            "production_readiness": scores.get("score", 0.5),
            "opportunity": scores.get("score", 0.5),
        }

    result = {
        "score": scores.get("score", 0.5),
        "confidence": scores.get("confidence", 0.5),
        "uncertainty": uncertainty,
        "evidence_count": evidence_count,
        "feature_count": len(features),
        "sections": section_scores,
    }

    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={"evidence_weighted_scores": result},
    )


# ---------------------------------------------------------------------------
# Node 22: rank_with_expected_utility
# ---------------------------------------------------------------------------
@_register("rank_with_expected_utility", "Rank recommendations by expected utility")
def node_rank_with_expected_utility(state: ProductWorkflowState) -> NodeResult:
    nvidia_mappings = state.nvidia_mappings
    recommendations = state.recommendations

    candidates: list[dict[str, object]] = []
    for mapping in nvidia_mappings or []:
        gap_id = mapping.get("gap_id", "")
        technology = mapping.get("technology", "")
        candidates.append({
            "recommendation_id": f"rec_{technology}_{gap_id}",
            "technology": technology,
            "gap_id": gap_id,
            "business_impact": 0.5,
            "confidence": 0.5,
            "implementation_complexity": 0.3,
            "risk": 0.2,
        })

    for rec in recommendations or []:
        if isinstance(rec, str):
            candidates.append({
                "recommendation_id": f"rec_{len(candidates)}",
                "technology": rec,
                "gap_id": "",
                "business_impact": 0.5,
                "confidence": 0.5,
                "implementation_complexity": 0.3,
                "risk": 0.2,
            })

    if not candidates:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No candidates to rank")

    from src.decisioning.adaptive_recommendation_ranker import rank_recommendations

    try:
        ranked = rank_recommendations(candidates)
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            state_updates={"ranked_recommendations": candidates},
            degraded_reason=f"Ranking failed: {exc}",
        )

    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={"ranked_recommendations": ranked},
    )


# ---------------------------------------------------------------------------
# Node 23: write_decision_ledger
# ---------------------------------------------------------------------------
@_register("write_decision_ledger", "Write decision ledger CSV for audit trail")
def node_write_decision_ledger(state: ProductWorkflowState) -> NodeResult:
    from datetime import datetime, UTC
    from pathlib import Path
    from src.decisioning.decision_ledger_writer import append_decision

    ledger_path = Path("data/decision_ledger.csv")
    run_id = state.analysis_run_id or state.workflow_id

    decisions: list[dict[str, object]] = []

    if state.evidence_weighted_scores:
        ws = state.evidence_weighted_scores
        decisions.append({
            "decision_id": f"score_{run_id}",
            "area": "scoring",
            "decision": f"Evidence-weighted score: {ws.get('score', 'N/A')}",
            "alternatives_considered": "Deterministic scoring",
            "metrics_used": "source_reliability, relevance, profile_confidence",
            "data_source": "evidence_items, startup_profile",
            "benchmark_file": "config/scoring.yaml",
            "chosen_option": f"score={ws.get('score')}, confidence={ws.get('confidence')}",
            "expected_value": ws.get("score", 0),
            "confidence": ws.get("confidence", 0),
            "uncertainty": ws.get("uncertainty", 1),
            "risks": f"evidence_count={ws.get('evidence_count', 0)}",
            "owner": "pipeline",
            "date": datetime.now(UTC).isoformat(),
            "status": "approved",
        })

    if state.ranked_recommendations:
        for idx, rec in enumerate(state.ranked_recommendations):
            decisions.append({
                "decision_id": f"rank_{run_id}_{idx}",
                "area": "ranking",
                "decision": f"Rank {rec.get('expected_utility_rank', idx + 1)}: {rec.get('technology', 'N/A')}",
                "alternatives_considered": "Original order",
                "metrics_used": "expected_value, confidence, complexity, risk",
                "data_source": "nvidia_mappings, recommendations",
                "benchmark_file": "",
                "chosen_option": str(rec.get("technology", "")),
                "expected_value": rec.get("business_impact", 0),
                "confidence": rec.get("confidence", 0),
                "uncertainty": rec.get("uncertainty", 0),
                "risks": f"complexity={rec.get('implementation_complexity', 0)}, risk={rec.get('risk', 0)}",
                "owner": "pipeline",
                "date": datetime.now(UTC).isoformat(),
                "status": "approved",
            })

    if state.technique_results:
        for tr in state.technique_results:
            decisions.append({
                "decision_id": f"technique_{tr.get('technique', 'unknown')}_{run_id}",
                "area": "rag_technique",
                "decision": f"Group={tr.get('group', 'N/A')}, success={tr.get('success', False)}",
                "alternatives_considered": "Skip technique",
                "metrics_used": "run() return",
                "data_source": f"src.rag.{tr.get('technique', '')}",
                "benchmark_file": "config/techniques.yaml",
                "chosen_option": "enabled" if tr.get("success") else "failed",
                "expected_value": 1 if tr.get("success") else 0,
                "confidence": 1 if tr.get("success") else 0,
                "uncertainty": 0,
                "risks": tr.get("error", "") if not tr.get("success") else "",
                "owner": "pipeline",
                "date": datetime.now(UTC).isoformat(),
                "status": "completed" if tr.get("success") else "failed",
            })

    if not decisions:
        return NodeResult(status=NodeStatus.SKIPPED, error_message="No decisions to record")

    try:
        for dec in decisions:
            append_decision(ledger_path, dec)
    except Exception as exc:
        return NodeResult(
            status=NodeStatus.DEGRADED,
            state_updates={"decision_ledger_path": ""},
            degraded_reason=f"Failed to write decision ledger: {exc}",
        )

    return NodeResult(
        status=NodeStatus.COMPLETED,
        state_updates={"decision_ledger_path": str(ledger_path)},
    )
