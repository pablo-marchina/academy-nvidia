#!/usr/bin/env python3
# ruff: noqa: E402,I001
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EVIDENCE_DIR = PROJECT_ROOT / "final_case_evidence"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check final security and release artifacts.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()

    required = [
        "security_scan_report.json",
        "release_artifact_manifest.json",
        "license_inventory.json",
        "secret_scan_report.json",
        "dependency_vulnerability_report.json",
        "sast_report.json",
        "sbom.json",
        "container_scan_report.json",
        "openssf_scorecard_report.json",
        "no_hidden_manual_steps_report.json",
    ]
    missing = [name for name in required if not (args.evidence_dir / name).exists()]
    failures = [f"missing {name}" for name in missing]
    security_path = args.evidence_dir / "security_scan_report.json"
    if security_path.exists():
        security = json.loads(security_path.read_text(encoding="utf-8"))
        if security.get("status") == "FAIL":
            failures.append("security_scan_report.json has FAIL status")
    license_path = args.evidence_dir / "license_inventory.json"
    if license_path.exists():
        license_inventory = json.loads(license_path.read_text(encoding="utf-8"))
        if "python_dependency_count" not in license_inventory:
            failures.append("license_inventory.json is not a dependency manifest inventory")
    for name in required:
        path = args.evidence_dir / name
        if path.exists() and path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("status") == "FAIL":
                failures.append(f"{name} has FAIL status")
    if failures:
        print("FAIL: security/release artifacts missing")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("PASS: security/release artifact gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
