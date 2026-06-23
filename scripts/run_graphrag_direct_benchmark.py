#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_graphrag_evidence_graph_product_spike import build_report, write_markdown
from src.governance.artifacts import DEFAULT_EVIDENCE_DIR, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the canonical GraphRAG direct benchmark.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--report-path", type=Path)
    parser.add_argument("--markdown-path", type=Path)
    parser.add_argument("--min-delta", type=float, default=0.20)
    args = parser.parse_args()

    report_path = args.report_path or args.evidence_dir / "graphrag_direct_benchmark_report.json"
    markdown_path = args.markdown_path or args.evidence_dir / "graphrag_direct_benchmark_report.md"
    report = build_report(min_delta=args.min_delta)
    report["report_id"] = "graphrag_direct_benchmark_report"
    report["canonical_for"] = "Epic 30 GraphRAG direct benchmark"
    report["runtime_promotion"] = "not_promoted_without_direct_benchmark_and_final_gates"
    write_json(report_path, report)
    write_markdown(markdown_path, report)
    print(
        "GraphRAG direct benchmark completed: "
        f"decision={report['decision']}, quality_delta={report['quality_delta']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
