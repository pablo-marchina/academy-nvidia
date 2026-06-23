#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.rank_value_candidates import build_ranked_queue, write_ranked_queue
from scripts.run_benchmark import _rag_quality_lift
from src.governance.artifacts import DEFAULT_EVIDENCE_DIR, read_csv, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ranked output-quality benchmarks until the stop rule fires.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_EVIDENCE_DIR / "candidate_catalog.csv")
    parser.add_argument("--queue-path", type=Path, default=DEFAULT_EVIDENCE_DIR / "ranked_value_candidate_queue.json")
    parser.add_argument("--report-path", type=Path, default=DEFAULT_EVIDENCE_DIR / "ranked_value_benchmark_report.json")
    parser.add_argument("--markdown-path", type=Path, default=DEFAULT_EVIDENCE_DIR / "ranked_value_benchmark_report.md")
    parser.add_argument("--patience", type=int, default=3)
    parser.add_argument("--min-quality-delta", type=float, default=0.01)
    parser.add_argument("--max-queue-scan", type=int, default=500)
    args = parser.parse_args()

    queue = _load_or_build_queue(args.catalog, args.queue_path)
    report = run_ranked_benchmarks(
        queue,
        patience=args.patience,
        min_quality_delta=args.min_quality_delta,
        max_queue_scan=args.max_queue_scan,
    )
    write_json(args.report_path, report)
    _write_markdown(args.markdown_path, report)
    print(
        "Ranked value benchmark completed: "
        f"{report['executed_count']} executed, {report['adopt_count']} adopted, "
        f"stop_reason={report['stop_reason']}"
    )
    return 0


def run_ranked_benchmarks(
    queue: list[dict[str, Any]],
    *,
    patience: int = 3,
    min_quality_delta: float = 0.01,
    max_queue_scan: int = 80,
) -> dict[str, Any]:
    decisions: list[dict[str, Any]] = []
    executed = 0
    consecutive_no_lift = 0
    stop_reason = "QUEUE_EXHAUSTED"

    for index, item in enumerate(queue[:max_queue_scan], start=1):
        if consecutive_no_lift >= patience:
            decisions.append(_not_run_decision(index, item, "STOPPED_BEFORE_BENCHMARK"))
            stop_reason = f"NO_QUALITY_LIFT_IN_LAST_{patience}_EXECUTABLE_BENCHMARKS"
            continue
        if not item.get("executable"):
            decisions.append(_implementation_required_decision(index, item))
            continue

        executed += 1
        decision = _run_executable_decision(
            index,
            item,
            min_quality_delta=min_quality_delta,
        )
        decisions.append(decision)
        if decision["decision"] == "ADOPT":
            consecutive_no_lift = 0
        else:
            consecutive_no_lift += 1

    if consecutive_no_lift >= patience:
        stop_reason = f"NO_QUALITY_LIFT_IN_LAST_{patience}_EXECUTABLE_BENCHMARKS"
    scanned = min(len(queue), max_queue_scan)
    return {
        "report_id": "ranked_value_benchmark_report",
        "generated_at": datetime.now(UTC).isoformat(),
        "ranking_policy": (
            "Benchmark candidates are evaluated in ranked order. Non-executable candidates are implementation "
            "backlog. Execution stops after consecutive executable candidates fail to improve output quality."
        ),
        "stop_rule": {
            "patience": patience,
            "min_quality_delta": min_quality_delta,
            "max_queue_scan": max_queue_scan,
        },
        "stop_reason": stop_reason,
        "scanned_count": scanned,
        "executed_count": executed,
        "adopt_count": sum(1 for decision in decisions if decision["decision"] == "ADOPT"),
        "reject_no_lift_count": sum(1 for decision in decisions if decision["decision"] == "REJECT_NO_LIFT"),
        "implementation_required_count": sum(
            1 for decision in decisions if decision["decision"] == "IMPLEMENTATION_REQUIRED"
        ),
        "stopped_before_benchmark_count": sum(
            1 for decision in decisions if decision["decision"] == "STOPPED_BEFORE_BENCHMARK"
        ),
        "decisions": decisions,
    }


def _load_or_build_queue(catalog: Path, queue_path: Path) -> list[dict[str, Any]]:
    if queue_path.exists():
        payload = json.loads(queue_path.read_text(encoding="utf-8"))
        items = payload.get("items", [])
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
    rows = read_csv(catalog)
    queue = build_ranked_queue(rows)
    write_ranked_queue(
        queue_path,
        queue_path.with_suffix(".md"),
        queue,
    )
    return queue


def _run_executable_decision(
    rank: int,
    item: dict[str, Any],
    *,
    min_quality_delta: float,
) -> dict[str, Any]:
    if item.get("benchmark_key") != "rag_mode_quality":
        return _implementation_required_decision(rank, item)
    quality_lift = _rag_quality_lift(str(item["name"]))
    quality_delta = _as_float(quality_lift["quality_delta"])
    improved = quality_delta >= min_quality_delta
    return {
        "rank": rank,
        "candidate_id": item["candidate_id"],
        "name": item["name"],
        "category": item["category"],
        "priority_score": item["priority_score"],
        "decision": "ADOPT" if improved else "REJECT_NO_LIFT",
        "benchmark_key": item["benchmark_key"],
        "quality_delta": quality_delta,
        "baseline_quality_score": quality_lift["baseline_quality_score"],
        "candidate_quality_score": quality_lift["candidate_quality_score"],
        "quality_lift": quality_lift,
        "reason": (
            "Candidate improved output quality over baseline."
            if improved
            else "Candidate did not improve output quality over baseline."
        ),
    }


def _as_float(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise TypeError(f"Expected numeric value, got {type(value).__name__}")


def _implementation_required_decision(rank: int, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "rank": rank,
        "candidate_id": item["candidate_id"],
        "name": item["name"],
        "category": item["category"],
        "priority_score": item["priority_score"],
        "decision": "IMPLEMENTATION_REQUIRED",
        "benchmark_key": item.get("benchmark_key", ""),
        "quality_delta": None,
        "reason": "Candidate is promising but has no executable product variant to benchmark yet.",
    }


def _not_run_decision(rank: int, item: dict[str, Any], decision: str) -> dict[str, Any]:
    return {
        "rank": rank,
        "candidate_id": item["candidate_id"],
        "name": item["name"],
        "category": item["category"],
        "priority_score": item["priority_score"],
        "decision": decision,
        "benchmark_key": item.get("benchmark_key", ""),
        "quality_delta": None,
        "reason": "Skipped because the ranked benchmark stop rule already fired.",
    }


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Ranked Value Benchmark Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        f"Stop reason: `{report['stop_reason']}`",
        "",
        "## Summary",
        "",
        f"- Scanned candidates: {report['scanned_count']}",
        f"- Executed benchmarks: {report['executed_count']}",
        f"- Adopted: {report['adopt_count']}",
        f"- Rejected no lift: {report['reject_no_lift_count']}",
        f"- Implementation required: {report['implementation_required_count']}",
        f"- Stopped before benchmark: {report['stopped_before_benchmark_count']}",
        "",
        "## Decisions",
        "",
        "| Rank | Candidate | Decision | Quality delta | Reason |",
        "|---:|---|---:|---:|---|",
    ]
    for decision in report["decisions"]:
        lines.append(
            f"| {decision['rank']} | {_md_cell(str(decision['name']))} | "
            f"{_md_cell(str(decision['decision']))} | {_md_cell(str(decision['quality_delta']))} | "
            f"{_md_cell(str(decision['reason']))} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
