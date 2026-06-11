"""Integration tests for the CLI demo (Epic 24).

Tests verify that:
1. CLI runs with sample input and exits 0
2. Markdown brief is generated
3. JSON brief is generated
4. Demo run report is generated
5. Offline mode works (no Qdrant)
6. Answer quality eval generates additional report when enabled
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent
_SCRIPT_PATH = _SCRIPT_DIR / "scripts" / "run_startup_radar_demo.py"
_SAMPLE_INPUT = _SCRIPT_DIR / "examples" / "demo" / "sample_startup_input.json"

_REQUIRE_SCRIPT = pytest.mark.skipif(
    not _SCRIPT_PATH.exists(),
    reason="CLI demo script not found",
)
_REQUIRE_SAMPLE = pytest.mark.skipif(
    not _SAMPLE_INPUT.exists(),
    reason="Sample input not found",
)


def _demo_cmd(
    *args: str,
    output_dir: str = "tmp_test_demo",
) -> list[str]:
    cmd = [
        sys.executable,
        str(_SCRIPT_PATH),
        "--input",
        str(_SAMPLE_INPUT),
        "--output-dir",
        output_dir,
    ]
    cmd.extend(args)
    return cmd


def _run_demo(*args: str, output_dir: str = "tmp_test_demo") -> subprocess.CompletedProcess:
    cmd = _demo_cmd(*args, output_dir=output_dir)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(_SCRIPT_DIR))


@pytest.fixture
def demo_output_dir(tmp_path: Path) -> str:
    return str(tmp_path / "demo_runs" / "latest")


@pytest.mark.integration
@_REQUIRE_SCRIPT
@_REQUIRE_SAMPLE
def test_cli_runs_with_sample_input(demo_output_dir: str) -> None:
    """CLI runs with sample input and exits with code 0."""
    result = _run_demo(output_dir=demo_output_dir)
    assert result.returncode == 0, f"CLI failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    assert "DEMO COMPLETED" in result.stdout


@pytest.mark.integration
@_REQUIRE_SCRIPT
@_REQUIRE_SAMPLE
def test_cli_generates_markdown_brief(demo_output_dir: str) -> None:
    """CLI generates a valid Markdown brief."""
    _run_demo(output_dir=demo_output_dir)
    md_path = Path(demo_output_dir) / "startup_action_brief.md"
    assert md_path.exists(), f"Markdown brief not found: {md_path}"
    content = md_path.read_text(encoding="utf-8")
    assert "# Startup Action Brief:" in content
    assert "Nexus AI Labs" in content


@pytest.mark.integration
@_REQUIRE_SCRIPT
@_REQUIRE_SAMPLE
def test_cli_generates_json_brief(demo_output_dir: str) -> None:
    """CLI generates a valid JSON brief."""
    _run_demo(output_dir=demo_output_dir)
    json_path = Path(demo_output_dir) / "startup_action_brief.json"
    assert json_path.exists(), f"JSON brief not found: {json_path}"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["startup_name"] == "Nexus AI Labs"
    assert "verdict" in data
    assert "sections" in data


@pytest.mark.integration
@_REQUIRE_SCRIPT
@_REQUIRE_SAMPLE
def test_cli_generates_run_report(demo_output_dir: str) -> None:
    """CLI generates a demo run report with metadata."""
    _run_demo(output_dir=demo_output_dir)
    report_path = Path(demo_output_dir) / "demo_run_report.json"
    assert report_path.exists(), f"Run report not found: {report_path}"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "completed"
    assert report["startup_name"] == "Nexus AI Labs"
    assert "run_id" in report
    assert "pipeline_summary" in report
    assert "final_priority_score" in report["pipeline_summary"]
    assert "recommended_motion" in report["pipeline_summary"]


@pytest.mark.integration
@_REQUIRE_SCRIPT
@_REQUIRE_SAMPLE
def test_cli_offline_mode(demo_output_dir: str) -> None:
    """Offline mode runs without Qdrant or external dependencies."""
    result = _run_demo("--offline", output_dir=demo_output_dir)
    assert (
        result.returncode == 0
    ), f"CLI offline failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    report_path = Path(demo_output_dir) / "demo_run_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "completed"
    assert "Mode: offline" in result.stdout or "RAG disabled" in result.stdout


@pytest.mark.integration
@_REQUIRE_SCRIPT
@_REQUIRE_SAMPLE
def test_cli_answer_quality_eval(demo_output_dir: str) -> None:
    """Answer quality eval generates additional report when enabled."""
    result = _run_demo(
        "--run-answer-quality-eval",
        output_dir=demo_output_dir,
    )
    assert (
        result.returncode == 0
    ), f"CLI with answer quality eval failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    eval_path = Path(demo_output_dir) / "answer_quality_eval.json"
    assert eval_path.exists(), f"Answer quality eval not found: {eval_path}"
    data = json.loads(eval_path.read_text(encoding="utf-8"))
    assert "case_id" in data
    assert "metrics" in data
    assert "passed" in data
    assert "gates" in data
