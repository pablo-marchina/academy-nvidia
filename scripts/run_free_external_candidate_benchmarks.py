#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NPM_CLI = Path("C:/Program Files/nodejs/node_modules/npm/bin/npm-cli.js")
sys.path.insert(0, str(PROJECT_ROOT))

from src.governance.artifacts import DEFAULT_EVIDENCE_DIR, write_json

TOOL_PROBES: dict[str, dict[str, object]] = {
    "OpenSSF Scorecard": {"commands": ["scorecard", "scorecard.exe"], "modules": [], "version_commands": []},
    "Renovate": {
        "commands": ["renovate", "renovate.cmd"],
        "modules": [],
        "version_commands": [["node", str(NPM_CLI), "exec", "--offline", "--yes", "renovate", "--", "--version"]],
    },
    "Sigstore Cosign": {"commands": ["cosign", "cosign.exe"], "modules": [], "version_commands": []},
    "Phoenix": {"commands": [], "modules": ["phoenix", "arize.phoenix"], "version_commands": []},
    "Label Studio": {
        "commands": ["label-studio", "label-studio.exe"],
        "modules": ["label_studio"],
        "version_commands": [],
    },
    "Argilla": {"commands": ["argilla", "argilla.exe"], "modules": ["argilla"], "version_commands": []},
}

