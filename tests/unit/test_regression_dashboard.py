from __future__ import annotations

import json
from pathlib import Path

from scripts.build_regression_dashboard import (
    REQUIRED_MARKDOWN_SECTIONS,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARN,
    build_dashboard,
    render_markdown,
    write_dashboard,
)

REQUIRED_METRICS = [
    "documents_seen",
    "documents_valid",
    "documents_skipped",
    "chunks_created",
    "chunks_upserted",
    "sources_failed",
    "validation_errors",
    "stale_sources",
    "expired_sources",
    "deprecated_sources",
    "rag_eval_passed",
    "rag_eval_failed_cases",
    "golden_eval_passed",
    "golden_eval_failed_cases",
    "action_brief_required_sections_passed",
    "missing_context_count",
    "missing_evidence_count",
]


def test_clean_reports_generate_pass(tmp_path: Path) -> None:
    _write_clean_reports(tmp_path)

    dashboard = build_dashboard(tmp_path)

    assert dashboard.status == STATUS_PASS
    assert dashboard.metrics["documents_seen"] == 10
    assert dashboard.metrics["chunks_created"] == 50
    assert dashboard.metrics["rag_eval_passed"] is True
    assert dashboard.metrics["golden_eval_passed"] is True
    assert dashboard.metrics["action_brief_required_sections_passed"] is True


def test_stale_sources_generate_warn(tmp_path: Path) -> None:
    _write_clean_reports(tmp_path)
    _write_json(
        tmp_path / "freshness_audit.json",
        {
            "stale_sources": 1,
            "expired_sources": 0,
            "deprecated_sources": 0,
        },
    )

    dashboard = build_dashboard(tmp_path)

    assert dashboard.status == STATUS_WARN
    assert dashboard.metrics["stale_sources"] == 1
    assert "stale_sources > 0" in dashboard.warnings


def test_validation_errors_generate_fail(tmp_path: Path) -> None:
    _write_clean_reports(tmp_path)
    _write_json(
        tmp_path / "qdrant_ingest_dry_run.json",
        {
            "documents_seen": 1,
            "documents_valid": 0,
            "documents_skipped": 1,
            "chunks_created": 0,
            "chunks_upserted": 0,
            "sources_failed": ["bad_source"],
            "validation_errors": ["missing title"],
        },
    )

    dashboard = build_dashboard(tmp_path)

    assert dashboard.status == STATUS_FAIL
    assert dashboard.metrics["validation_errors"] == 1
    assert dashboard.metrics["sources_failed"] == 1


def test_markdown_contains_required_sections(tmp_path: Path) -> None:
    _write_clean_reports(tmp_path)
    dashboard = build_dashboard(tmp_path)

    markdown = render_markdown(dashboard)

    for section in REQUIRED_MARKDOWN_SECTIONS:
        assert f"## {section}" in markdown


def test_json_contains_required_fields(tmp_path: Path) -> None:
    _write_clean_reports(tmp_path)
    dashboard = build_dashboard(tmp_path)
    _, json_path = write_dashboard(dashboard, tmp_path / "out")

    data = json.loads(json_path.read_text(encoding="utf-8"))

    assert data["status"] == STATUS_PASS
    for metric in REQUIRED_METRICS:
        assert metric in data["metrics"]
    assert isinstance(data["warnings"], list)
    assert isinstance(data["failures"], list)
    assert isinstance(data["inputs"], list)


def test_missing_reports_are_controlled_warning(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing"

    dashboard = build_dashboard(missing_dir)

    assert dashboard.status == STATUS_WARN
    assert dashboard.warnings
    for metric in REQUIRED_METRICS:
        assert metric in dashboard.metrics


def _write_clean_reports(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _write_json(
        path / "source_sync_dry_run.json",
        {
            "sources_seen": 10,
            "sources_failed": [],
            "validation_errors": [],
        },
    )
    _write_json(
        path / "freshness_audit.json",
        {
            "stale_sources": 0,
            "expired_sources": 0,
            "deprecated_sources": 0,
        },
    )
    _write_json(
        path / "qdrant_ingest_dry_run.json",
        {
            "documents_seen": 10,
            "documents_valid": 10,
            "documents_skipped": 0,
            "chunks_created": 50,
            "chunks_upserted": 0,
            "sources_failed": [],
            "validation_errors": [],
        },
    )
    _write_junit(path / "rag_eval_junit.xml")
    _write_junit(path / "golden_eval_junit.xml")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_junit(path: Path) -> None:
    path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuite name="pytest" tests="1" failures="0" errors="0" skipped="0">
  <testcase
    classname="tests.evals.test_pipeline_golden.TestGoldenHighFit"
    name="test_action_brief_sections"
  />
</testsuite>
""",
        encoding="utf-8",
    )
