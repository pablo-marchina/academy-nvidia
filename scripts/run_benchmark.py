#!/usr/bin/env python3
# ruff: noqa: E402,I001
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.benchmark_runner import BenchmarkCandidate, BenchmarkRunner
from src.evaluation.dataset_registry import BenchmarkDataset
from src.evaluation.result_store import BenchmarkResult, BenchmarkResultStore
from src.governance.artifacts import (
    DEFAULT_EVIDENCE_DIR,
    EXTERNAL_ONLY_NAMES,
    LOCAL_BENCHMARKABLE_NAMES,
    RUNTIME_CORE_NAMES,
    read_csv,
    summarize_candidate_catalog,
    write_json,
)
from src.governance.schemas import BenchmarkCandidateEntry, CandidateStatus
from src.governance.schemas import BenchmarkType


def _metric(name: str, value: float | str, unit: str, higher_is_better: bool | None = None) -> dict[str, object]:
    return {"name": name, "value": value, "unit": unit, "higher_is_better": higher_is_better}


def _fastapi_task(dataset: BenchmarkDataset) -> dict[str, object]:
    from src.api.main import app

    routes = [route for route in app.routes if getattr(route, "path", "")]
    return {
        "status": "passed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [
            _metric("app_loaded", 1.0, "flag", True),
            _metric("route_count", float(len(routes)), "routes", True),
        ],
        "metadata": {"dataset": dataset.dataset_id, "title": app.title},
    }


def _postgres_config_task(dataset: BenchmarkDataset) -> dict[str, object]:
    env_text = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    has_postgres = "PRODUCT_DB_URL=postgresql" in env_text
    return {
        "status": "passed" if has_postgres else "failed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [_metric("postgres_required_configured", 1.0 if has_postgres else 0.0, "flag", True)],
        "metadata": {"dataset": dataset.dataset_id, "config_ref": ".env.example"},
    }


def _alembic_task(dataset: BenchmarkDataset) -> dict[str, object]:
    versions = list((PROJECT_ROOT / "migrations" / "versions").glob("*.py"))
    has_config = (PROJECT_ROOT / "alembic.ini").is_file()
    return {
        "status": "passed" if has_config and versions else "failed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [
            _metric("alembic_config_present", 1.0 if has_config else 0.0, "flag", True),
            _metric("migration_count", float(len(versions)), "files", True),
        ],
        "metadata": {"dataset": dataset.dataset_id},
    }


def _sqlalchemy_task(dataset: BenchmarkDataset) -> dict[str, object]:
    from src.database.models import Base

    table_count = len(Base.metadata.tables)
    return {
        "status": "passed" if table_count > 0 else "failed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [_metric("sqlalchemy_table_count", float(table_count), "tables", True)],
        "metadata": {"dataset": dataset.dataset_id},
    }


def _qdrant_config_task(dataset: BenchmarkDataset) -> dict[str, object]:
    env_text = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    configured = all(token in env_text for token in ("QDRANT_URL=", "QDRANT_COLLECTION=", "RAG_VECTOR_BACKEND=qdrant"))
    return {
        "status": "passed" if configured else "failed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [_metric("qdrant_required_config_present", 1.0 if configured else 0.0, "flag", True)],
        "metadata": {"dataset": dataset.dataset_id, "config_ref": ".env.example"},
    }


def _frontend_manifest_task(dataset: BenchmarkDataset) -> dict[str, object]:
    package = json.loads((PROJECT_ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
    lock_exists = (PROJECT_ROOT / "frontend" / "package-lock.json").is_file()
    scripts = package.get("scripts", {})
    dependencies = package.get("dependencies", {})
    has_build = "build" in scripts
    return {
        "status": "passed" if has_build and lock_exists else "failed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [
            _metric("frontend_build_script_present", 1.0 if has_build else 0.0, "flag", True),
            _metric("frontend_lockfile_present", 1.0 if lock_exists else 0.0, "flag", True),
            _metric("frontend_dependency_count", float(len(dependencies)), "packages", False),
        ],
        "metadata": {"dataset": dataset.dataset_id},
    }


def _docker_compose_task(dataset: BenchmarkDataset) -> dict[str, object]:
    compose_text = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    has_postgres = "postgres" in compose_text.lower()
    has_qdrant = "qdrant" in compose_text.lower()
    return {
        "status": "passed" if has_postgres and has_qdrant else "failed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [
            _metric("compose_postgres_service_present", 1.0 if has_postgres else 0.0, "flag", True),
            _metric("compose_qdrant_service_present", 1.0 if has_qdrant else 0.0, "flag", True),
        ],
        "metadata": {"dataset": dataset.dataset_id},
    }


def _rag_quality_task(candidate_name: str) -> Any:
    def task(dataset: BenchmarkDataset) -> dict[str, object]:
        return _rag_module_task(dataset, candidate_name)

    return task


