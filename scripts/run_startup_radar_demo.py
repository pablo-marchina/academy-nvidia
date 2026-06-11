#!/usr/bin/env python3
"""CLI demo — End-to-end Startup Action Brief generation.

Runs the full Startup AI Radar pipeline on a sample input JSON and exports
brief Markdown, brief JSON, and a run report. Optionally uses RAG (local or
Qdrant) and runs answer quality evaluation.

Usage:
    python scripts/run_startup_radar_demo.py --input examples/demo/sample_startup_input.json
    python scripts/run_startup_radar_demo.py --input ... --use-rag --rag-backend local
    python scripts/run_startup_radar_demo.py --input ... --use-rag --rag-backend qdrant
    python scripts/run_startup_radar_demo.py --input ... --offline
    python scripts/run_startup_radar_demo.py --input ... --run-answer-quality-eval
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from pydantic import HttpUrl  # noqa: E402

from src.briefing.action_brief import build_action_brief  # noqa: E402
from src.briefing.markdown_renderer import render_action_brief_markdown  # noqa: E402
from src.briefing.schemas import StartupActionBrief  # noqa: E402
from src.evaluation.answer_quality_eval import evaluate_answer_quality  # noqa: E402
from src.evaluation.answer_quality_schemas import (  # noqa: E402
    AnswerQualityEvalCase,
    AnswerQualityEvalResult,
)
from src.extraction.schemas import (  # noqa: E402
    ConfidenceLevel,
    Evidence,
    SourceType,
    StartupProfile,
)
from src.pipeline.run_pipeline import run_full_pipeline  # noqa: E402
from src.rag.embeddings import MockEmbeddingProvider  # noqa: E402
from src.rag.retrieval import build_default_index  # noqa: E402
from src.rag.schemas import PackingConfig, RerankingConfig  # noqa: E402
from src.rag.vector_store import InMemoryVectorStore  # noqa: E402

DEFAULT_FORBIDDEN_ABSOLUTE = [
    "guaranteed",
    "always",
    "never",
    "proves",
    "will definitely",
    "100%",
]


# ---------------------------------------------------------------------------
# Report schema
# ---------------------------------------------------------------------------


@dataclass
class DemoRunReport:
    run_id: str
    started_at: str
    finished_at: str = ""
    input_file: str = ""
    startup_name: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, str | None] = field(default_factory=dict)
    pipeline_summary: dict[str, Any] = field(default_factory=dict)
    answer_quality_eval: dict[str, Any] | None = None
    status: str = "running"


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------


def load_demo_input(path: Path) -> dict[str, Any]:
    """Load and validate the sample startup input JSON."""
    if not path.exists():
        _input_error(f"Input file not found: {path}")
    if path.is_dir():
        _input_error(
            f"Input path is a directory, not a file: {path}\n"
            f"  Use --input examples/demo/sample_startup_input.json"
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except PermissionError:
        _input_error(f"Permission denied reading: {path}")
    except json.JSONDecodeError as exc:
        _input_error(f"Invalid JSON in input file: {exc}")
    required = ["startup_name", "profile", "evidence"]
    missing = [r for r in required if r not in raw]
    if missing:
        _input_error(f"Input file missing required fields: {missing}")
    return raw


def _input_error(msg: str) -> None:
    """Print an input error and exit."""
    print(f"ERROR: {msg}", file=sys.stderr)
    print(file=sys.stderr)
    print("  Usage: python scripts/run_startup_radar_demo.py", file=sys.stderr)
    print("    --input examples/demo/sample_startup_input.json", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Build pipeline inputs
# ---------------------------------------------------------------------------


def build_profile(
    startup_name: str,
    raw: dict[str, Any],
) -> StartupProfile:
    """Build a StartupProfile from the demo input."""
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


def build_evidence(raw: dict[str, Any]) -> list[Evidence]:
    """Build evidence list from the demo input."""
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


def build_rag_dependencies(
    rag_backend: str,
) -> tuple[Any, Any, Any]:
    """Build chunk_index, embedding_model, vector_store for RAG.

    Returns (chunk_index, embedding_model, vector_store).
    embedding_model and vector_store are None for lexical fallback.
    """
    chunk_index = build_default_index()
    if not chunk_index.chunks:
        print("  WARNING: Corpus is empty. RAG will run with no context.")
        return chunk_index, None, None

    if rag_backend == "local":
        print("  RAG backend: local (InMemoryVectorStore + MockEmbeddingProvider)")
        embedding_model = MockEmbeddingProvider()
        vector_store: Any = InMemoryVectorStore()
    elif rag_backend == "qdrant":
        print("  RAG backend: Qdrant")
        try:
            from src.rag.qdrant_store import QdrantConfig, QdrantConnectionError, QdrantStore

            embedding_model = MockEmbeddingProvider()
            config = QdrantConfig(collection_name="nvidia_corpus")
            store = QdrantStore(config=config)
            store._ensure_client()
            vector_store = store
            print("  Connected to Qdrant successfully.")
        except QdrantConnectionError as exc:
            print(
                f"  ERROR: Cannot connect to Qdrant: {exc}",
                file=sys.stderr,
            )
            print(
                "  HINT: Start Qdrant with: docker compose up -d qdrant",
                file=sys.stderr,
            )
            sys.exit(1)
        except ImportError:
            print(
                "  ERROR: qdrant-client is not installed. " "Install it with: pip install -e .",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        print(f"  ERROR: Unknown RAG backend: {rag_backend}", file=sys.stderr)
        sys.exit(1)

    return chunk_index, embedding_model, vector_store


# ---------------------------------------------------------------------------
# Answer quality eval
# ---------------------------------------------------------------------------


def build_generic_quality_case(startup_name: str) -> AnswerQualityEvalCase:
    """Build a generic answer quality eval case for demo output."""
    return AnswerQualityEvalCase(
        case_id=f"demo_{startup_name}",
        description=f"Generic quality check for demo startup '{startup_name}'",
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
        forbidden_absolute_language=DEFAULT_FORBIDDEN_ABSOLUTE,
        unsupported_claim_patterns=[],
        min_rag_context_citation_coverage=0.0,
        min_startup_evidence_citation_coverage=0.0,
    )


def run_demo_quality_eval(
    brief: StartupActionBrief,
    startup_name: str,
) -> AnswerQualityEvalResult:
    """Run answer quality eval with a generic case."""
    case = build_generic_quality_case(startup_name)
    return evaluate_answer_quality(brief, case)


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_brief_markdown(brief: StartupActionBrief, path: Path) -> None:
    md = render_action_brief_markdown(brief)
    path.write_text(md, encoding="utf-8")
    print(f"  Markdown brief: {path}")


def write_brief_json(brief: StartupActionBrief, path: Path) -> None:
    path.write_text(brief.model_dump_json(indent=2), encoding="utf-8")
    print(f"  JSON brief: {path}")


def write_run_report(report: DemoRunReport, path: Path) -> None:
    path.write_text(json.dumps(asdict(report), indent=2, default=str), encoding="utf-8")
    print(f"  Run report: {path}")


def write_answer_quality_eval(
    result: AnswerQualityEvalResult,
    path: Path,
) -> None:
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    print(f"  Answer quality eval: {path}")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_demo(args: argparse.Namespace) -> None:
    started_at = datetime.now(UTC).isoformat()
    run_id = f"demo_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    output_dir = ensure_output_dir(Path(args.output_dir))

    report = DemoRunReport(
        run_id=run_id,
        started_at=started_at,
        input_file=str(args.input),
        startup_name="",
        parameters={
            "use_rag": args.use_rag,
            "rag_backend": args.rag_backend if args.use_rag else None,
            "offline": args.offline,
            "run_answer_quality_eval": args.run_answer_quality_eval,
            "format": args.format,
        },
    )

    t0 = time.perf_counter()

    # 1. Load input
    print("\nNVIDIA Startup AI Radar — Demo CLI")
    print(f"  Run ID: {run_id}")
    print(f"  Output: {output_dir}")
    print()
    print("Step 1/5: Loading input...")
    raw = load_demo_input(Path(args.input))
    startup_name = raw["startup_name"]
    report.startup_name = startup_name
    print(f"  Startup: {startup_name}")

    # 2. Build pipeline inputs
    print("Step 2/5: Building pipeline inputs...")
    profile = build_profile(startup_name, raw)
    evidence = build_evidence(raw)
    print(f"  Profile: {profile.sector}")
    print(f"  Evidence items: {len(evidence)}")

    # 3. Build RAG dependencies
    chunk_index = None
    embedding_model = None
    vector_store = None
    reranking_config = None
    packing_config = None

    if args.use_rag and not args.offline:
        print("Step 3/5: Building RAG dependencies...")
        chunk_index, embedding_model, vector_store = build_rag_dependencies(
            args.rag_backend,
        )
        reranking_config = RerankingConfig()
        packing_config = PackingConfig()
    else:
        print("Step 3/5: RAG disabled (use --use-rag to enable).")

    if args.offline:
        print("  Mode: offline (no external dependencies)")

    # 4. Run pipeline
    print("Step 4/5: Running pipeline...")
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
        print(f"  ERROR: Pipeline failed: {exc}", file=sys.stderr)
        report.status = "failed"
        report.finished_at = datetime.now(UTC).isoformat()
        write_run_report(report, output_dir / "demo_run_report.json")
        sys.exit(1)

    print(f"  Motion: {result.recommended_motion}")
    print(f"  Score: {result.final_priority_score:.1f}/100")
    gd = result.gap_diagnosis
    gaps = [g for g in (gd.diagnosed_gaps if gd else []) if g.detected]
    print(f"  Gaps detected: {len(gaps)}")
    recs = result.recommendation
    print(f"  Recommendations: {len(recs.recommendations) if recs else 0}")

    # 5. Build brief
    print("Step 5/5: Generating Startup Action Brief...")
    brief = build_action_brief(result)
    print(f"  Verdict: {brief.verdict.value}")

    # --- Exports ---
    fmt = args.format
    outputs: dict[str, str | None] = {}

    if fmt in ("markdown", "both"):
        md_path = output_dir / "startup_action_brief.md"
        write_brief_markdown(brief, md_path)
        outputs["brief_markdown"] = str(md_path)

    if fmt in ("json", "both"):
        json_path = output_dir / "startup_action_brief.json"
        write_brief_json(brief, json_path)
        outputs["brief_json"] = str(json_path)

    # Run report
    report.pipeline_summary = {
        "final_priority_score": result.final_priority_score,
        "recommended_motion": result.recommended_motion,
        "gaps_detected": len(gaps),
        "recommendations": len(recs.recommendations) if recs else 0,
        "evidence_items": len(result.evidence_used),
        "missing_evidence_items": len(result.missing_evidence),
        "rag_used": args.use_rag,
    }
    report.outputs = outputs

    # Optional: answer quality eval
    if args.run_answer_quality_eval:
        print("  Running answer quality evaluation...")
        eval_result = run_demo_quality_eval(brief, startup_name)
        eval_path = output_dir / "answer_quality_eval.json"
        write_answer_quality_eval(eval_result, eval_path)
        outputs["answer_quality_eval"] = str(eval_path)
        report.answer_quality_eval = {
            "passed": eval_result.passed,
            "status": eval_result.metrics.answer_quality_status.value,
            "case_id": eval_result.case_id,
            "unsupported_claim_count": eval_result.metrics.unsupported_claim_count,
            "forbidden_absolute_language_count": (
                eval_result.metrics.forbidden_absolute_language_count
            ),
            "required_sections_present": eval_result.metrics.required_sections_present,
        }
        status_str = "PASS" if eval_result.passed else "FAIL"
        print(f"    Answer quality: {status_str}")
        if eval_result.failure_reasons:
            for r in eval_result.failure_reasons:
                print(f"      - FAIL: {r}")
        if eval_result.warnings:
            for w in eval_result.warnings:
                print(f"      - WARN: {w}")

    elapsed = time.perf_counter() - t0
    report.finished_at = datetime.now(UTC).isoformat()
    report.status = "completed"
    write_run_report(report, output_dir / "demo_run_report.json")

    print()
    print("=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print(f"  Startup:        {startup_name}")
    print(f"  Run ID:         {run_id}")
    print(f"  Elapsed:        {elapsed:.2f}s")
    print(f"  Output dir:     {output_dir}")
    print(f"  Motion:         {result.recommended_motion}")
    print(f"  Priority Score: {result.final_priority_score:.1f}/100")
    print(f"  Status:         {report.status}")
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NVIDIA Startup AI Radar — CLI Demo End-to-End",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Basic demo:\n"
            "    python scripts/run_startup_radar_demo.py"
            " --input examples/demo/sample_startup_input.json\n\n"
            "  Offline mode (no external dependencies):\n"
            "    python scripts/run_startup_radar_demo.py --input ... --offline\n\n"
            "  With local RAG (InMemoryVectorStore):\n"
            "    python scripts/run_startup_radar_demo.py"
            " --input ... --use-rag --rag-backend local\n\n"
            "  With Qdrant RAG:\n"
            "    python scripts/run_startup_radar_demo.py"
            " --input ... --use-rag --rag-backend qdrant\n\n"
            "  With answer quality evaluation:\n"
            "    python scripts/run_startup_radar_demo.py"
            " --input ... --run-answer-quality-eval"
        ),
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to sample startup input JSON",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/demo_runs/latest",
        help="Output directory for generated files (default: data/demo_runs/latest)",
    )
    parser.add_argument(
        "--use-rag",
        action="store_true",
        help="Enable Product RAG pipeline (Step 11)",
    )
    parser.add_argument(
        "--rag-backend",
        type=str,
        choices=["qdrant", "local"],
        default="local",
        help="RAG vector store backend (default: local). Ignored without --use-rag",
    )
    parser.add_argument(
        "--run-answer-quality-eval",
        action="store_true",
        help="Run answer quality evaluation on the generated brief",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help=("Run in offline mode (no Qdrant, no external deps," " uses MockEmbeddingProvider)"),
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "json", "both"],
        default="both",
        help="Output format for brief files (default: both)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    run_demo(args)


if __name__ == "__main__":
    main()
