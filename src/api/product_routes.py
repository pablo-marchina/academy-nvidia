"""Minimum persisted product routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.product_schemas import (
    ActionBriefRead,
    AnalysisRunCreate,
    AnalysisRunRead,
    ClaimListResponse,
    ClaimRead,
    ClaimReviewUpdate,
    DependencyHealthRead,
    EvidenceCoverageRead,
    ExportCreate,
    ExportRead,
    OpportunityListItem,
    OpportunityListResponse,
    ProductHealthRead,
    ReadinessCheckRead,
    ReviewDecisionCreate,
    ReviewDecisionRead,
    StartupCreate,
    StartupEvidenceRead,
    StartupListItem,
    StartupRead,
    StartupUpdate,
)
from src.database.models import ActionBriefRecord, AnalysisRun, ClaimRecord, Startup
from src.database.session import get_db_session
from src.services.product import ProductService
from src.services.product.claim_ledger import ClaimLedgerService

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
    return result


@router.get("/analysis-runs/{analysis_run_id}", response_model=AnalysisRunRead)
def get_analysis_run(analysis_run_id: str, session: DbSession) -> AnalysisRunRead:
    run = ProductService(session).get_analysis_run(analysis_run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis run not found.")
    result = _analysis_run_read(run)
    _inject_claim_summary(result, session)
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