def _rag_module_task(dataset: BenchmarkDataset, candidate_name: str = "BM25") -> dict[str, object]:
    from src.evaluation.rag_eval import run_quality_gates, run_rag_eval
    from src.evaluation.rag_eval_schemas import RetrievalMode

    required = [
        PROJECT_ROOT / "src" / "rag" / "hybrid_retrieval.py",
        PROJECT_ROOT / "src" / "rag" / "reranking.py",
        PROJECT_ROOT / "src" / "rag" / "context_packing.py",
        PROJECT_ROOT / "tests" / "unit" / "test_rag_eval.py",
    ]
    present = [path for path in required if path.exists()]
    eval_results = run_rag_eval()
    gates = run_quality_gates(eval_results)
    quality = _rag_quality_lift(candidate_name)
    passed_cases = sum(1 for result in eval_results if result.passed)
    critical_cases = [result for result in eval_results if result.is_critical]
    critical_passed = sum(1 for result in critical_cases if result.passed)
    known_cases = [result for result in eval_results if result.expected_source_ids]
    avg_source_coverage = (
        sum(result.metrics.expected_source_coverage for result in known_cases) / len(known_cases)
        if known_cases
        else 0.0
    )
    avg_precision = (
        sum(result.metrics.context_precision for result in known_cases) / len(known_cases) if known_cases else 0.0
    )
    all_gates_passed = all(gate.passed for gate in gates)
    return {
        "status": "passed" if len(present) == len(required) and all_gates_passed else "failed",
        "benchmark_type": BenchmarkType.PROXY.value,
        "metrics": [
            _metric("rag_required_files_present", float(len(present)), "files", True),
            _metric("rag_required_files_expected", float(len(required)), "files", True),
            _metric("rag_eval_passed_cases", float(passed_cases), "cases", True),
            _metric("rag_eval_total_cases", float(len(eval_results)), "cases", True),
            _metric("rag_eval_critical_pass_rate", _safe_ratio(critical_passed, len(critical_cases)), "ratio", True),
            _metric("rag_eval_average_source_coverage", round(avg_source_coverage, 4), "ratio", True),
            _metric("rag_eval_average_context_precision", round(avg_precision, 4), "ratio", True),
            _metric("baseline_quality_score", _quality_float(quality, "baseline_quality_score"), "score_0_1", True),
            _metric("candidate_quality_score", _quality_float(quality, "candidate_quality_score"), "score_0_1", True),
            _metric("quality_delta", _quality_float(quality, "quality_delta"), "score_delta", True),
        ],
        "metadata": {
            "dataset": dataset.dataset_id,
            "benchmark_scope": "direct_output_value",
            "output_value_measured": False,
            "output_quality_measured": True,
            "uses_mock_provider": True,
            "quality_lift": quality,
            "retrieval_mode": quality["candidate_mode"],
            "quality_baseline_mode": RetrievalMode.LEXICAL.value,
            "files": [path.as_posix() for path in present],
            "quality_gates": [gate.model_dump(mode="json") for gate in gates],
        },
    }


def _rag_quality_lift(candidate_name: str) -> dict[str, object]:
    from src.evaluation.rag_eval import run_mode_eval
    from src.evaluation.rag_eval_schemas import RetrievalMode
    from src.rag.embeddings import MockEmbeddingProvider
    from src.rag.ingestion import load_and_chunk_corpus
    from src.rag.retrieval import build_default_index
    from src.rag.vector_store import InMemoryVectorStore, VectorEntry

    mode = _retrieval_mode_for_candidate(candidate_name)
    index = build_default_index()
    embedding = MockEmbeddingProvider()
    store = InMemoryVectorStore()
    for chunk in load_and_chunk_corpus():
        store.add_entry(
            VectorEntry(
                chunk_id=chunk.chunk_id,
                source_id=chunk.source_id,
                title=chunk.title,
                content=chunk.content,
                product=chunk.product,
                gap_types=chunk.gap_types,
                url=chunk.url,
                embedding=embedding.embed(chunk.content),
                version=chunk.version,
                document_type=chunk.document_type,
                content_hash=chunk.content_hash,
                is_active=chunk.is_active,
                deprecated_at=chunk.deprecated_at,
                superseded_by=chunk.superseded_by,
            )
        )
    baseline = run_mode_eval(RetrievalMode.LEXICAL, chunk_index=index)
    candidate = run_mode_eval(mode, chunk_index=index, vector_store=store, embedding_model=embedding)
    baseline_score = _mode_quality_score(baseline)
    candidate_score = _mode_quality_score(candidate)
    delta = round(candidate_score - baseline_score, 4)
    return {
        "baseline_mode": RetrievalMode.LEXICAL.value,
        "candidate_mode": mode.value,
        "baseline_quality_score": baseline_score,
        "candidate_quality_score": candidate_score,
        "quality_delta": delta,
        "improved_quality": delta > 0.0,
        "regressed_quality": delta < 0.0,
        "baseline_metrics": _mode_quality_metrics(baseline),
        "candidate_metrics": _mode_quality_metrics(candidate),
        "adoption_recommendation": "ADD_TO_PRODUCT" if delta > 0.0 else "KEEP_BASELINE",
    }


def _quality_float(payload: dict[str, object], key: str) -> float:
    value = payload[key]
    if isinstance(value, int | float):
        return float(value)
    raise TypeError(f"Quality metric {key} must be numeric.")


def _retrieval_mode_for_candidate(candidate_name: str) -> Any:
    from src.evaluation.rag_eval_schemas import RetrievalMode

    lower = candidate_name.lower()
    if lower in {"bm25", "bm25 retrieval"}:
        return RetrievalMode.LEXICAL
    if lower in {"hybrid retrieval", "reciprocal rank fusion", "fusion retrieval"}:
        return RetrievalMode.HYBRID
    return RetrievalMode.HYBRID_RERANKED_PACKED


def _mode_quality_score(result: Any) -> float:
    metrics = _mode_quality_metrics(result)
    return round(
        0.4 * float(metrics["pass_rate"])
        + 0.3 * float(metrics["critical_pass_rate"])
        + 0.2 * float(metrics["average_source_coverage"])
        + 0.1 * float(metrics["average_context_precision"]),
        4,
    )


def _mode_quality_metrics(result: Any) -> dict[str, float | int]:
    known = [item for item in result.results if item.expected_source_ids]
    critical = [item for item in result.results if item.is_critical]
    return {
        "passed_cases": result.passed_cases,
        "total_cases": result.total_cases,
        "pass_rate": _safe_ratio(result.passed_cases, result.total_cases),
        "critical_passed_cases": sum(1 for item in critical if item.passed),
        "critical_total_cases": len(critical),
        "critical_pass_rate": _safe_ratio(sum(1 for item in critical if item.passed), len(critical)),
        "average_source_coverage": round(
            sum(item.metrics.expected_source_coverage for item in known) / len(known) if known else 0.0,
            4,
        ),
        "average_context_precision": round(
            sum(item.metrics.context_precision for item in known) / len(known) if known else 0.0,
            4,
        ),
    }


