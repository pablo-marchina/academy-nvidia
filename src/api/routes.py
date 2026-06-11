from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from src.api.schemas import (
    ArtifactListResponse,
    BriefRequest,
    BriefResponse,
    EvaluateRequest,
    EvaluateResponse,
    RagStatusResponse,
    VersionResponse,
)
from src.api.service import (
    get_rag_status,
    get_version,
    list_artifacts,
    run_brief_evaluate,
    run_brief_pipeline,
)

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    data = get_version()
    return VersionResponse(**data)


@router.get("/rag/status", response_model=RagStatusResponse)
def rag_status() -> RagStatusResponse:
    data = get_rag_status()
    return RagStatusResponse(**data)


@router.post("/brief", response_model=BriefResponse)
def brief(req: BriefRequest) -> BriefResponse:
    try:
        result = run_brief_pipeline(
            startup_name=req.startup_name,
            raw_input={
                "startup_name": req.startup_name,
                "source_url": req.source_url,
                "profile": req.profile,
                "evidence": req.evidence,
            },
            use_rag=req.use_rag,
            rag_backend=req.rag_backend,
            offline=req.offline,
            run_answer_quality_eval=req.run_answer_quality_eval,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return BriefResponse(**result)


@router.post("/brief/evaluate", response_model=EvaluateResponse)
def brief_evaluate(req: EvaluateRequest) -> EvaluateResponse:
    try:
        result = run_brief_evaluate(
            startup_name=req.startup_name,
            brief_json=req.brief_json,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return EvaluateResponse(**result)


@router.get("/demo/artifacts", response_model=ArtifactListResponse)
def demo_artifacts(
    path: str = Query(default="", description="Subpath within data/demo_runs/"),
) -> ArtifactListResponse:
    result = list_artifacts(path)
    return ArtifactListResponse(**result)
