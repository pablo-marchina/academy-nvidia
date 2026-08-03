"""CI evaluation runner for deterministic offline quality suites.

Usage::

    python -m src.evaluation.eval_runner                  # run required suites
    python -m src.evaluation.eval_runner --suite rag      # single suite
    python -m src.evaluation.eval_runner --ci             # fail on regressions/config errors

Optional suites are reported as skipped when their test implementation is not
present. Required suites always fail fast on stale paths so CI cannot silently
claim coverage it does not execute.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from src.evaluation.result_store import BenchmarkResult, BenchmarkResultStore, MetricResult

_RESULTS_DIR = Path("data/eval_results")
_RESULTS_PATH = _RESULTS_DIR / "ci_results.jsonl"


@dataclass(frozen=True)
class SuiteDefinition:
    description: str
    pytest_args: tuple[str, ...]
    optional: bool = False


SUITES: dict[str, SuiteDefinition] = {
    "rag": SuiteDefinition(
        description="RAG retrieval metrics (hit rate, precision, recall)",
        pytest_args=(
            "tests/unit/test_rag_eval.py",
            "tests/unit/test_rag_eval_semantic.py",
            "tests/unit/test_rag_eval_reranking.py",
            "tests/unit/test_rag_retrieval_intent.py",
        ),
    ),
    "answer_quality": SuiteDefinition(
        description="Deterministic final-answer structure, evidence, and citation quality",
        pytest_args=("tests/evals/test_answer_quality_golden.py",),
    ),
    "gap_diagnosis": SuiteDefinition(
        description="Gap diagnosis baseline accuracy",
        pytest_args=("tests/evals/test_gap_diagnosis_baseline.py",),
    ),
    "scraping": SuiteDefinition(
        description="Scraping baseline extraction quality",
        pytest_args=("tests/evals/test_scraping_baseline.py",),
    ),
    "source_evidence": SuiteDefinition(
        description="Source quality and evidence confidence calibration",
        pytest_args=("tests/evals/test_source_evidence_baseline.py",),
    ),
    "recommendation": SuiteDefinition(
        description="Recommendation engine calibration",
        pytest_args=("tests/evals/test_recommendation_baseline.py",),
    ),
    "ragas": SuiteDefinition(
        description="Optional external-judge RAGAS evaluation metrics",
        pytest_args=("tests/evals/test_ragas_eval.py",),
        optional=True,
    ),
}


def _append_result(
    store: BenchmarkResultStore,
    *,
    run_id: str,
    name: str,
    status: str,
    exit_code: int | None = None,
    error: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    metrics = []
    if exit_code is not None:
        metrics.append(
            MetricResult(
                name="exit_code",
                value=exit_code,
                unit="code",
                higher_is_better=False,
            )
        )
    store.append(
        BenchmarkResult(
            run_id=run_id,
            candidate_id=name,
            candidate_name=name,
            dataset_id="pytest",
            status=status,
            metrics=metrics,
            error=error,
            metadata=metadata or {},
        )
    )


def _missing_paths(suite: SuiteDefinition) -> list[str]:
    return [path for path in suite.pytest_args if not Path(path).is_file()]


def run_suite(name: str, store: BenchmarkResultStore, ci_mode: bool = False) -> bool:
    suite = SUITES.get(name)
    if suite is None:
        print(f"  UNKNOWN SUITE: {name}")
        return False

    print(f"\n{'=' * 60}")
    print(f"Suite: {name} — {suite.description}")
    print(f"{'=' * 60}")

    run_id = f"{name}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    missing = _missing_paths(suite)
    if missing:
        missing_text = ", ".join(missing)
        if suite.optional:
            print(f"  Status: SKIPPED — optional test implementation missing: {missing_text}")
            _append_result(
                store,
                run_id=run_id,
                name=name,
                status="skipped",
                metadata={"missing_paths": missing, "optional": True},
            )
            return True

        error = f"Required suite references missing test files: {missing_text}"
        print(f"  Status: MISCONFIGURED — {error}")
        _append_result(
            store,
            run_id=run_id,
            name=name,
            status="failed",
            exit_code=4,
            error=error,
            metadata={"missing_paths": missing, "optional": False},
        )
        return not ci_mode

    pytest_args = [*suite.pytest_args, "--tb=short", "-q"]

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", *pytest_args],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        passed = result.returncode == 0
        status = "passed" if passed else "failed"
        print(result.stdout[-2000:] if result.stdout else "")
        if result.stderr:
            print(result.stderr[-2000:])

        _append_result(
            store,
            run_id=run_id,
            name=name,
            status=status,
            exit_code=result.returncode,
            metadata={
                "stdout_len": len(result.stdout),
                "stderr_len": len(result.stderr),
                "test_paths": list(suite.pytest_args),
            },
        )
        print(f"  Status: {status.upper()} (exit code {result.returncode})")
        if ci_mode and not passed:
            return False
        return True
    except subprocess.TimeoutExpired:
        print("  TIMEOUT after 600s")
        _append_result(
            store,
            run_id=run_id,
            name=name,
            status="failed",
            error="Timeout (600s)",
        )
        return not ci_mode
    except Exception as exc:
        print(f"  FAILED: {exc}")
        _append_result(
            store,
            run_id=run_id,
            name=name,
            status="failed",
            error=str(exc),
        )
        return not ci_mode


def main() -> None:
    parser = argparse.ArgumentParser(description="CI eval runner")
    parser.add_argument("--suite", choices=[*SUITES.keys(), "all"], default="all")
    parser.add_argument("--ci", action="store_true", help="Fail on regressions or missing required suites")
    args = parser.parse_args()

    store = BenchmarkResultStore(_RESULTS_PATH)
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    suites_to_run = list(SUITES) if args.suite == "all" else [args.suite]
    all_passed = True

    for name in suites_to_run:
        if not run_suite(name, store, ci_mode=args.ci):
            all_passed = False

    print(f"\n{'=' * 60}")
    print(f"Results saved to: {_RESULTS_PATH}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