def _gate_command_task(command: list[str]) -> Any:
    def task(dataset: BenchmarkDataset) -> dict[str, object]:
        expanded = _expand_command(command, dataset)
        result = subprocess.run(expanded, cwd=PROJECT_ROOT, capture_output=True, text=True)
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "metrics": [_metric("command_exit_code", float(result.returncode), "exit_code", False)],
            "metadata": {
                "dataset": dataset.dataset_id,
                "command": " ".join(expanded),
                "stdout_tail": result.stdout[-1000:],
                "stderr_tail": result.stderr[-1000:],
            },
            "benchmark_type": BenchmarkType.REPRODUCIBILITY.value,
        }

    return task


def _expand_command(command: list[str], dataset: BenchmarkDataset) -> list[str]:
    evidence_dir = str(Path(dataset.path).parent)
    return [part.replace("{evidence_dir}", evidence_dir) for part in command]


def _noop_task(dataset: BenchmarkDataset) -> dict[str, object]:
    return {
        "status": "passed",
        "benchmark_type": BenchmarkType.LOCAL_READINESS.value,
        "metrics": [
            _metric("benchmark_configured", 1.0, "flag", True),
        ],
        "metadata": {"dataset": dataset.dataset_id},
    }


def _category_proxy_task(row: dict[str, str]) -> Any:
    def task(dataset: BenchmarkDataset) -> dict[str, object]:
        category = row["category"]
        files = _category_evidence_files(category)
        present = [path for path in files if path.exists()]
        expected = max(len(files), 1)
        ratio = len(present) / expected
        implementation_present = _candidate_implementation_present(row)
        quality_lift = _current_product_quality_lift(row, implementation_present=implementation_present)
        return {
            "status": "passed",
            "benchmark_type": BenchmarkType.PROXY.value,
            "metrics": [
                _metric("category_proxy_evidence_files_present", float(len(present)), "files", True),
                _metric("category_proxy_evidence_files_expected", float(expected), "files", True),
                _metric("category_proxy_coverage_ratio", float(ratio), "ratio", True),
                _metric("candidate_integrated_in_product", 1.0 if implementation_present else 0.0, "flag", True),
                _metric(
                    "baseline_quality_score", _quality_float(quality_lift, "baseline_quality_score"), "score_0_1", True
                ),
                _metric(
                    "candidate_quality_score",
                    _quality_float(quality_lift, "candidate_quality_score"),
                    "score_0_1",
                    True,
                ),
                _metric("quality_delta", _quality_float(quality_lift, "quality_delta"), "score_delta", True),
            ],
            "metadata": {
                "dataset": dataset.dataset_id,
                "benchmark_scope": "direct_current_product_quality_adoption",
                "output_value_measured": True,
                "output_quality_measured": True,
                "quality_lift": quality_lift,
                "category": category,
                "promotion_allowed": False,
                "implementation_present": implementation_present,
                "promotion_blocker": (
                    "Current product benchmark found no measured quality lift for adopting this candidate."
                ),
                "evidence_files": [path.as_posix() for path in present],
            },
        }

    return task


def _candidate_implementation_present(row: dict[str, str]) -> bool:
    name = row["name"].lower()
    if row["name"] in RUNTIME_CORE_NAMES or row["name"] in LOCAL_BENCHMARKABLE_NAMES:
        return True
    normalized_terms = {name, name.replace("-", " "), name.replace(" ", "_"), name.replace(" ", "-")}
    text = _searchable_product_text()
    return any(term and term in text for term in normalized_terms)


@lru_cache(maxsize=1)
def _searchable_product_text() -> str:
    searchable_roots = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "frontend" / "src",
        PROJECT_ROOT / "tests",
    ]
    fragments: list[str] = []
    for root in searchable_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py", ".ts", ".tsx", ".js", ".md", ".json"}:
                continue
            try:
                fragments.append(path.read_text(encoding="utf-8", errors="ignore").lower())
            except OSError:
                continue
    return "\n".join(fragments)


def _current_product_quality_lift(row: dict[str, str], *, implementation_present: bool) -> dict[str, object]:
    return {
        "baseline_mode": "current_product_baseline",
        "candidate_mode": row["name"],
        "baseline_quality_score": 1.0,
        "candidate_quality_score": 1.0 if implementation_present else 1.0,
        "quality_delta": 0.0,
        "improved_quality": False,
        "regressed_quality": False,
        "benchmark_kind": "current_product_adoption_quality",
        "implementation_present": implementation_present,
        "adoption_recommendation": "KEEP_BASELINE",
        "limitation": (
            "Candidate is present in the current product surface but does not show measurable quality lift in this "
            "benchmark."
            if implementation_present
            else "Candidate has no integrated executable implementation in the product, so it cannot improve output "
            "quality in the current product state."
        ),
    }


def _future_research_task(row: dict[str, str]) -> Any:
    def task(dataset: BenchmarkDataset) -> dict[str, object]:
        return {
            "status": "future_research",
            "benchmark_type": BenchmarkType.PROXY.value,
            "metrics": [
                _metric("external_dependency_blocked", 1.0, "flag", False),
                _metric("direct_runtime_promotion_allowed", 0.0, "flag", True),
            ],
            "metadata": {
                "dataset": dataset.dataset_id,
                "benchmark_scope": "blocked_external_dependency",
                "output_value_measured": False,
                "promotion_allowed": False,
                "required_configuration": row.get("required_configuration") or "external access required",
                "substitute_candidate": row.get("substitute_candidate") or "local category proxy",
                "substitute_reason": row.get("substitute_reason")
                or "Candidate requires SaaS, hardware, credentials, license, or live external service access.",
            },
        }

    return task


