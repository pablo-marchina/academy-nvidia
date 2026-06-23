#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORT_PATH = PROJECT_ROOT / "final_case_evidence" / "repository_clean_report.json"
FORBIDDEN_TRACKED_PARTS = (
    "node_modules/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "__pycache__/",
    "frontend/dist/",
    "test_exports/",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check tracked repository cleanliness.")
    parser.add_argument("--repo", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    result = subprocess.run(["git", "ls-files"], cwd=args.repo, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        _write_report(
            args.report_path,
            {
                "report_id": "repository_clean_report",
                "status": "FAIL",
                "generated_at": datetime.now(UTC).isoformat(),
                "reason": "git_ls_files_failed",
                "stderr": result.stderr,
            },
        )
        return 2
    tracked = result.stdout.splitlines()
    violations = [
        path
        for path in tracked
        if any(part in path.replace("\\", "/") for part in FORBIDDEN_TRACKED_PARTS)
        or path.endswith((".pyc", ".pyo", ".sqlite", ".sqlite3", ".db"))
    ]
    if violations:
        _write_report(args.report_path, _build_report(tracked, violations))
        print("FAIL: forbidden tracked artifacts")
        for violation in violations:
            print(f"  {violation}")
        return 1
    _write_report(args.report_path, _build_report(tracked, violations))
    print(f"PASS: repository cleanliness checked {len(tracked)} tracked files")
    return 0


def _build_report(tracked: list[str], violations: list[str]) -> dict[str, object]:
    return {
        "report_id": "repository_clean_report",
        "status": "PASS" if not violations else "FAIL",
        "generated_at": datetime.now(UTC).isoformat(),
        "tracked_file_count": len(tracked),
        "violation_count": len(violations),
        "violations": violations,
        "checks": [
            "tracked_forbidden_artifacts",
            "local_databases",
            "node_modules",
            "cache_directories",
            "test_exports",
        ],
    }


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
