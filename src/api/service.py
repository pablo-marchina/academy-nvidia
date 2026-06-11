from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import HttpUrl

from src.briefing.action_brief import build_action_brief
from src.briefing.markdown_renderer import render_action_brief_markdown
from src.evaluation.answer_quality_eval import evaluate_answer_quality
from src.evaluation.answer_quality_schemas import AnswerQualityEvalCase
from src.extraction.schemas import ConfidenceLevel, Evidence, SourceType, StartupProfile
from src.pipeline.run_pipeline import run_full_pipeline
from src.rag.embeddings import MockEmbeddingProvider
from src.rag.retrieval import build_default_index
from src.rag.schemas import PackingConfig, RerankingConfig
from src.rag.vector_store import InMemoryVectorStore

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEMO_RUNS_DIR = _PROJECT_ROOT / "data" / "demo_runs"


def _load_pyproject_version() -> dict[str, str]:
    pyproject = _PROJECT_ROOT / "pyproject.toml"
    try:
        import tomllib

        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
        proj = data.get("project", {})
        return {
            "name": proj.get("name", "nvidia-startup-ai-radar"),
            "version": proj.get("version", "0.1.0"),
            "description": proj.get("description", ""),
        }
    except Exception:
        return {
            "name": "nvidia-startup-ai-radar",
            "version": "0.1.0",
            "description": "NVIDIA Startup AI Radar",
        }


def get_version() -> dict[str, str]:
    return _load_pyproject_version()


def get_rag_status() -> dict[str, Any]:
    info: dict[str, Any] = {
        "backend": "in_memory",
        "collection_name": "nvidia_corpus",
        "vector_size": 384,
        "qdrant_url": "http://localhost:6333",
        "qdrant_available": False,
        "error": None,
    }
    try:
        from src.rag.qdrant_store import QdrantConfig, QdrantStore

        cfg = QdrantConfig()
        info["qdrant_url"] = cfg.url
        info["collection_name"] = cfg.collection_name
        info["vector_size"] = cfg.vector_size
        store = QdrantStore(config=cfg)
        store._ensure_client()
        info["qdrant_available"] = True
        info["backend"] = "qdrant"
    except Exception as e:
        info["error"] = str(e)
    return info


def build_rag_dependencies(
    rag_backend: str,
) -> tuple[Any, Any, Any]:
    chunk_index = build_default_index()
    if not chunk_index.chunks:
        return chunk_index, None, None

    if rag_backend == "local":
        embedding_model = MockEmbeddingProvider()
        vector_store: Any = InMemoryVectorStore()
    elif rag_backend == "qdrant":
        from src.rag.qdrant_store import QdrantConfig, QdrantStore

        embedding_model = MockEmbeddingProvider()
        config = QdrantConfig(collection_name="nvidia_corpus")
        store = QdrantStore(config=config)
        store._ensure_client()
        vector_store = store
    else:
        raise ValueError(f"Unknown RAG backend: {rag_backend}")

    return chunk_index, embedding_model, vector_store


def _build_profile(startup_name: str, raw: dict[str, Any]) -> StartupProfile:
    p = raw.get("profile", {})
    return StartupProfile(
        startup_name=startup_name,
        website=HttpUrl(raw.get("source_url", "https://example.com")),
        sector=p.get("sector", "Technology"),
        description=p.get("description", ""),
        product_summary=p.get("product_summary", ""),
        ai_signals=p.get("ai_signals", []),
        tech_stack_signals=p.get("tech_stack", []),
        customers=p.get("customers", []),
        funding_signals=p.get("funding", []),
        sources=[],
        confidence_score=0.6,
    )


def _build_evidence(raw: dict[str, Any]) -> list[Evidence]:
    return [
        Evidence(
            claim=e["claim"],
            source_url=HttpUrl("https://example.com"),
            source_type=SourceType.OFFICIAL_SITE,
            quote_or_evidence=e["claim"],
            confidence=ConfidenceLevel(e.get("confidence", "medium")),
            collected_at=datetime.now(UTC),
        )
        for e in raw.get("evidence", [])
    ]


def _build_generic_quality_case(startup_name: str) -> AnswerQualityEvalCase:
    forbidden = [
        "guaranteed",
        "always",
        "never",
        "proves",
        "will definitely",
        "100%",
    ]
    return AnswerQualityEvalCase(
        case_id=f"api_{startup_name}",
        description=f"Generic quality check for API-generated brief '{startup_name}'",
        pipeline_case_id=startup_name,
        use_rag=False,
        required_sections=[
            "Executive Summary",
            "Why This Startup Matters",
            "AI-Native Maturity",
            "Scores Overview",
            "Evidence",
        ],
        expect_missing_evidence=False,
        expect_uncertainty=False,
        max_unsupported_claim_count=0,
        max_forbidden_absolute_language_count=0,
        forbidden_absolute_language=forbidden,
        unsupported_claim_patterns=[],
        min_rag_context_citation_coverage=0.0,
        min_startup_evidence_citation_coverage=0.0,
    )


@dataclass
class _DemoRunReport:
    run_id: str
    started_at: str
    finished_at: str = ""
    startup_name: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, str | None] = field(default_factory=dict)
    pipeline_summary: dict[str, Any] = field(default_factory=dict)
    status: str = "running"


