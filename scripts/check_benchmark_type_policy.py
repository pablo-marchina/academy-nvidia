#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EVIDENCE_DIR = PROJECT_ROOT / "final_case_evidence"
BENCHMARK_TYPES = {
    "LOCAL_READINESS",
    "PROXY",
    "OUTPUT_VALUE",
    "PRODUCTION_QUALITY",
    "SECURITY",
    "COST_LATENCY",
    "COMPLIANCE",
    "REPRODUCIBILITY",
}
PROMOTION_TYPES = {"OUTPUT_VALUE", "PRODUCTION_QUALITY"}
NON_PROMOTION_TYPES = {"LOCAL_READINESS", "PROXY"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check benchmark_type policy for final runtime promotion.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()

    failures = validate_benchmark_type_policy(args.evidence_dir)
    write_benchmark_type_reports(args.evidence_dir, failures)
    if failures:
        print("FAIL: benchmark_type policy")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("PASS: benchmark_type policy")
    return 0


def validate_benchmark_type_policy(evidence_dir: Path) -> list[str]:
    failures: list[str] = []
    catalog_path = evidence_dir / "candidate_catalog.csv"
    if not catalog_path.exists():
        return [f"missing {catalog_path}"]
    with catalog_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    allowed = BENCHMARK_TYPES
    missing_or_invalid = [
        row.get("candidate_id", "unknown")
        for row in rows
        if row.get("benchmark_type") not in allowed
    ]
    if missing_or_invalid:
        failures.append(f"candidate_catalog benchmark_type missing/invalid: {missing_or_invalid[:20]}")

    results_path = evidence_dir / "benchmark_results.jsonl"
    if results_path.exists():
        with results_path.open(encoding="utf-8") as handle:
            for index, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                payload = json.loads(line)
                benchmark_type = payload.get("benchmark_type")
                if benchmark_type not in allowed:
                    failures.append(f"benchmark_results.jsonl line {index} has invalid benchmark_type {benchmark_type}")

    output_path = evidence_dir / "output_value_benchmark_report.json"
    if not output_path.exists():
        failures.append(f"missing {output_path}")
        return failures
    output = json.loads(output_path.read_text(encoding="utf-8"))
    for decision in output.get("decisions", []):
        if not isinstance(decision, dict):
            continue
        benchmark_type = decision.get("benchmark_type")
        if decision.get("promotion_allowed") is True and benchmark_type not in PROMOTION_TYPES:
            failures.append(
                f"{decision.get('candidate_id', 'unknown')} promotes with non-output benchmark_type {benchmark_type}"
            )
        if decision.get("promotion_allowed") is True and benchmark_type in NON_PROMOTION_TYPES:
            failures.append(f"{decision.get('candidate_id', 'unknown')} has proxy/readiness-only promotion")
        if decision.get("uses_mock_provider") is True and benchmark_type == "OUTPUT_VALUE":
            failures.append(f"{decision.get('candidate_id', 'unknown')} uses mock provider as OUTPUT_VALUE")
    return failures


def write_benchmark_type_reports(evidence_dir: Path, failures: list[str]) -> None:
    generated_at = datetime.now(UTC).isoformat()
    catalog_path = evidence_dir / "candidate_catalog.csv"
    rows: list[dict[str, str]] = []
    if catalog_path.exists():
        with catalog_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    counts: dict[str, int] = {}
    for row in rows:
        benchmark_type = row.get("benchmark_type", "MISSING")
        counts[benchmark_type] = counts.get(benchmark_type, 0) + 1
    _write_json(
        evidence_dir / "benchmark_type_coverage_report.json",
        {
            "report_id": "benchmark_type_coverage_report",
            "status": "PASS" if not failures else "FAIL",
            "generated_at": generated_at,
            "allowed_values": sorted(BENCHMARK_TYPES),
            "candidate_count": len(rows),
            "catalog_type_counts": counts,
        },
    )
    _write_json(
        evidence_dir / "proxy_benchmark_promotion_block_report.json",
        {
            "report_id": "proxy_benchmark_promotion_block_report",
            "status": "PASS" if not any("proxy/readiness-only promotion" in item for item in failures) else "FAIL",
            "generated_at": generated_at,
            "policy": "LOCAL_READINESS and PROXY never promote runtime adoption alone.",
            "failures": [item for item in failures if "proxy" in item or "non-output" in item],
        },
    )
    _write_json(
        evidence_dir / "mock_provider_benchmark_classification_report.json",
        {
            "report_id": "mock_provider_benchmark_classification_report",
            "status": "PASS" if not any("mock provider" in item for item in failures) else "FAIL",
            "generated_at": generated_at,
            "policy": "Mock providers cannot prove OUTPUT_VALUE.",
            "failures": [item for item in failures if "mock provider" in item],
        },
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