BENCHMARK_RECIPES: dict[str, dict[str, object]] = {
    "OpenSSF Scorecard": {
        "value_hypothesis": "Improve release/supply-chain output by adding repo risk signals beyond local file checks.",
        "output_quality_metrics": [
            "actionable_security_findings",
            "supply_chain_risk_coverage",
            "false_positive_rate",
            "remediation_specificity",
        ],
        "activation_commands": ["install OpenSSF Scorecard CLI from its official release channel"],
        "benchmark_command": "python scripts/run_free_external_candidate_benchmarks.py",
    },
    "Renovate": {
        "value_hypothesis": (
            "Improve dependency-maintenance output by producing more actionable update/remediation evidence."
        ),
        "output_quality_metrics": [
            "actionable_dependency_updates",
            "security_update_coverage",
            "config_validation_quality",
            "false_positive_rate",
        ],
        "activation_commands": ["npm install renovate --save-dev"],
        "benchmark_command": "python scripts/run_free_external_candidate_benchmarks.py",
    },
    "Sigstore Cosign": {
        "value_hypothesis": "Improve release output by adding verifiable artifact signing/provenance evidence.",
        "output_quality_metrics": [
            "release_provenance_completeness",
            "verification_reproducibility",
            "manual_release_step_reduction",
        ],
        "activation_commands": ["install Cosign CLI from its official release channel"],
        "benchmark_command": "python scripts/run_free_external_candidate_benchmarks.py",
    },
    "Phoenix": {
        "value_hypothesis": (
            "Improve product-output evaluation by adding trace-level observability for recommendations, "
            "claims, and degraded evidence."
        ),
        "output_quality_metrics": [
            "trace_step_coverage",
            "evidence_debuggability",
            "latency_attribution_coverage",
            "failure_root_cause_specificity",
        ],
        "activation_commands": [
            ".venv\\Scripts\\python.exe -m pip install arize-phoenix",
            (
                "If Windows native build fails, install Microsoft C++ Build Tools or use a Python version "
                "with compatible wheels."
            ),
        ],
        "benchmark_command": "python scripts/run_free_external_candidate_benchmarks.py",
    },
    "Label Studio": {
        "value_hypothesis": (
            "Improve human evaluation output by making claim/recommendation review structured and exportable."
        ),
        "output_quality_metrics": [
            "review_schema_fit",
            "unsupported_claim_detection_rate",
            "human_correction_capture",
            "review_export_completeness",
        ],
        "activation_commands": [".venv\\Scripts\\python.exe -m pip install label-studio"],
        "benchmark_command": "python scripts/run_free_external_candidate_benchmarks.py",
    },
    "Argilla": {
        "value_hypothesis": "Improve evaluator feedback output by capturing disagreement, labels, and review datasets.",
        "output_quality_metrics": [
            "review_disagreement_capture",
            "dataset_export_completeness",
            "preference_signal_quality",
            "review_workflow_reproducibility",
        ],
        "activation_commands": [".venv\\Scripts\\python.exe -m pip install argilla"],
        "benchmark_command": "python scripts/run_free_external_candidate_benchmarks.py",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe free external candidates for benchmark readiness.")
    parser.add_argument(
        "--review-path",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR / "free_external_candidate_review.json",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR / "free_external_candidate_benchmark_report.json",
    )
    parser.add_argument(
        "--markdown-path",
        type=Path,
        default=DEFAULT_EVIDENCE_DIR / "free_external_candidate_benchmark_report.md",
    )
    args = parser.parse_args()

    report = build_probe_report(args.review_path)
    write_json(args.report_path, report)
    write_markdown_report(args.markdown_path, report)
    print(
        "Free external benchmark probes completed: "
        f"ready={report['summary']['ready_for_product_benchmark_count']}, "
        f"blocked={report['summary']['blocked_by_environment_count']}"
    )
    return 0


def build_probe_report(review_path: Path) -> dict[str, Any]:
    review = _load_json(review_path)
    eligible_items = [item for item in review.get("items", []) if item.get("ranking_eligible")]
    probes = [probe_candidate(item) for item in eligible_items]
    return {
        "report_id": "free_external_candidate_benchmark_report",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "PASS",
        "review_path": str(review_path),
        "benchmark_policy": (
            "This probe checks whether a no-cost external/open-source candidate is locally available for a "
            "future output-quality benchmark. Availability is not adoption and does not promote runtime."
        ),
        "summary": {
            "eligible_candidate_count": len(eligible_items),
            "ready_for_product_benchmark_count": sum(
                1 for probe in probes if probe["status"] == "READY_FOR_PRODUCT_BENCHMARK"
            ),
            "blocked_by_environment_count": sum(1 for probe in probes if probe["status"] == "BLOCKED_BY_ENVIRONMENT"),
        },
        "probes": probes,
    }


def probe_candidate(item: dict[str, Any]) -> dict[str, Any]:
    name = str(item.get("name", ""))
    probe = TOOL_PROBES.get(name, {"commands": [], "modules": [], "version_commands": []})
    recipe = BENCHMARK_RECIPES.get(
        name,
        {
            "value_hypothesis": "Evaluate whether this candidate improves final product output quality.",
            "output_quality_metrics": ["output_quality_delta"],
            "activation_commands": ["document candidate-specific activation before benchmark"],
            "benchmark_command": "python scripts/run_free_external_candidate_benchmarks.py",
        },
    )
    commands_checked = _string_list(probe["commands"])
    modules_checked = _string_list(probe["modules"])
    version_commands = _command_list(probe["version_commands"])
    found_commands = [command for command in commands_checked if shutil.which(command)]
    found_modules = [module for module in modules_checked if _module_available(module)]
    version_checks = [_run_version_check(command) for command in version_commands]
    available = bool(found_commands or found_modules or any(check["available"] for check in version_checks))
    status = "READY_FOR_PRODUCT_BENCHMARK" if available else "BLOCKED_BY_ENVIRONMENT"
    return {
        "name": name,
        "status": status,
        "output_value_family": item.get("output_value_family", ""),
        "catalog_status": item.get("catalog_status", ""),
        "benchmark_path": item.get("benchmark_path", ""),
        "commands_checked": commands_checked,
        "commands_found": found_commands,
        "modules_checked": modules_checked,
        "modules_found": found_modules,
        "version_checks": version_checks,
        "quality_delta": None,
        "value_hypothesis": recipe["value_hypothesis"],
        "output_quality_metrics": recipe["output_quality_metrics"],
        "activation_commands": recipe["activation_commands"],
        "benchmark_command": recipe["benchmark_command"],
        "decision": "PRODUCT_BENCHMARK_REQUIRED" if available else "BLOCKED_BY_ENVIRONMENT",
        "reason": (
            "Candidate is locally available; run a product-output spike before adoption."
            if available
            else "Candidate is registry-eligible but the local free/open-source tool is not installed or importable."
        ),
        "promotion_guardrail": (
            "Do not promote from this probe alone. Promotion requires measured output-quality lift, "
            "cost/latency/risk evidence, reproducibility, and decision-ledger approval."
        ),
    }


def write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Free External Candidate Benchmark Report",
        "",
        f"Status: `{report['status']}`",
        "",
        f"- Eligible candidates: {summary['eligible_candidate_count']}",
        f"- Ready for product benchmark: {summary['ready_for_product_benchmark_count']}",
        f"- Blocked by environment: {summary['blocked_by_environment_count']}",
        "",
        "| Candidate | Status | Decision | Reason |",
        "|---|---|---|---|",
    ]
    for probe in report["probes"]:
        lines.append(
            f"| {_md_cell(str(probe['name']))} | {probe['status']} | "
            f"{probe['decision']} | {_md_cell(str(probe['reason']))} |"
        )
    lines.append("")
    lines.extend(["## Benchmark Recipes", ""])
    for probe in report["probes"]:
        lines.extend(
            [
                f"### {probe['name']}",
                "",
                f"- Value hypothesis: {probe['value_hypothesis']}",
                f"- Metrics: {', '.join(probe['output_quality_metrics'])}",
                f"- Benchmark command: `{probe['benchmark_command']}`",
                "- Activation commands:",
            ]
        )
        for command in probe["activation_commands"]:
            lines.append(f"  - `{command}`")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    import json

    if not path.exists():
        return {"items": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"items": []}


def _module_available(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except ModuleNotFoundError:
        return False


def _run_version_check(command: list[str]) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "command": command,
            "available": False,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": str(exc)[-500:],
        }
    return {
        "command": command,
        "available": result.returncode == 0,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-500:],
        "stderr_tail": result.stderr[-500:],
    }


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _command_list(value: object) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    commands: list[list[str]] = []
    for item in value:
        if isinstance(item, list):
            commands.append([str(part) for part in item])
    return commands


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
