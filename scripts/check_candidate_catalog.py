#!/usr/bin/env python3
# ruff: noqa: E402,I001
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.governance.artifacts import (
    DEFAULT_EVIDENCE_DIR,
    DEFAULT_ROADMAP_PATH,
    parse_candidate_catalog_from_roadmap,
    read_csv,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check final candidate catalog completeness.")
    parser.add_argument("--roadmap", type=Path, default=DEFAULT_ROADMAP_PATH)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_EVIDENCE_DIR / "candidate_catalog.csv")
    parser.add_argument("--require-benchmark-coverage", action="store_true")
    args = parser.parse_args()

    if not args.catalog.exists():
        print(f"FAIL: missing candidate catalog: {args.catalog}")
        return 1
    expected = {entry.candidate_id for entry in parse_candidate_catalog_from_roadmap(args.roadmap)}
    actual = {row["candidate_id"] for row in read_csv(args.catalog)}
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        print("FAIL: candidate catalog missing canonical candidates")
        for item in missing:
            print(f"  missing: {item}")
        return 1
    if extra:
        print("WARN: candidate catalog has extra rows")
        for item in extra:
            print(f"  extra: {item}")
    if args.require_benchmark_coverage:
        coverage_path = args.catalog.parent / "benchmark_coverage_report.json"
        output_value_path = args.catalog.parent / "output_value_benchmark_report.json"
        documentation_path = args.catalog.parent / "all_candidate_benchmark_documentation.md"
        if not coverage_path.exists():
            print(f"FAIL: missing benchmark coverage report: {coverage_path}")
            return 1
        if not output_value_path.exists():
            print(f"FAIL: missing output-value benchmark report: {output_value_path}")
            return 1
        if not documentation_path.exists():
            print(f"FAIL: missing benchmark documentation report: {documentation_path}")
            return 1
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        if int(coverage.get("total_candidates", -1)) != len(expected):
            print("FAIL: benchmark coverage total does not match canonical catalog")
            return 1
        if int(coverage.get("total_results", -1)) != len(expected):
            print("FAIL: benchmark coverage does not include every candidate")
            return 1
        output_value = json.loads(output_value_path.read_text(encoding="utf-8"))
        if int(output_value.get("total_candidates", -1)) != len(expected):
            print("FAIL: output-value report total does not match canonical catalog")
            return 1
        decisions = output_value.get("decisions", [])
        if len(decisions) != len(expected):
            print("FAIL: output-value report does not include every candidate decision")
            return 1
        missing_decision = [
            item
            for item in decisions
            if not isinstance(item, dict) or not item.get("decision") or item.get("decision") == "UNDECIDED"
        ]
        if missing_decision:
            print("FAIL: output-value report has candidates without benchmark disposition")
            for item in missing_decision[:20]:
                print(f"  unfinished: {item.get('candidate_id', 'unknown')}")
            return 1
        documentation = documentation_path.read_text(encoding="utf-8")
        if "## Decisions" not in documentation:
            print("FAIL: benchmark documentation is missing the decisions section")
            return 1
    print(f"PASS: candidate catalog covers {len(expected)} canonical candidates")
    if args.require_benchmark_coverage:
        print(f"PASS: benchmark coverage includes {len(expected)} candidate results")
        print(f"PASS: output-value report includes {len(expected)} candidate decisions")
        print("PASS: benchmark documentation report exists")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