def run_brief_pipeline(
    startup_name: str,
    raw_input: dict[str, Any],
    use_rag: bool = False,
    rag_backend: str = "local",
    offline: bool = False,
    run_answer_quality_eval: bool = False,
) -> dict[str, Any]:
    started_at = datetime.now(UTC).isoformat()
    run_id = f"api_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

    report = _DemoRunReport(
        run_id=run_id,
        started_at=started_at,
        startup_name=startup_name,
        parameters={
            "use_rag": use_rag,
            "rag_backend": rag_backend if use_rag else None,
            "offline": offline,
            "run_answer_quality_eval": run_answer_quality_eval,
        },
    )

    warnings: list[str] = []

    profile = _build_profile(startup_name, raw_input)
    evidence = _build_evidence(raw_input)

    chunk_index = None
    embedding_model = None
    vector_store = None
    reranking_config = None
    packing_config = None

    if use_rag and not offline:
        try:
            chunk_index, embedding_model, vector_store = build_rag_dependencies(rag_backend)
            reranking_config = RerankingConfig()
            packing_config = PackingConfig()
        except Exception as exc:
            warnings.append(f"RAG dependency build failed: {exc}. Running without RAG.")
            chunk_index = None
            embedding_model = None
            vector_store = None

    t0 = time.perf_counter()
    try:
        result = run_full_pipeline(
            startup_name=startup_name,
            profile=profile,
            evidence_list=evidence,
            chunk_index=chunk_index,
            embedding_model=embedding_model,
            vector_store=vector_store,
            reranking_config=reranking_config,
            packing_config=packing_config,
        )
    except Exception as exc:
        report.finished_at = datetime.now(UTC).isoformat()
        report.status = "failed"
        return {
            "run_id": run_id,
            "startup_name": startup_name,
            "brief_json": {},
            "brief_markdown": "",
            "run_report": asdict(report),
            "answer_quality_eval": None,
            "warnings": warnings + [f"Pipeline failed: {exc}"],
        }

    elapsed = time.perf_counter() - t0

    brief = build_action_brief(result)
    brief_json = json.loads(brief.model_dump_json())
    brief_markdown = render_action_brief_markdown(brief)

    gd = result.gap_diagnosis
    gaps = [g for g in (gd.diagnosed_gaps if gd else []) if g.detected]
    recs = result.recommendation

    report.pipeline_summary = {
        "elapsed_seconds": round(elapsed, 2),
        "final_priority_score": result.final_priority_score,
        "recommended_motion": result.recommended_motion,
        "gaps_detected": len(gaps),
        "recommendations": len(recs.recommendations) if recs else 0,
        "evidence_items": len(result.evidence_used),
        "missing_evidence_items": len(result.missing_evidence),
        "rag_used": use_rag,
    }
    report.finished_at = datetime.now(UTC).isoformat()
    report.status = "completed"

    outputs: dict[str, str | None] = {}
    outputs["brief_json"] = "embedded"
    outputs["brief_markdown"] = "embedded"

    answer_quality_result: dict | None = None
    if run_answer_quality_eval:
        case = _build_generic_quality_case(startup_name)
        eval_result = evaluate_answer_quality(brief, case)
        answer_quality_result = json.loads(eval_result.model_dump_json())
        if eval_result.failure_reasons:
            warnings.extend(f"Answer quality FAIL: {r}" for r in eval_result.failure_reasons)

    report.outputs = outputs

    return {
        "run_id": run_id,
        "startup_name": startup_name,
        "brief_json": brief_json,
        "brief_markdown": brief_markdown,
        "run_report": asdict(report),
        "answer_quality_eval": answer_quality_result,
        "warnings": warnings,
    }


def run_brief_evaluate(
    startup_name: str,
    brief_json: dict,
) -> dict[str, Any]:
    from src.briefing.schemas import StartupActionBrief

    brief = StartupActionBrief(**brief_json)
    case = _build_generic_quality_case(startup_name)
    eval_result = evaluate_answer_quality(brief, case)
    result_data = json.loads(eval_result.model_dump_json())
    status = "PASS"
    if not eval_result.passed:
        if eval_result.metrics.answer_quality_status.value == "FAIL":
            status = "FAIL"
        else:
            status = "WARN"
    return {
        "status": status,
        "metrics": result_data.get("metrics", {}),
        "gates": result_data.get("gates", []),
        "failure_reasons": result_data.get("failure_reasons", []),
        "warnings": result_data.get("warnings", []),
    }


def list_artifacts(sub_path: str = "") -> dict[str, Any]:
    base = _DEMO_RUNS_DIR.resolve()
    if sub_path:
        target = (base / sub_path).resolve()
    else:
        target = base

    if not str(target).startswith(str(base)):
        return {"artifacts": [], "total": 0}

    if not target.exists() or not target.is_dir():
        return {"artifacts": [], "total": 0}

    artifacts: list[dict[str, Any]] = []
    for f in sorted(target.iterdir()):
        if f.is_file():
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=UTC).isoformat()
            artifacts.append(
                {
                    "filename": f.name,
                    "path": str(f.relative_to(base)),
                    "size_bytes": f.stat().st_size,
                    "modified_at": mtime,
                }
            )
    return {"artifacts": artifacts, "total": len(artifacts)}
