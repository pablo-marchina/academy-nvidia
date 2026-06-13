"""Minimum persisted product routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.product_schemas import (
    ActionBriefRead,
    ActivationDossierGenerateResponse,
    ActivationDossierMarkdownRead,
    ActivationDossierRead,
    ActivationPlaybookListResponse,
    ActivationPlaybookRead,
    ActivationRecommendationListResponse,
    ActivationRecommendationRead,
    AnalysisRunCreate,
    AnalysisRunRead,
    ClaimListResponse,
    ClaimRead,
    ClaimReviewUpdate,
    DedupCandidateResponse,
    DependencyHealthRead,
    DiscoveryCandidateListResponse,
    DiscoveryCandidateRead,
    DiscoveryRunListResponse,
    DiscoveryRunRead,
    DiscoverySourceRead,
    EvidenceCoverageRead,
    ExportCreate,
    ExportRead,
    GenerateActivationRecommendationsResponse,
    ManualSeedRequest,
    ManualSeedResponse,
    OpportunityListItem,
    OpportunityListResponse,
    ProductCapabilityRead,
    ProductConfigurationItemRead,
    ProductHealthRead,
    ProductQualityMetricRead,
    ProductQualityRunRead,
    ProductQualitySummaryRead,
    ProductReadinessRead,
    ProductSetupChecklistItem,
    ProductSetupChecklistRead,
    PromoteCandidateResponse,
    ReadinessCheckRead,
    ReviewDecisionCreate,
    ReviewDecisionRead,
    StartupCreate,
    StartupEvidenceRead,
    StartupListItem,
    StartupRead,
    StartupUpdate,
    UrlListRequest,
    UrlListResponse,
)
from src.database.models import (
    ActionBriefRecord,
    ActivationDossierRecord,
    AnalysisRun,
    ClaimRecord,
    ProductQualityRun,
    Startup,
)
from src.database.session import get_db_session
from src.discovery.service import StartupDiscoveryService
from src.quality.service import ProductQualityService
from src.services.product import ProductService
from src.services.product.activation_service import ActivationPlaybookService
from src.services.product.claim_ledger import ClaimLedgerService
from src.services.product.dossier_service import ActivationDossierService
from src.services.product.readiness_service import ProductReadinessService

router = APIRouter(tags=["product"])
DbSession = Annotated[Session, Depends(get_db_session)]


def _startup_read(startup: Startup) -> StartupRead:
    return StartupRead(
        id=startup.id,
        name=startup.name,
        normalized_name=startup.normalized_name,
        website=startup.website,
        country=startup.country,
        sector=startup.sector,
        description=startup.description,
        product_summary=startup.product_summary,
        status=startup.status,
        tags=startup.tags_json,
        evidence=[
            StartupEvidenceRead(
                id=item.id,
                claim=item.claim,
                source_url=item.source_url,
                source_type=item.source_type,
                quote_or_evidence=item.quote_or_evidence,
                confidence=item.confidence,
                evidence_kind=item.evidence_kind,
                collected_at=item.collected_at,
                metadata=item.metadata_json,
            )
            for item in startup.evidence
        ],
        created_at=startup.created_at,
        updated_at=startup.updated_at,
    )


def _analysis_run_read(run: AnalysisRun) -> AnalysisRunRead:
    latest_brief = max(run.briefs, key=lambda item: item.version, default=None)
    return AnalysisRunRead(
        id=run.id,
        startup_id=run.startup_id,
        status=run.status,
        error_message=run.error_message,
        degraded_reason=run.degraded_reason,
        started_at=run.started_at,
        completed_at=run.completed_at,
        pipeline_version=run.pipeline_version,
        corpus_version=run.corpus_version,
        input_snapshot=run.input_snapshot_json,
        output_snapshot=run.output_snapshot_json,
        scores=[
            {
                "id": item.id,
                "score_type": item.score_type,
                "value": item.value,
                "confidence": item.confidence,
                "components": item.components_json,
                "missing_evidence": item.missing_evidence_json,
            }
            for item in run.scores
        ],
        gaps=[
            {
                "id": item.id,
                "gap_type": item.gap_type,
                "detected": item.detected,
                "confidence": item.confidence,
                "evidence_tag": item.evidence_tag,
                "reasoning": item.reasoning,
                "evidence_refs": item.evidence_refs_json,
                "missing_evidence": item.missing_evidence_json,
            }
            for item in run.gaps
        ],
        nvidia_mappings=[
            {
                "id": item.id,
                "gap_record_id": item.gap_record_id,
                "technology_name": item.technology_name,
                "addresses_gap": item.addresses_gap,
                "justification": item.justification,
                "recommendation_action": item.recommendation_action,
                "priority": item.priority,
                "details": item.details_json,
            }
            for item in run.mappings
        ],
        readiness_checks=[
            ReadinessCheckRead(
                code=item.code,
                severity=item.severity,
                status=item.status,
                user_message=item.user_message,
                internal_detail=item.internal_detail,
                recommended_action=item.recommended_action,
                metadata=item.metadata_json,
                observed_at=item.observed_at,
            )
            for item in run.readiness_checks
        ],
        action_brief_id=latest_brief.id if latest_brief is not None else None,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


def _inject_claim_summary(result: AnalysisRunRead, session: Session) -> None:
    try:
        from src.api.product_schemas import ClaimSummaryRead
        from src.repositories.claim import ClaimRepository

        repo = ClaimRepository(session)
        cov = repo.get_evidence_coverage_summary(result.id)
        if cov["total_claims"] > 0:
            result.claim_summary = ClaimSummaryRead(
                total_claims=cov["total_claims"],
                supported_claims=cov["supported_claims"],
                unsupported_claims=cov["unsupported_claims"],
                evidence_coverage=cov["evidence_coverage"],
            )
    except Exception:
        result.claim_summary = None


def _inject_dossier_summary(result: AnalysisRunRead, session: Session) -> None:
    try:
        from src.api.product_schemas import ActivationDossierSummaryRead
        from src.services.product.dossier_service import ActivationDossierService

        svc = ActivationDossierService(session)
        summary = svc.get_dossier_summary(result.id)
        result.dossier_summary = ActivationDossierSummaryRead(**summary)
    except Exception:
        result.dossier_summary = None


def _action_brief_read(record: ActionBriefRecord) -> ActionBriefRead:
    return ActionBriefRead(
        id=record.id,
        analysis_run_id=record.analysis_run_id,
        version=record.version,
        schema_version=record.schema_version,
        brief_json=record.brief_json,
        brief_markdown=record.brief_markdown,
        is_latest=record.is_latest,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post("/startups", response_model=StartupRead, status_code=status.HTTP_201_CREATED)
def create_startup(request: StartupCreate, session: DbSession) -> StartupRead:
    service = ProductService(session)
    payload = request.model_dump(mode="python")
    try:
        startup = service.create_startup(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _startup_read(startup)


@router.get("/startups", response_model=list[StartupListItem])
def list_startups(
    session: DbSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[StartupListItem]:
    service = ProductService(session)
    response: list[StartupListItem] = []
    for startup in service.list_startups(offset=offset, limit=limit):
        latest = service.repository.get_latest_analysis_run(startup.id)
        response.append(
            StartupListItem(
                id=startup.id,
                name=startup.name,
                website=startup.website,
                sector=startup.sector,
                status=startup.status,
                latest_analysis_run_id=latest.id if latest is not None else None,
                latest_analysis_status=latest.status if latest is not None else None,
                created_at=startup.created_at,
                updated_at=startup.updated_at,
            )
        )
    return response


@router.get("/startups/{startup_id}", response_model=StartupRead)
def get_startup(startup_id: str, session: DbSession) -> StartupRead:
    startup = ProductService(session).get_startup(startup_id)
    if startup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found.")
    return _startup_read(startup)


@router.post(
    "/startups/{startup_id}/analysis-runs",
    response_model=AnalysisRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_analysis_run(
    startup_id: str,
    request: AnalysisRunCreate,
    session: DbSession,
) -> AnalysisRunRead:
    service = ProductService(session)
    try:
        run = service.create_analysis_run_for_startup(
            startup_id,
            use_rag=request.use_rag,
            rag_backend=request.rag_backend,
            pipeline_version=request.pipeline_version,
            corpus_version=request.corpus_version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    result = _analysis_run_read(run)
    _inject_claim_summary(result, session)
    _inject_dossier_summary(result, session)
    return result


@router.get("/analysis-runs/{analysis_run_id}", response_model=AnalysisRunRead)
def get_analysis_run(analysis_run_id: str, session: DbSession) -> AnalysisRunRead:
    run = ProductService(session).get_analysis_run(analysis_run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    result = _analysis_run_read(run)
    _inject_claim_summary(result, session)
    _inject_dossier_summary(result, session)
    return result


@router.get("/analysis-runs/{analysis_run_id}/brief", response_model=ActionBriefRead)
def get_action_brief(analysis_run_id: str, session: DbSession) -> ActionBriefRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    brief = service.get_action_brief_for_run(analysis_run_id)
    if brief is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action brief not found.")
    return _action_brief_read(brief)


@router.get("/health/product", response_model=ProductHealthRead)
def product_health(session: DbSession) -> ProductHealthRead:
    return ProductHealthRead(**ProductService(session).get_product_health())


@router.get("/health/dependencies", response_model=DependencyHealthRead)
def dependency_health(session: DbSession) -> DependencyHealthRead:
    data: dict[str, Any] = ProductService(session).get_dependency_health()
    return DependencyHealthRead(**data)


@router.patch("/startups/{startup_id}", response_model=StartupRead)
def update_startup(startup_id: str, request: StartupUpdate, session: DbSession) -> StartupRead:
    service = ProductService(session)
    fields = request.model_dump(exclude_unset=True)
    if not fields:
        startup = service.get_startup(startup_id)
        if startup is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Startup not found.")
        return _startup_read(startup)
    try:
        updated = service.update_startup(startup_id, fields)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _startup_read(updated)


@router.post(
    "/analysis-runs/{analysis_run_id}/review",
    response_model=ReviewDecisionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    analysis_run_id: str,
    request: ReviewDecisionCreate,
    session: DbSession,
) -> ReviewDecisionRead:
    service = ProductService(session)
    try:
        record = service.create_review(
            analysis_run_id,
            decision=request.decision,
            reviewer=request.reviewer,
            notes=request.notes,
            metadata=request.metadata,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReviewDecisionRead(
        id=record.id,
        analysis_run_id=record.analysis_run_id,
        decision=record.decision,
        reviewer=record.reviewer,
        notes=record.notes,
        metadata=record.metadata_json,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get(
    "/analysis-runs/{analysis_run_id}/reviews",
    response_model=list[ReviewDecisionRead],
)
def list_reviews(analysis_run_id: str, session: DbSession) -> list[ReviewDecisionRead]:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    records = service.list_reviews(analysis_run_id)
    return [
        ReviewDecisionRead(
            id=item.id,
            analysis_run_id=item.analysis_run_id,
            decision=item.decision,
            reviewer=item.reviewer,
            notes=item.notes,
            metadata=item.metadata_json,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in records
    ]


@router.get("/opportunities", response_model=OpportunityListResponse)
def list_opportunities(
    session: DbSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    status: str | None = Query(default=None),
    recommended_motion: str | None = Query(default=None),
    min_score: float | None = Query(default=None, ge=0, le=100),
    sector: str | None = Query(default=None),
    has_degraded: bool | None = Query(default=None),
    review_decision: str | None = Query(default=None),
    order_by: str = Query(default="inception_fit_score"),
) -> OpportunityListResponse:
    service = ProductService(session)
    items, total = service.list_opportunities(
        offset=offset,
        limit=limit,
        status=status,
        recommended_motion=recommended_motion,
        min_score=min_score,
        sector=sector,
        has_degraded=has_degraded,
        review_decision=review_decision,
        order_by=order_by,
    )
    run_ids: list[str] = [
        item["latest_analysis_run_id"] for item in items if item.get("latest_analysis_run_id")
    ]
    if run_ids:
        try:
            act_service = ActivationPlaybookService(session)
            top_by_run = act_service.get_top_by_run_ids(run_ids)
            for item in items:
                run_id = item.get("latest_analysis_run_id")
                if run_id and run_id in top_by_run:
                    top = top_by_run[run_id]
                    item["top_activation_playbook"] = top.get("playbook_name")
                    item["activation_confidence"] = top.get("confidence")
                    item["activation_next_step"] = top.get("next_step")
                    exp = top.get("technical_experiment", "")
                    item["technical_experiment_summary"] = exp[:150] if exp else None
        except Exception:
            pass
        try:
            dossier_svc = ActivationDossierService(session)
            for item in items:
                run_id = item.get("latest_analysis_run_id")
                if run_id:
                    summary = dossier_svc.get_dossier_summary(run_id)
                    item["dossier_available"] = summary.get("dossier_available", False)
                    item["latest_dossier_id"] = summary.get("dossier_id")
        except Exception:
            pass
    return OpportunityListResponse(
        items=[OpportunityListItem(**item) for item in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post(
    "/analysis-runs/{analysis_run_id}/exports",
    response_model=ExportRead,
    status_code=status.HTTP_201_CREATED,
)
def create_export(
    analysis_run_id: str,
    request: ExportCreate,
    session: DbSession,
) -> ExportRead:
    service = ProductService(session)
    try:
        record = service.create_export(analysis_run_id, request.export_type)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return ExportRead(
        id=record.id,
        analysis_run_id=record.analysis_run_id,
        action_brief_id=record.action_brief_id,
        export_type=record.export_type,
        status=record.status,
        storage_path=record.storage_path,
        content_hash=record.content_hash,
        error_message=record.error_message,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/exports/{export_id}", response_model=ExportRead)
def get_export(export_id: str, session: DbSession) -> ExportRead:
    service = ProductService(session)
    record = service.get_export(export_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found.")
    return ExportRead(
        id=record.id,
        analysis_run_id=record.analysis_run_id,
        action_brief_id=record.action_brief_id,
        export_type=record.export_type,
        status=record.status,
        storage_path=record.storage_path,
        content_hash=record.content_hash,
        error_message=record.error_message,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _claim_read(record: ClaimRecord) -> ClaimRead:
    return ClaimRead(
        id=record.id,
        startup_id=record.startup_id,
        analysis_run_id=record.analysis_run_id,
        claim_text=record.claim_text,
        claim_type=record.claim_type,
        support_level=record.support_level,
        confidence=record.confidence,
        evidence_refs=record.evidence_refs_json,
        used_in_score=record.used_in_score,
        used_in_gap=record.used_in_gap,
        used_in_mapping=record.used_in_mapping,
        used_in_brief=record.used_in_brief,
        review_status=record.review_status,
        reviewer_notes=record.reviewer_notes,
        metadata=record.metadata_json,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/analysis-runs/{analysis_run_id}/claims", response_model=ClaimListResponse)
def list_claims(
    analysis_run_id: str,
    session: DbSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    claim_type: str | None = Query(default=None),
    support_level: str | None = Query(default=None),
    review_status: str | None = Query(default=None),
) -> ClaimListResponse:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    ledger = ClaimLedgerService(session)
    records = ledger.get_claims_for_analysis_run(
        analysis_run_id,
        claim_type=claim_type,
        support_level=support_level,
        review_status=review_status,
    )
    page = records[offset : offset + limit]
    return ClaimListResponse(
        items=[_claim_read(r) for r in page],
        total=len(records),
        offset=offset,
        limit=limit,
    )


@router.get(
    "/analysis-runs/{analysis_run_id}/evidence-coverage",
    response_model=EvidenceCoverageRead,
)
def get_evidence_coverage(
    analysis_run_id: str,
    session: DbSession,
) -> EvidenceCoverageRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    ledger = ClaimLedgerService(session)
    coverage = ledger.get_evidence_coverage_for_analysis_run(analysis_run_id)
    return EvidenceCoverageRead(**coverage)


@router.patch(
    "/analysis-runs/{analysis_run_id}/claims/{claim_id}/review",
    response_model=ClaimRead,
)
def update_claim_review(
    analysis_run_id: str,
    claim_id: str,
    request: ClaimReviewUpdate,
    session: DbSession,
) -> ClaimRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    ledger = ClaimLedgerService(session)
    record = ledger.update_claim_review(
        claim_id,
        review_status=request.review_status,
        reviewer_notes=request.reviewer_notes,
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found.")
    return _claim_read(record)


@router.get("/activation-playbooks", response_model=ActivationPlaybookListResponse)
def list_activation_playbooks() -> ActivationPlaybookListResponse:
    playbooks = ActivationPlaybookService.get_playbooks()
    items = [
        ActivationPlaybookRead(
            playbook_id=pb.playbook_id,
            name=pb.name,
            description=pb.description,
            target_gap_types=pb.target_gap_types,
            target_claim_types=pb.target_claim_types,
            nvidia_technologies=pb.nvidia_technologies,
            technical_experiment=pb.technical_experiment.model_dump(),
            success_metrics=pb.success_metrics,
            recommended_motion=pb.recommended_motion,
            prerequisites=pb.prerequisites,
            evidence_requirements=pb.evidence_requirements,
            risks=pb.risks,
            expected_value=pb.expected_value,
            implementation_complexity=pb.implementation_complexity,
            version=pb.version,
        )
        for pb in playbooks
    ]
    return ActivationPlaybookListResponse(playbooks=items, total=len(items))


@router.get(
    "/analysis-runs/{analysis_run_id}/activation-recommendations",
    response_model=ActivationRecommendationListResponse,
)
def list_activation_recommendations(
    analysis_run_id: str,
    session: DbSession,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> ActivationRecommendationListResponse:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    act_service = ActivationPlaybookService(session)
    items_raw = act_service.get_recommendations_for_run(analysis_run_id)
    items = [_activation_rec_read(r) for r in items_raw]
    total = len(items)
    page = items[offset : offset + limit]
    return ActivationRecommendationListResponse(items=page, total=total, offset=offset, limit=limit)


@router.post(
    "/analysis-runs/{analysis_run_id}/activation-recommendations/generate",
    response_model=GenerateActivationRecommendationsResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_activation_recommendations(
    analysis_run_id: str,
    session: DbSession,
) -> GenerateActivationRecommendationsResponse:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    act_service = ActivationPlaybookService(session)
    raw = act_service.persist_recommendations_for_run(analysis_run_id)
    items = [_activation_rec_read(r) for r in raw]
    return GenerateActivationRecommendationsResponse(recommendations=items, total=len(items))


def _dossier_read(record: ActivationDossierRecord) -> ActivationDossierRead:
    return ActivationDossierRead(
        id=record.id,
        analysis_run_id=record.analysis_run_id,
        version=record.version,
        schema_version=record.schema_version,
        dossier_json=record.dossier_json,
        dossier_markdown=record.dossier_markdown,
        is_latest=record.is_latest,
        evidence_coverage=record.evidence_coverage,
        unsupported_claim_count=record.unsupported_claim_count,
        top_activation_playbook_id=record.top_activation_playbook_id,
        recommended_motion=record.recommended_motion,
        review_status=record.review_status,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post(
    "/analysis-runs/{analysis_run_id}/dossier",
    response_model=ActivationDossierGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dossier(
    analysis_run_id: str,
    session: DbSession,
    force: bool = Query(default=False, description="Force regeneration of a new version"),
) -> ActivationDossierGenerateResponse:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    dossier_svc = ActivationDossierService(session)
    existing = dossier_svc.get_latest_dossier(analysis_run_id)
    is_new = force or existing is None
    if force or existing is None:
        record = dossier_svc.build_dossier_for_analysis_run(
            analysis_run_id, force_new_version=force
        )
    else:
        record = existing
    return ActivationDossierGenerateResponse(
        dossier=_dossier_read(record),
        version=record.version,
        is_new=is_new,
    )


@router.get(
    "/analysis-runs/{analysis_run_id}/dossier",
    response_model=ActivationDossierRead,
)
def get_dossier(
    analysis_run_id: str,
    session: DbSession,
) -> ActivationDossierRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    dossier_svc = ActivationDossierService(session)
    record = dossier_svc.get_latest_dossier(analysis_run_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dossier found for this analysis run. Generate one first with POST.",
        )
    return _dossier_read(record)


@router.get(
    "/analysis-runs/{analysis_run_id}/dossier/markdown",
    response_model=ActivationDossierMarkdownRead,
)
def get_dossier_markdown(
    analysis_run_id: str,
    session: DbSession,
) -> ActivationDossierMarkdownRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    dossier_svc = ActivationDossierService(session)
    record = dossier_svc.get_latest_dossier(analysis_run_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dossier found for this analysis run. Generate one first with POST.",
        )
    return ActivationDossierMarkdownRead(
        markdown=record.dossier_markdown,
        dossier_id=record.id,
        version=record.version,
    )


@router.post(
    "/analysis-runs/{analysis_run_id}/quality-runs",
    response_model=ProductQualityRunRead,
    status_code=status.HTTP_201_CREATED,
)
def create_quality_run(
    analysis_run_id: str,
    session: DbSession,
) -> ProductQualityRunRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    quality_service = ProductQualityService(session)
    try:
        quality_run = quality_service.run_quality_evaluation_for_analysis_run(analysis_run_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _quality_run_read(quality_run, session)


@router.get(
    "/analysis-runs/{analysis_run_id}/quality-runs",
    response_model=list[ProductQualityRunRead],
)
def list_quality_runs(
    analysis_run_id: str,
    session: DbSession,
) -> list[ProductQualityRunRead]:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    quality_service = ProductQualityService(session)
    runs = quality_service.repository.list_quality_runs_for_analysis_run(analysis_run_id)
    return [_quality_run_read(r, session) for r in runs]


@router.get(
    "/analysis-runs/{analysis_run_id}/quality-runs/latest",
    response_model=ProductQualityRunRead,
)
def get_latest_quality_run(
    analysis_run_id: str,
    session: DbSession,
) -> ProductQualityRunRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    quality_service = ProductQualityService(session)
    quality_run = quality_service.repository.get_latest_quality_run_for_analysis_run(
        analysis_run_id
    )
    if quality_run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No quality run found for this analysis run. Run one first with POST.",
        )
    return _quality_run_read(quality_run, session)


@router.get(
    "/analysis-runs/{analysis_run_id}/quality-summary",
    response_model=ProductQualitySummaryRead,
)
def get_quality_summary(
    analysis_run_id: str,
    session: DbSession,
) -> ProductQualitySummaryRead:
    service = ProductService(session)
    if service.get_analysis_run(analysis_run_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    quality_service = ProductQualityService(session)
    summary = quality_service.summarize_quality_result(analysis_run_id)
    return ProductQualitySummaryRead(**summary)


# ---------------------------------------------------------------------------
# Product Capability & Configuration Endpoints
# ---------------------------------------------------------------------------


@router.get("/product/capabilities", response_model=list[ProductCapabilityRead])
def list_capabilities() -> list[ProductCapabilityRead]:
    svc = ProductReadinessService()
    return [
        ProductCapabilityRead(
            capability_id=c.capability_id,
            name=c.name,
            description=c.description,
            category=c.category,
            required=c.required,
            status=c.status.value,
            status_reason=c.status_reason,
            required_env_vars=c.required_env_vars,
            optional_env_vars=c.optional_env_vars,
            required_extras=c.required_extras,
            required_services=c.required_services,
            setup_instructions=c.setup_instructions,
            failure_mode=c.failure_mode,
            user_visible=c.user_visible,
            documentation_ref=c.documentation_ref,
        )
        for c in svc.list_capabilities()
    ]


@router.get("/product/configuration", response_model=list[ProductConfigurationItemRead])
def list_configuration() -> list[ProductConfigurationItemRead]:
    svc = ProductReadinessService()
    return [
        ProductConfigurationItemRead(
            key=item["key"],
            description=item["description"],
            required=item["required"],
            secret=item["secret"],
            default=item["default"],
            current_value=item["current_value"],
            is_set=item["is_set"],
        )
        for item in svc.list_required_configuration()
    ]


@router.get("/product/setup-checklist", response_model=ProductSetupChecklistRead)
def get_setup_checklist() -> ProductSetupChecklistRead:
    svc = ProductReadinessService()
    items = svc.get_setup_checklist()
    completed = sum(1 for i in items if i["is_set"])
    pending = len(items) - completed
    return ProductSetupChecklistRead(
        items=[
            ProductSetupChecklistItem(
                key=i["key"],
                description=i["description"],
                is_set=i["is_set"],
                required=i["required"],
            )
            for i in items
        ],
        total=len(items),
        completed=completed,
        pending=pending,
    )


@router.get("/product/readiness", response_model=ProductReadinessRead)
def get_product_readiness() -> ProductReadinessRead:
    svc = ProductReadinessService()
    report = svc.get_product_readiness()
    return ProductReadinessRead(
        ready=report.ready,
        blocking_missing_config=report.blocking_missing_config,
        optional_missing_config=report.optional_missing_config,
        unavailable_capabilities=report.unavailable_capabilities,
        degraded_capabilities=report.degraded_capabilities,
        setup_checklist=[
            ProductSetupChecklistItem(
                key=i["key"],
                description=i["description"],
                is_set=i["is_set"],
                required=i["required"],
            )
            for i in report.setup_checklist
        ],
        user_messages=report.user_messages,
    )


def _quality_run_read(
    quality_run: ProductQualityRun,
    session: Session,
) -> ProductQualityRunRead:
    from src.quality.repository import ProductQualityRepository

    repo = ProductQualityRepository(session)
    metrics = repo.get_metrics_for_quality_run(quality_run.id)
    return ProductQualityRunRead(
        id=quality_run.id,
        analysis_run_id=quality_run.analysis_run_id,
        dossier_id=quality_run.dossier_id,
        action_brief_id=quality_run.action_brief_id,
        status=quality_run.status,
        started_at=quality_run.started_at,
        completed_at=quality_run.completed_at,
        evaluator_version=quality_run.evaluator_version,
        metrics=[
            ProductQualityMetricRead(
                id=m.id,
                quality_run_id=m.quality_run_id,
                metric_name=m.metric_name,
                metric_value=m.metric_value,
                threshold=m.threshold,
                passed=m.passed,
                severity=m.severity,
                details=m.details_json,
                created_at=m.created_at,
            )
            for m in metrics
        ],
        metrics_json=quality_run.metrics_json,
        summary_json=quality_run.summary_json,
        degraded_reason=quality_run.degraded_reason,
        created_at=quality_run.created_at,
        updated_at=quality_run.updated_at,
    )


def _activation_rec_read(rec: dict) -> ActivationRecommendationRead:
    return ActivationRecommendationRead(
        id=rec.get("id", ""),
        analysis_run_id=rec.get("analysis_run_id", ""),
        playbook_id=rec.get("playbook_id", ""),
        playbook_name=rec.get("playbook_name", ""),
        matched_gap_types=rec.get("matched_gap_types", []),
        matched_claim_ids=rec.get("matched_claim_ids", []),
        nvidia_technologies=rec.get("nvidia_technologies", []),
        technical_experiment=rec.get("technical_experiment", ""),
        success_metrics=rec.get("success_metrics", []),
        recommended_motion=rec.get("recommended_motion", ""),
        priority=rec.get("priority", 4),
        confidence=rec.get("confidence", "low"),
        reasoning=rec.get("reasoning", ""),
        evidence_refs=rec.get("evidence_refs", []),
        risks=rec.get("risks", []),
        next_step=rec.get("next_step", ""),
        created_at=rec.get("created_at"),
        updated_at=rec.get("updated_at"),
    )


# ---------------------------------------------------------------------------
# Discovery Routes
# ---------------------------------------------------------------------------


@router.get("/discovery/sources", response_model=list[DiscoverySourceRead])
def list_discovery_sources(
    session: DbSession,
) -> list[DiscoverySourceRead]:
    svc = StartupDiscoveryService(session)
    sources = svc.list_sources()
    return [DiscoverySourceRead(**s) for s in sources]


@router.post("/discovery/manual-seed", response_model=ManualSeedResponse, status_code=201)
def discover_manual_seed(
    body: ManualSeedRequest,
    session: DbSession,
) -> ManualSeedResponse:
    svc = StartupDiscoveryService(session)
    result = svc.run_manual_seed_discovery(
        [e.model_dump() for e in body.entries],
    )
    return ManualSeedResponse(**result)


@router.post("/discovery/url-list", response_model=UrlListResponse, status_code=201)
def discover_url_list(
    body: UrlListRequest,
    session: DbSession,
) -> UrlListResponse:
    svc = StartupDiscoveryService(session)
    result = svc.run_url_list_discovery(body.urls)
    return UrlListResponse(**result)


@router.get("/discovery/runs", response_model=DiscoveryRunListResponse)
def list_discovery_runs(
    session: DbSession,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
) -> DiscoveryRunListResponse:
    svc = StartupDiscoveryService(session)
    runs = svc.repo.list_discovery_runs(offset=offset, limit=limit, status=status)
    items = [
        DiscoveryRunRead(
            id=r.id,
            source_id=r.source_id,
            status=r.status,
            error_message=r.error_message,
            results_count=r.results_count,
            candidates_created=r.candidates_created,
            duplicates_found=r.duplicates_found,
            query_json=r.query_json,
            metadata_json=r.metadata_json,
            started_at=r.started_at,
            completed_at=r.completed_at,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in runs
    ]
    return DiscoveryRunListResponse(items=items, total=len(items), offset=offset, limit=limit)


@router.get("/discovery/runs/{run_id}", response_model=DiscoveryRunRead)
def get_discovery_run(
    run_id: str,
    session: DbSession,
) -> DiscoveryRunRead:
    svc = StartupDiscoveryService(session)
    run = svc.repo.get_discovery_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Discovery run not found: {run_id}")
    return DiscoveryRunRead(
        id=run.id,
        source_id=run.source_id,
        status=run.status,
        error_message=run.error_message,
        results_count=run.results_count,
        candidates_created=run.candidates_created,
        duplicates_found=run.duplicates_found,
        query_json=run.query_json,
        metadata_json=run.metadata_json,
        started_at=run.started_at,
        completed_at=run.completed_at,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.get("/discovery/candidates", response_model=DiscoveryCandidateListResponse)
def list_discovery_candidates(
    session: DbSession,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    source_id: str | None = Query(None),
    sector: str | None = Query(None),
    confidence_min: float | None = Query(None, ge=0.0, le=1.0),
    has_website: bool | None = Query(None),
    ai_native_signal: bool | None = Query(None),
) -> DiscoveryCandidateListResponse:
    svc = StartupDiscoveryService(session)
    candidates = svc.list_candidates(
        offset=offset,
        limit=limit,
        status=status,
        source_id=source_id,
        sector=sector,
        confidence_min=confidence_min,
        has_website=has_website,
        ai_native_signal=ai_native_signal,
    )
    items = [
        DiscoveryCandidateRead(
            id=c.id,
            discovery_run_id=c.discovery_run_id,
            source_id=c.source_id,
            discovered_name=c.discovered_name,
            normalized_name=c.normalized_name,
            website=c.website,
            country=c.country,
            sector=c.sector,
            description=c.description,
            source_url=c.source_url,
            raw_text_excerpt=c.raw_text_excerpt,
            ai_native_signals_json=c.ai_native_signals_json,
            evidence_refs_json=c.evidence_refs_json,
            confidence=c.confidence,
            status=c.status,
            promoted_startup_id=c.promoted_startup_id,
            metadata_json=c.metadata_json,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in candidates
    ]
    return DiscoveryCandidateListResponse(items=items, total=len(items), offset=offset, limit=limit)


@router.get("/discovery/candidates/{candidate_id}", response_model=DiscoveryCandidateRead)
def get_discovery_candidate(
    candidate_id: str,
    session: DbSession,
) -> DiscoveryCandidateRead:
    svc = StartupDiscoveryService(session)
    c = svc.get_candidate_detail(candidate_id)
    if c is None:
        raise HTTPException(status_code=404, detail=f"Candidate not found: {candidate_id}")
    return DiscoveryCandidateRead(
        id=c.id,
        discovery_run_id=c.discovery_run_id,
        source_id=c.source_id,
        discovered_name=c.discovered_name,
        normalized_name=c.normalized_name,
        website=c.website,
        country=c.country,
        sector=c.sector,
        description=c.description,
        source_url=c.source_url,
        raw_text_excerpt=c.raw_text_excerpt,
        ai_native_signals_json=c.ai_native_signals_json,
        evidence_refs_json=c.evidence_refs_json,
        confidence=c.confidence,
        status=c.status,
        promoted_startup_id=c.promoted_startup_id,
        metadata_json=c.metadata_json,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.post(
    "/discovery/candidates/{candidate_id}/promote",
    response_model=PromoteCandidateResponse,
)
def promote_discovery_candidate(
    candidate_id: str,
    session: DbSession,
) -> PromoteCandidateResponse:
    svc = StartupDiscoveryService(session)
    try:
        result = svc.promote_candidate(candidate_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=f"Candidate not found: {candidate_id}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return PromoteCandidateResponse(**result)


@router.post(
    "/discovery/candidates/{candidate_id}/dedup",
    response_model=DedupCandidateResponse,
)
def dedup_discovery_candidate(
    candidate_id: str,
    session: DbSession,
) -> DedupCandidateResponse:
    svc = StartupDiscoveryService(session)
    result = svc.deduplicate_candidate(candidate_id)
    if result.get("_error") == "not_found":
        raise HTTPException(status_code=404, detail=f"Candidate not found: {candidate_id}")
    return DedupCandidateResponse(
        duplicate_of_candidate_id=result.get("duplicate_of_candidate_id"),
        duplicate_of_startup_id=result.get("duplicate_of_startup_id"),
    )