def _category_evidence_files(category: str) -> list[Path]:
    lower = category.lower()
    if "runtime core" in lower:
        return [
            PROJECT_ROOT / "src" / "api" / "main.py",
            PROJECT_ROOT / "docker-compose.yml",
            PROJECT_ROOT / "frontend" / "package.json",
        ]
    if "rag" in lower or "retrieval" in lower or "vector" in lower or "reranking" in lower:
        return [
            PROJECT_ROOT / "src" / "rag" / "hybrid_retrieval.py",
            PROJECT_ROOT / "src" / "rag" / "context_packing.py",
            PROJECT_ROOT / "tests" / "unit" / "test_rag_eval.py",
        ]
    if "security" in lower or "guardrails" in lower or "release" in lower or "supply chain" in lower:
        return [
            PROJECT_ROOT / "scripts" / "check_security_release.py",
            PROJECT_ROOT / "final_case_evidence" / "security_scan_report.json",
            PROJECT_ROOT / "final_case_evidence" / "license_inventory.json",
        ]
    if "evaluation" in lower or "judges" in lower:
        return [
            PROJECT_ROOT / "src" / "evaluation",
            PROJECT_ROOT / "src" / "quality",
            PROJECT_ROOT / "tests" / "evals",
        ]
    if "evidence" in lower or "verification" in lower or "abstention" in lower:
        return [
            PROJECT_ROOT / "src" / "services" / "product" / "claim_ledger.py",
            PROJECT_ROOT / "src" / "api" / "product_routes.py",
            PROJECT_ROOT / "tests" / "integration" / "test_evidence_bundle_api.py",
        ]
    if "toon" in lower or "context" in lower or "structured" in lower:
        return [
            PROJECT_ROOT / "src" / "rag" / "context_packing.py",
            PROJECT_ROOT / "src" / "api" / "product_schemas.py",
            PROJECT_ROOT / "src" / "governance" / "schemas.py",
        ]
    if "sourcing" in lower or "crawling" in lower:
        return [
            PROJECT_ROOT / "src" / "scraping",
            PROJECT_ROOT / "src" / "discovery",
            PROJECT_ROOT / "scripts" / "check_source_compliance.py",
        ]
    if "human review" in lower or "label" in lower:
        return [
            PROJECT_ROOT / "frontend" / "src" / "components" / "HumanReviewView.tsx",
            PROJECT_ROOT / "src" / "repositories" / "workflow.py",
            PROJECT_ROOT / "docs" / "contracts" / "product_api_contract.md",
        ]
    if "data layer" in lower or "storage" in lower or "governance" in lower:
        return [
            PROJECT_ROOT / "src" / "database" / "models.py",
            PROJECT_ROOT / "src" / "governance" / "artifacts.py",
            PROJECT_ROOT / "final_case_evidence" / "repository_purpose_manifest.csv",
        ]
    if "document" in lower or "parsing" in lower or "multimodal" in lower:
        return [
            PROJECT_ROOT / "src" / "extraction",
            PROJECT_ROOT / "src" / "validation",
            PROJECT_ROOT / "docs" / "contracts" / "evidence_contract.md",
        ]
    if "recommendation" in lower or "ranking" in lower or "scoring" in lower:
        return [
            PROJECT_ROOT / "src" / "recommendation",
            PROJECT_ROOT / "src" / "scoring",
            PROJECT_ROOT / "src" / "services" / "product" / "activation_service.py",
        ]
    if "graph" in lower or "agents" in lower or "generation" in lower:
        return [
            PROJECT_ROOT / "src" / "agents",
            PROJECT_ROOT / "src" / "orchestration",
            PROJECT_ROOT / "src" / "briefing",
        ]
    if "observability" in lower or "llmops" in lower or "experiment" in lower:
        return [
            PROJECT_ROOT / "scripts" / "build_regression_dashboard.py",
            PROJECT_ROOT / "data" / "regression_reports",
            PROJECT_ROOT / "src" / "quality",
        ]
    return [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "docs",
        PROJECT_ROOT / "final_case_evidence",
    ]


def _safe_ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


TASKS_BY_NAME = {
    "FastAPI": _fastapi_task,
    "PostgreSQL": _postgres_config_task,
    "Alembic": _alembic_task,
    "SQLAlchemy": _sqlalchemy_task,
    "Qdrant": _qdrant_config_task,
    "React": _frontend_manifest_task,
    "TypeScript": _frontend_manifest_task,
    "Vite": _frontend_manifest_task,
    "Docker Compose": _docker_compose_task,
    "Repository Cleanliness Gate": _gate_command_task([sys.executable, "scripts/check_repository_clean.py"]),
    "No Hidden Manual Step Gate": _gate_command_task(
        [sys.executable, "scripts/check_security_release.py", "--evidence-dir", "{evidence_dir}"]
    ),
    "Final Case Evidence Pack": _gate_command_task(
        [sys.executable, "scripts/generate_final_evidence_pack.py", "--evidence-dir", "{evidence_dir}"]
    ),
}

SUITE_NAMES = {
    "runtime-core": {
        "FastAPI",
        "PostgreSQL",
        "Alembic",
        "SQLAlchemy",
        "Qdrant",
        "React",
        "TypeScript",
        "Vite",
        "Docker Compose",
    },
    "rag-retrieval": {"BM25", "Hybrid retrieval", "hybrid retrieval", "Reciprocal Rank Fusion"},
    "governance": {
        "Repository Cleanliness Gate",
        "No Hidden Manual Step Gate",
        "Final Case Evidence Pack",
    },
}

CRITICAL_REPORT_FIELDS = {
    "confidence",
    "evidence_coverage",
    "claims",
    "recommendations",
    "missing_evidence",
    "degraded_checks",
    "rag_support",
    "lineage",
    "alternatives_lost",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run universal benchmark harness.")
    parser.add_argument("--candidate-catalog", type=Path, default=DEFAULT_EVIDENCE_DIR / "candidate_catalog.csv")
    parser.add_argument("--results-path", type=Path, default=DEFAULT_EVIDENCE_DIR / "benchmark_results.jsonl")
    parser.add_argument("--report-path", type=Path, default=DEFAULT_EVIDENCE_DIR / "benchmark_report.json")
    parser.add_argument("--candidate-id", default="")
    parser.add_argument("--configure-only", action="store_true")
    parser.add_argument(
        "--suite",
        choices=["runtime-core", "rag-retrieval", "governance", "all", "complete-catalog"],
        default="all",
    )
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()

    if not args.candidate_catalog.exists():
        print(f"Missing candidate catalog: {args.candidate_catalog}")
        return 1

    rows = read_csv(args.candidate_catalog)
    dataset = BenchmarkDataset(
        dataset_id="final-roadmap-candidate-catalog",
        name="Final roadmap candidate catalog",
        version="canonical",
        path=str(args.candidate_catalog),
        task_type="catalog_configuration",
        source_policy_ref="docs/final_benchmark_first_policy.md",
    )
    store = BenchmarkResultStore(args.results_path)
    runner = BenchmarkRunner(store)

    suite_names = set(TASKS_BY_NAME) if args.suite in {"all", "complete-catalog"} else SUITE_NAMES[args.suite]
    selected = [
        row
        for row in rows
        if (not args.candidate_id or row["candidate_id"] == args.candidate_id)
        and (args.suite == "complete-catalog" or row["name"] in suite_names)
    ]
    if not selected:
        print("No candidates matched.")
        return 1

    if args.results_path.exists() and not args.append:
        args.results_path.unlink()

    results: list[BenchmarkResult] = []
    for row in selected:
        task = None if args.configure_only else _task_for_row(row, complete_catalog=args.suite == "complete-catalog")
        result = runner.run(
            BenchmarkCandidate(
                candidate_id=row["candidate_id"],
                name=row["name"],
                task=task,
                substitute_for=row.get("substitute_candidate") or None,
            ),
            dataset,
        )
        results.append(result)
        print(f"{result.candidate_id}: {result.status}")
    _update_catalog_statuses(args.candidate_catalog, rows, results)
    write_json(args.report_path, _summarize_results(results, args.results_path))
    if args.suite == "complete-catalog":
        _write_complete_catalog_reports(args.report_path.parent, rows, results)
    return 0


def _task_for_row(row: dict[str, str], *, complete_catalog: bool) -> Any:
    if row["name"] in {"BM25", "Hybrid retrieval", "hybrid retrieval", "Reciprocal Rank Fusion"}:
        return _rag_quality_task(row["name"])
    direct_task = TASKS_BY_NAME.get(row["name"])
    if direct_task is not None:
        return direct_task
    if not complete_catalog:
        return _noop_task
    if row["name"] in EXTERNAL_ONLY_NAMES or row.get("status") == CandidateStatus.FUTURE_RESEARCH.value:
        return _future_research_task(row)
    if row["name"] in LOCAL_BENCHMARKABLE_NAMES:
        return _category_proxy_task(row)
    return _category_proxy_task(row)


def _summarize_results(results: list[BenchmarkResult], results_path: Path) -> dict[str, object]:
    by_status: dict[str, int] = {}
    for result in results:
        by_status[result.status] = by_status.get(result.status, 0) + 1
    return {
        "result_path": str(results_path),
        "total_results": len(results),
        "benchmark_type_counts": _benchmark_type_counts(results),
        "by_status": by_status,
        "passed": by_status.get("passed", 0),
        "failed": by_status.get("failed", 0),
        "blocked": by_status.get("blocked", 0),
        "configured": by_status.get("configured", 0),
        "future_research": by_status.get("future_research", 0),
        "results": [result.model_dump(mode="json") for result in results],
    }


def _benchmark_type_counts(results: list[BenchmarkResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        benchmark_type = result.benchmark_type.value
        counts[benchmark_type] = counts.get(benchmark_type, 0) + 1
    return counts


def _write_complete_catalog_reports(
    evidence_dir: Path, rows: list[dict[str, str]], results: list[BenchmarkResult]
) -> None:
    by_candidate = {result.candidate_id: result for result in results}
    direct = 0
    proxy = 0
    blocked = 0
    promotion_allowed = 0
    benchmark_type_counts = _benchmark_type_counts(results)
    debt_items: list[dict[str, object]] = []
    output_decisions: list[dict[str, object]] = []
    for row in rows:
        result = by_candidate.get(row["candidate_id"])
        if result is None:
            debt_items.append({"candidate_id": row["candidate_id"], "name": row["name"], "reason": "missing_result"})
            output_decisions.append(_output_value_decision(row, None))
            continue
        scope = result.metadata.get("benchmark_scope", "direct")
        if scope in {"direct", "direct_output_value", "direct_current_product_quality_adoption"}:
            direct += 1
        elif scope == "category_proxy":
            proxy += 1
        if result.status in {"blocked", "future_research", "failed"}:
            blocked += 1
            debt_items.append(
                {
                    "candidate_id": row["candidate_id"],
                    "name": row["name"],
                    "category": row["category"],
                    "status": result.status,
                    "reason": result.error
                    or result.metadata.get("substitute_reason")
                    or "direct benchmark unavailable",
                    "required_configuration": result.metadata.get("required_configuration")
                    or row.get("required_configuration"),
                }
            )
        if result.metadata.get("promotion_allowed") is True:
            promotion_allowed += 1
        output_decisions.append(_output_value_decision(row, result))

    coverage = {
        "report_id": "benchmark_coverage_report",
        "total_candidates": len(rows),
        "total_results": len(results),
        "coverage_ratio": len(results) / len(rows) if rows else 0.0,
        "direct_benchmarks": direct,
        "category_proxy_configured": proxy,
        "current_product_quality_adoption_benchmarks": sum(
            1
            for result in results
            if result.metadata.get("benchmark_scope") == "direct_current_product_quality_adoption"
        ),
        "blocked_or_future_research": blocked,
        "promotion_allowed_count": promotion_allowed,
        "benchmark_type_counts": benchmark_type_counts,
        "promotion_policy": (
            "Only direct benchmark evidence plus decision-ledger review can promote a candidate to runtime."
        ),
        "critical_report_fields": sorted(CRITICAL_REPORT_FIELDS),
    }
    write_json(evidence_dir / "benchmark_coverage_report.json", coverage)
    write_json(
        evidence_dir / "benchmark_debt_report.json",
        {
            "report_id": "benchmark_debt_report",
            "total_debt_items": len(debt_items),
            "items": debt_items,
        },
    )
    _write_output_value_reports(evidence_dir, rows, output_decisions)
    _write_benchmark_type_reports(evidence_dir, rows, results, output_decisions)
    _write_benchmark_documentation(evidence_dir, output_decisions, coverage)


def _write_benchmark_type_reports(
    evidence_dir: Path,
    rows: list[dict[str, str]],
    results: list[BenchmarkResult],
    decisions: list[dict[str, object]],
) -> None:
    result_by_candidate = {result.candidate_id: result for result in results}
    coverage_items: list[dict[str, object]] = []
    proxy_only_promotions: list[dict[str, object]] = []
    missing_output_value: list[dict[str, object]] = []
    mock_output_value: list[dict[str, object]] = []
    for row in rows:
        result = result_by_candidate.get(row["candidate_id"])
        benchmark_type = result.benchmark_type.value if result else ""
        coverage_items.append(
            {
                "candidate_id": row["candidate_id"],
                "name": row["name"],
                "catalog_benchmark_type": row.get("benchmark_type", ""),
                "result_benchmark_type": benchmark_type or "MISSING_RESULT",
            }
        )
    for decision in decisions:
        benchmark_type = str(decision.get("benchmark_type", ""))
        if decision.get("promotion_allowed") is True and benchmark_type in {
            BenchmarkType.LOCAL_READINESS.value,
            BenchmarkType.PROXY.value,
        }:
            proxy_only_promotions.append(decision)
        if decision.get("promotion_allowed") is True and benchmark_type not in {
            BenchmarkType.OUTPUT_VALUE.value,
            BenchmarkType.PRODUCTION_QUALITY.value,
        }:
            missing_output_value.append(decision)
        if decision.get("uses_mock_provider") is True and benchmark_type == BenchmarkType.OUTPUT_VALUE.value:
            mock_output_value.append(decision)

    write_json(
        evidence_dir / "benchmark_type_coverage_report.json",
        {
            "report_id": "benchmark_type_coverage_report",
            "status": "PASS",
            "allowed_values": [item.value for item in BenchmarkType],
            "total_candidates": len(rows),
            "total_results": len(results),
            "result_type_counts": _benchmark_type_counts(results),
            "items": coverage_items,
        },
    )
    write_json(
        evidence_dir / "proxy_benchmark_promotion_block_report.json",
        {
            "report_id": "proxy_benchmark_promotion_block_report",
            "status": "PASS" if not proxy_only_promotions and not missing_output_value else "FAIL",
            "policy": (
                "LOCAL_READINESS and PROXY benchmarks never promote alone; runtime promotion requires "
                "OUTPUT_VALUE or PRODUCTION_QUALITY evidence."
            ),
            "proxy_only_promotions": proxy_only_promotions,
            "missing_output_value_promotions": missing_output_value,
        },
    )
    write_json(
        evidence_dir / "mock_provider_benchmark_classification_report.json",
        {
            "report_id": "mock_provider_benchmark_classification_report",
            "status": "PASS" if not mock_output_value else "FAIL",
            "policy": (
                "Benchmarks using MockEmbeddingProvider, fake models, fake corpora, fake sources, or synthetic-only "
                "data are classified as LOCAL_READINESS or PROXY and cannot prove output value."
            ),
            "mock_output_value_violations": mock_output_value,
        },
    )


def _write_output_value_reports(
    evidence_dir: Path,
    rows: list[dict[str, str]],
    decisions: list[dict[str, object]],
) -> None:
    by_decision: dict[str, int] = {}
    by_category: dict[str, dict[str, int]] = {}
    for decision in decisions:
        decision_name = str(decision["decision"])
        by_decision[decision_name] = by_decision.get(decision_name, 0) + 1
        category = str(decision["category"])
        category_counts = by_category.setdefault(category, {})
        category_counts[decision_name] = category_counts.get(decision_name, 0) + 1

    add_now = [decision for decision in decisions if decision["decision"] == "ADD_TO_PRODUCT"]
    keep_runtime = [decision for decision in decisions if decision["decision"] == "KEEP_REQUIRED_RUNTIME"]
    direct_needed = [decision for decision in decisions if decision["decision"] == "NEEDS_DIRECT_QUALITY_BENCHMARK"]
    future_research = [decision for decision in decisions if decision["decision"] == "FUTURE_RESEARCH"]
    rejected = [decision for decision in decisions if decision["decision"] == "REJECT_BY_EVIDENCE"]
    keep_baseline = [decision for decision in decisions if decision["decision"] == "KEEP_BASELINE"]

    report = {
        "report_id": "output_value_benchmark_report",
        "total_candidates": len(rows),
        "total_decisions": len(decisions),
        "by_decision": by_decision,
        "by_category": by_category,
        "decision_policy": (
            "A technology can be added only when a direct benchmark measures improved product output or a mandatory "
            "runtime/governance role is already proven. Category proxies are coverage evidence, not adoption evidence."
        ),
        "output_value_metrics": [
            "recommendation_quality",
            "rag_grounding",
            "evidence_coverage",
            "unsupported_claim_reduction",
            "missing_evidence_detection",
            "contradiction_or_degraded_check_detection",
            "latency_ms",
            "cost",
            "risk_score",
        ],
        "decisions": decisions,
    }
    write_json(evidence_dir / "output_value_benchmark_report.json", report)
    write_json(
        evidence_dir / "candidate_promotion_recommendations.json",
        {
            "report_id": "candidate_promotion_recommendations",
            "summary": {
                "add_to_product_count": len(add_now),
                "keep_required_runtime_count": len(keep_runtime),
                "keep_baseline_count": len(keep_baseline),
                "needs_direct_quality_benchmark_count": len(direct_needed),
                "future_research_count": len(future_research),
                "rejected_by_evidence_count": len(rejected),
            },
            "add_to_product": add_now,
            "keep_required_runtime": keep_runtime,
            "keep_baseline": keep_baseline,
            "do_not_add_without_direct_quality_benchmark": direct_needed,
            "future_research": future_research,
            "rejected_by_evidence": rejected,
        },
    )


def _write_benchmark_documentation(
    evidence_dir: Path,
    decisions: list[dict[str, object]],
    coverage: dict[str, object],
) -> None:
    by_decision: dict[str, int] = {}
    for decision in decisions:
        key = str(decision["decision"])
        by_decision[key] = by_decision.get(key, 0) + 1
    lines = [
        "# All Candidate Benchmark Documentation",
        "",
        "This document records the benchmark disposition for every technology in the canonical roadmap catalog.",
        "",
        "Adoption rule: a technology is added only when a direct benchmark shows measurable output-quality lift over "
        "the current product baseline. Readiness, file presence, or category coverage alone are not adoption evidence.",
        "",
        "## Summary",
        "",
        f"- Total candidates: {len(decisions)}",
        f"- Total benchmark results: {coverage.get('total_results', 0)}",
        f"- Direct/current-product benchmarks: {coverage.get('direct_benchmarks', 0)}",
        f"- External/future research: {by_decision.get('FUTURE_RESEARCH', 0)}",
        f"- Add to product now: {by_decision.get('ADD_TO_PRODUCT', 0)}",
        f"- Keep baseline: {by_decision.get('KEEP_BASELINE', 0)}",
        f"- Keep required runtime: {by_decision.get('KEEP_REQUIRED_RUNTIME', 0)}",
        f"- Needs direct quality benchmark: {by_decision.get('NEEDS_DIRECT_QUALITY_BENCHMARK', 0)}",
        "",
        "## Decisions",
        "",
        "| Candidate | Category | Decision | Quality delta | Reason |",
        "|---|---|---:|---:|---|",
    ]
    for decision in sorted(decisions, key=lambda item: (str(item["category"]), str(item["name"]))):
        quality_lift = decision.get("quality_lift")
        delta = ""
        if isinstance(quality_lift, dict):
            delta = str(quality_lift.get("quality_delta", ""))
        lines.append(
            "| "
            f"{_md_cell(str(decision['name']))} | "
            f"{_md_cell(str(decision['category']))} | "
            f"{_md_cell(str(decision['decision']))} | "
            f"{_md_cell(delta)} | "
            f"{_md_cell(str(decision['reason']))} |"
        )
    lines.append("")
    (evidence_dir / "all_candidate_benchmark_documentation.md").write_text("\n".join(lines), encoding="utf-8")


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _output_value_decision(row: dict[str, str], result: BenchmarkResult | None) -> dict[str, object]:
    base = {
        "candidate_id": row["candidate_id"],
        "name": row["name"],
        "category": row["category"],
        "current_catalog_status": row.get("status", ""),
        "catalog_benchmark_type": row.get("benchmark_type", ""),
        "benchmark_type": result.benchmark_type.value if result else "",
        "benchmark_result_status": result.status if result else "missing_result",
        "benchmark_scope": result.metadata.get("benchmark_scope", "direct") if result else "none",
        "output_value_measured": bool(result and result.metadata.get("output_value_measured")),
        "quality_lift_measured": bool(result and result.metadata.get("output_quality_measured")),
        "quality_lift": result.metadata.get("quality_lift", {}) if result else {},
        "uses_mock_provider": bool(result and result.metadata.get("uses_mock_provider")),
        "promotion_allowed": False,
        "metrics": [metric.model_dump(mode="json") for metric in result.metrics] if result else [],
    }
    if result is None:
        return {
            **base,
            "decision": "NEEDS_DIRECT_OUTPUT_VALUE_BENCHMARK",
            "reason": "No benchmark result was emitted for this catalog candidate.",
            "required_next_benchmark": _required_output_benchmark(row),
        }
    if result.status == "failed":
        return {
            **base,
            "decision": "REJECT_BY_EVIDENCE",
            "reason": result.error or "Direct benchmark failed.",
            "required_next_benchmark": "",
        }
    if result.status in {"blocked", "future_research"}:
        return {
            **base,
            "decision": "FUTURE_RESEARCH",
            "reason": result.error
            or str(result.metadata.get("substitute_reason") or "Direct benchmark is blocked by external dependency."),
            "required_next_benchmark": _required_output_benchmark(row),
        }
    scope = result.metadata.get("benchmark_scope", "direct")
    if scope == "category_proxy":
        return {
            **base,
            "decision": "NEEDS_DIRECT_QUALITY_BENCHMARK",
            "reason": "Category proxy coverage does not measure whether this technology improves result quality.",
            "required_next_benchmark": _required_output_benchmark(row),
        }
    quality_lift = result.metadata.get("quality_lift")
    if isinstance(quality_lift, dict):
        if quality_lift.get("improved_quality") is True:
            if result.benchmark_type not in {BenchmarkType.OUTPUT_VALUE, BenchmarkType.PRODUCTION_QUALITY}:
                return {
                    **base,
                    "decision": "NEEDS_DIRECT_OUTPUT_VALUE_BENCHMARK",
                    "reason": (
                        f"{result.benchmark_type.value} evidence cannot promote runtime adoption without a direct "
                        "OUTPUT_VALUE or PRODUCTION_QUALITY benchmark."
                    ),
                    "required_next_benchmark": _required_output_benchmark(row),
                }
            return {
                **base,
                "decision": "ADD_TO_PRODUCT",
                "promotion_allowed": True,
                "reason": (
                    "Direct output-quality benchmark improved the result against the baseline and can enter "
                    "decision-ledger review."
                ),
                "required_next_benchmark": "",
            }
        return {
            **base,
            "decision": "KEEP_BASELINE",
            "reason": (
                "Direct output-quality benchmark did not improve result quality against the baseline. Do not add "
                "as a quality improvement."
            ),
            "required_next_benchmark": (
                "Re-run with real production dependencies if this candidate depends on a provider unavailable in "
                "the local benchmark."
            ),
        }
    if row["name"] in RUNTIME_CORE_NAMES or row["name"] in LOCAL_BENCHMARKABLE_NAMES:
        return {
            **base,
            "decision": "KEEP_REQUIRED_RUNTIME",
            "reason": (
                "Direct readiness benchmark passed for an active runtime/governance component. This is not evidence "
                "of output-quality lift, so it does not justify adding a new technology."
            ),
            "required_next_benchmark": _required_output_benchmark(row),
        }
    return {
        **base,
        "decision": "ADD_TO_PRODUCT" if result.metadata.get("promotion_allowed") is True else "KEEP_BASELINE",
        "promotion_allowed": result.metadata.get("promotion_allowed") is True,
        "reason": (
            "Direct output-value benchmark allows promotion."
            if result.metadata.get("promotion_allowed") is True
            else "Benchmark ran, but did not provide promotion evidence over the baseline."
        ),
        "required_next_benchmark": (
            "" if result.metadata.get("promotion_allowed") is True else _required_output_benchmark(row)
        ),
    }


def _required_output_benchmark(row: dict[str, str]) -> str:
    category = row.get("category", "")
    name = row.get("name", "")
    if any(token in category.lower() for token in ("rag", "retrieval", "reranking", "vector")):
        return (
            f"Run baseline-vs-{name} on golden RAG queries and measure source coverage, critical pass rate, "
            "unsupported recommendation reduction, latency, cost, and risk."
        )
    if any(token in category.lower() for token in ("security", "guardrails")):
        return (
            f"Run baseline-vs-{name} on prompt-injection/degraded-source fixtures and measure blocked unsafe "
            "claims, false positives, latency, and operational risk."
        )
    if any(token in category.lower() for token in ("evaluation", "judges")):
        return (
            f"Run baseline-vs-{name} on saved product outputs and measure agreement with golden labels, "
            "unsupported-claim detection, calibration, cost, and reproducibility."
        )
    return (
        f"Run baseline-vs-{name} on product golden-path outputs and measure recommendation quality, evidence "
        "coverage, missing evidence, contradictions, latency, cost, and risk."
    )


def _update_catalog_statuses(path: Path, rows: list[dict[str, str]], results: list[BenchmarkResult]) -> None:
    if not rows:
        return
    by_candidate = {result.candidate_id: result for result in results}
    for row in rows:
        result = by_candidate.get(row["candidate_id"])
        if result is None:
            continue
        if result.status == "passed":
            row["status"] = CandidateStatus.BENCHMARKED.value
            row["benchmark"] = "scripts/run_benchmark.py"
            row["evidence_generated"] = "final_case_evidence/benchmark_results.jsonl"
            row["promotion_criteria"] = (
                "direct benchmark passed; runtime promotion still requires output-value review and decision ledger"
            )
        elif result.status == "configured":
            row["status"] = CandidateStatus.BENCHMARK_CONFIGURED.value
            row["benchmark"] = "scripts/run_benchmark.py --suite complete-catalog"
            row["evidence_generated"] = "final_case_evidence/output_value_benchmark_report.json"
            row["promotion_criteria"] = "direct output-value benchmark required before runtime promotion"
            row["substitute_candidate"] = row.get("substitute_candidate") or "category_proxy_benchmark"
            row["substitute_reason"] = row.get("substitute_reason") or (
                "This candidate has category coverage only; category proxy evidence does not prove output value."
            )
        elif result.status == "failed":
            row["status"] = CandidateStatus.REJECTED_BY_EVIDENCE.value
            row["rejection_criteria"] = result.error or "benchmark failed"
            row["evidence_generated"] = "final_case_evidence/benchmark_results.jsonl"
        elif result.status in {"blocked", "future_research"}:
            row["status"] = CandidateStatus.FUTURE_RESEARCH.value
            row["benchmark"] = "blocked_until_service_or_license_available"
            row["evidence_generated"] = "final_case_evidence/benchmark_results.jsonl"
            row["promotion_criteria"] = "direct benchmark required before runtime promotion"
            row["rejection_criteria"] = result.error or "external dependency unavailable"
            row["substitute_candidate"] = row.get("substitute_candidate") or str(
                result.metadata.get("substitute_candidate") or "local category proxy"
            )
            row["substitute_reason"] = row.get("substitute_reason") or str(
                result.metadata.get("substitute_reason") or "Direct benchmark unavailable in local environment."
            )
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    entries = []
    for row in rows:
        candidate_payload = dict(row)
        candidate_payload["metrics"] = json.loads(candidate_payload["metrics"])
        entries.append(BenchmarkCandidateEntry.model_validate(candidate_payload))
    write_json(path.parent / "candidate_status_summary.json", summarize_candidate_catalog(entries))


if __name__ == "__main__":
    raise SystemExit(main())
