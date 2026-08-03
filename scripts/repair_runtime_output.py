"""Repair post-merge runtime/output regressions and add regression coverage.

This script is intentionally idempotent. It is used once by GitHub Actions and
then retained as a reproducible repair/audit utility.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, content: str) -> None:
    (ROOT / relative).write_text(content, encoding="utf-8")


def require_replace(relative: str, old: str, new: str, *, already: str | None = None) -> None:
    text = read(relative)
    if old in text:
        write(relative, text.replace(old, new, 1))
        return
    if already and already in text:
        return
    raise RuntimeError(f"Expected repair target not found in {relative}: {old[:120]!r}")


def repair_quality_route() -> None:
    require_replace(
        "src/api/product_routes.py",
        "from __future__ import annotations\n\nfrom typing import Annotated, Any\n",
        "from __future__ import annotations\n\nfrom datetime import UTC, datetime\nfrom typing import Annotated, Any\n",
        already="from datetime import UTC, datetime",
    )


def repair_orchestration_nodes() -> None:
    relative = "src/orchestration/node_impl.py"
    text = read(relative)

    start = text.index("def node_plan_search(state: ProductWorkflowState) -> NodeResult:")
    end = text.index("\n\n# ---------------------------------------------------------------------------\n# Node 3: collect_sources", start)
    block = text[start:end]
    if "known_source_urls: list[str] = []" not in block:
        block = block.replace(
            '    startup_name = ""\n    website_url = ""\n',
            '    startup_name = ""\n    website_url = ""\n    known_source_urls: list[str] = []\n',
            1,
        )
        block = block.replace(
            '                website_url = startup.website or ""\n',
            '                website_url = startup.website or ""\n'
            '                known_source_urls = [\n'
            '                    str(evidence.source_url)\n'
            '                    for evidence in (startup.evidence or [])\n'
            '                    if str(evidence.source_url or "").startswith(("http://", "https://"))\n'
            '                ]\n',
            1,
        )
        block = block.replace(
            "    plan = build_search_plan(startup_name, website_url=website_url)\n",
            "    plan = build_search_plan(\n"
            "        startup_name,\n"
            "        website_url=website_url,\n"
            "        known_source_urls=known_source_urls,\n"
            "    )\n",
            1,
        )
        text = text[:start] + block + text[end:]

    old_gate = '''    if error_rate > max_error_rate:
        degraded_failures.append("maximum_collection_error_rate_exceeded")

    if failures:
        msg_parts = []
'''
    new_gate = '''    if error_rate > max_error_rate:
        degraded_failures.append("maximum_collection_error_rate_exceeded")

    failures = critical_failures + degraded_failures
    if failures:
        msg_parts = []
'''
    if old_gate in text:
        text = text.replace(old_gate, new_gate, 1)
    elif "failures = critical_failures + degraded_failures" not in text:
        raise RuntimeError("collect_sources failures aggregation target not found")

    old_status = '''        is_failed = _is_product_mode() and bool(critical_failures)
        return NodeResult(
            status=NodeStatus.FAILED if _is_product_mode() else NodeStatus.DEGRADED,
            error_message=msg if _is_product_mode() else None,
            degraded_reason=msg,
            state_updates=updates,
        )
'''
    new_status = '''        is_failed = product_mode and bool(critical_failures)
        return NodeResult(
            status=NodeStatus.FAILED if is_failed else NodeStatus.DEGRADED,
            error_message=msg if is_failed else None,
            degraded_reason=msg,
            state_updates=updates,
        )
'''
    if old_status in text:
        text = text.replace(old_status, new_status, 1)
    elif "status=NodeStatus.FAILED if is_failed else NodeStatus.DEGRADED" not in text:
        raise RuntimeError("collect_sources status target not found")

    write(relative, text)


def repair_radar_service() -> None:
    relative = "src/services/product/radar_dashboard_service.py"
    text = read(relative)
    text = text.replace(
        '_TERMINAL_RUN_STATUSES = {"completed", "degraded"}',
        '_TERMINAL_RUN_STATUSES = {"completed", "degraded", "awaiting_review"}',
        1,
    )

    old_source = '''            except Exception as exc:  # keep dashboard population resilient while reporting the exact blocker
                results.append({"source_id": source_id, "status": "failed", "error": str(exc)})'''
    new_source = '''            except Exception as exc:  # optional external acquisition must not block the central pipeline
                error = str(exc)
                status = "unavailable" if error.startswith("fetch_failed:") else "failed"
                results.append(
                    {
                        "source_id": source_id,
                        "status": status,
                        "error": error,
                        "blocking": status == "failed",
                    }
                )'''
    if old_source in text:
        text = text.replace(old_source, new_source, 1)
    elif 'status = "unavailable" if error.startswith("fetch_failed:") else "failed"' not in text:
        raise RuntimeError("radar source error target not found")

    method_start = text.index("    def _run_pipeline_for_startups(")
    method_end = text.index("\n    def _ensure_post_pipeline_artifacts(", method_start)
    new_method = '''    def _run_pipeline_for_startups(self, startup_ids: list[str], *, force_rerun: bool) -> list[dict[str, Any]]:
        from src.repositories.workflow import WorkflowRepository
        from src.services.product.service import ProductService

        results: list[dict[str, Any]] = []
        product_service = ProductService(self.session)
        workflow_repo = WorkflowRepository(self.session)
        for startup_id in startup_ids:
            latest = self.product_repo.get_latest_analysis_run(startup_id)
            if latest is not None and latest.status in _TERMINAL_RUN_STATUSES and not force_rerun:
                run = latest
            else:
                try:
                    run = product_service.create_analysis_run_for_startup(
                        startup_id,
                        use_rag=True,
                        rag_backend="qdrant",
                        pipeline_version="radar_dashboard_unified_runtime_v2",
                    )
                except Exception as exc:
                    self.session.rollback()
                    results.append(
                        {
                            "startup_id": startup_id,
                            "status": "failed",
                            "error": f"{type(exc).__name__}: {exc}",
                            "blocking": True,
                        }
                    )
                    continue

            analysis_run_id = run.id
            status = str(run.status)
            workflow = workflow_repo.get_workflow_for_analysis_run(analysis_run_id)
            workflow_id = workflow.id if workflow is not None else None
            artifact_errors: list[str] = []
            if status in {"completed", "degraded"}:
                artifact_errors = self._ensure_post_pipeline_artifacts(analysis_run_id)

            result_status = "degraded" if artifact_errors and status == "completed" else status
            error = str(run.error_message or (workflow.error_message if workflow is not None else "") or "")
            degraded_reason = str(
                run.degraded_reason or (workflow.degraded_reason if workflow is not None else "") or ""
            )
            results.append(
                {
                    "startup_id": startup_id,
                    "analysis_run_id": analysis_run_id,
                    "workflow_id": workflow_id,
                    "status": result_status,
                    "current_node": workflow.current_node if workflow is not None else "",
                    "error": error or None,
                    "degraded_reason": degraded_reason or None,
                    "artifact_errors": artifact_errors,
                    "blocking": result_status == "failed",
                }
            )
        return results
'''
    text = text[:method_start] + new_method + text[method_end:]
    write(relative, text)


def repair_worker() -> None:
    relative = "src/orchestration/worker.py"
    text = read(relative)
    old = '''def _execute(workflow_id: str) -> None:
    try:
        with product_session() as session:
            WorkflowOrchestrationService(session).run_existing_workflow(workflow_id)
        logger.info("workflow_completed workflow_id=%s", workflow_id)
    except Exception as exc:
        logger.exception("workflow_failed workflow_id=%s", workflow_id)
        with product_session() as session:
            WorkflowRepository(session).fail_workflow(
                workflow_id,
                error_message=f"Worker execution failed: {exc}",
            )
'''
    new = '''def _execute(workflow_id: str) -> None:
    try:
        with product_session() as session:
            WorkflowOrchestrationService(session).run_existing_workflow(workflow_id)
            persisted = WorkflowRepository(session).get_workflow_run(workflow_id)
            raw_status = getattr(persisted.status, "value", persisted.status) if persisted is not None else "unknown"
            status = str(raw_status).casefold()
            error = persisted.error_message if persisted is not None else None
            if status == "failed":
                logger.error("workflow_finished_failed workflow_id=%s error=%s", workflow_id, error or "unknown")
            elif status == "degraded":
                logger.warning("workflow_finished_degraded workflow_id=%s", workflow_id)
            else:
                logger.info("workflow_finished workflow_id=%s status=%s", workflow_id, status)
    except Exception as exc:
        logger.exception("workflow_worker_exception workflow_id=%s", workflow_id)
        with product_session() as session:
            WorkflowRepository(session).fail_workflow(
                workflow_id,
                error_message=f"Worker execution failed: {exc}",
            )
'''
    if old in text:
        text = text.replace(old, new, 1)
    elif "workflow_finished_failed" not in text:
        raise RuntimeError("worker execution target not found")
    write(relative, text)


def repair_compose() -> None:
    relative = "docker-compose.yml"
    text = read(relative)
    if "b'src.orchestration.worker'" in text:
        return
    marker = '''    volumes:
      - product_data:/app/data/product
      - model_cache:/opt/model-cache

  frontend:
'''
    replacement = '''    volumes:
      - product_data:/app/data/product
      - model_cache:/opt/model-cache
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - "import pathlib; raise SystemExit(0 if b'src.orchestration.worker' in pathlib.Path('/proc/1/cmdline').read_bytes() else 1)"
      interval: 20s
      timeout: 5s
      retries: 3
      start_period: 20s

  frontend:
'''
    pos = text.rfind(marker)
    if pos < 0:
        raise RuntimeError("workflow-worker compose target not found")
    write(relative, text[:pos] + replacement + text[pos + len(marker) :])


def repair_discovery_sources() -> None:
    relative = "src/config/discovery_sources.json"
    sources = json.loads(read(relative))
    overrides = {
        "open_startups_ecosystem": {
            "base_url": "https://www.openstartups.net/site/ranking/rankings-startups.html",
            "enabled_by_default": True,
            "notes": "Current public ranking table with startup entities.",
        },
        "cubo_ecosystem": {
            "base_url": "https://pwa.cubo.network/para-startups",
            "enabled_by_default": False,
            "notes": "Official page is current, but the startup directory is gated and not a stable static public list.",
        },
        "distrito_startup_programs": {
            "base_url": "https://www.distrito.me/ai-ecosystem",
            "enabled_by_default": False,
            "notes": "Official ecosystem page is current; entity-level startup search is gated.",
        },
        "inovativa_startups": {
            "base_url": "https://www.inovativa.online/aceleracao",
            "enabled_by_default": False,
            "notes": "Current program page does not expose a stable public cohort listing for static ingestion.",
        },
        "bossa_invest_portfolio": {
            "base_url": "https://bossainvest.com/receber-investimento/",
            "enabled_by_default": False,
            "notes": "Current official page does not expose a stable public entity list.",
        },
    }
    found = set()
    for source in sources:
        source_id = source.get("source_id")
        if source_id in overrides:
            source.update(overrides[source_id])
            found.add(source_id)
    missing = set(overrides) - found
    if missing:
        raise RuntimeError(f"Missing discovery source IDs: {sorted(missing)}")
    write(relative, json.dumps(sources, ensure_ascii=False, indent=2) + "\n")


def repair_frontend() -> None:
    relative = "frontend/src/views/RadarDashboardView.tsx"
    text = read(relative)
    status_fn = '''function runtimeItemStatus(item: Record<string, JsonValue>): string {
  return stringValue(item.status) || stringValue(item.reason) || "recorded";
}
'''
    detail_fn = '''function runtimeItemStatus(item: Record<string, JsonValue>): string {
  return stringValue(item.status) || stringValue(item.reason) || "recorded";
}

function runtimeItemDetail(item: Record<string, JsonValue>): string {
  for (const key of ["error", "error_message", "degraded_reason", "current_node"]) {
    const value = stringValue(item[key]);
    if (value) return value;
  }
  const artifactErrors = item.artifact_errors;
  if (Array.isArray(artifactErrors)) {
    const values = artifactErrors.map((value) => stringValue(value)).filter(Boolean);
    if (values.length > 0) return values.join("; ");
  }
  return runtimeItemStatus(item);
}
'''
    if "function runtimeItemDetail" not in text:
        if status_fn not in text:
            raise RuntimeError("frontend runtime status target not found")
        text = text.replace(status_fn, detail_fn, 1)
    if "<small>{runtimeItemStatus(item)}</small>" in text:
        text = text.replace(
            "<small>{runtimeItemStatus(item)}</small>",
            "<small>{runtimeItemDetail(item)}</small>",
            1,
        )
    write(relative, text)


def write_regression_tests() -> None:
    relative = "tests/unit/test_runtime_merge_regressions.py"
    write(
        relative,
        '''from __future__ import annotations

import json
from pathlib import Path

from src.agents.search_planner import build_search_plan


ROOT = Path(__file__).resolve().parents[2]


def test_search_planner_uses_defined_bounded_source_limit(monkeypatch) -> None:
    monkeypatch.setenv("RADAR_ANALYSIS_MAX_SOURCES", "2")
    plan = build_search_plan(
        "Maritaca AI",
        website_url="https://www.maritaca.ai/",
        known_source_urls=[
            "https://www.maritaca.ai/blog",
            "https://startups.com.br/maritaca-ai",
        ],
    )
    assert 1 <= len(plan) <= 2
    assert plan[0]["url"] == "https://www.maritaca.ai/"
    assert plan[0]["is_official_source"] is True


def test_collect_sources_defines_and_uses_combined_failures() -> None:
    text = (ROOT / "src/orchestration/node_impl.py").read_text(encoding="utf-8")
    assert "failures = critical_failures + degraded_failures" in text
    assert "status=NodeStatus.FAILED if is_failed else NodeStatus.DEGRADED" in text
    assert "known_source_urls=known_source_urls" in text


def test_quality_route_imports_timestamp_dependencies() -> None:
    text = (ROOT / "src/api/product_routes.py").read_text(encoding="utf-8")
    assert "from datetime import UTC, datetime" in text


def test_worker_has_process_healthcheck_and_logs_persisted_status() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    worker = (ROOT / "src/orchestration/worker.py").read_text(encoding="utf-8")
    assert "b'src.orchestration.worker'" in compose
    assert "workflow_finished_failed" in worker


def test_only_stable_public_directory_is_enabled_for_repaired_sources() -> None:
    sources = {
        item["source_id"]: item
        for item in json.loads((ROOT / "src/config/discovery_sources.json").read_text(encoding="utf-8"))
    }
    assert sources["open_startups_ecosystem"]["enabled_by_default"] is True
    assert sources["open_startups_ecosystem"]["base_url"].endswith("rankings-startups.html")
    for source_id in (
        "cubo_ecosystem",
        "distrito_startup_programs",
        "inovativa_startups",
        "bossa_invest_portfolio",
    ):
        assert sources[source_id]["enabled_by_default"] is False


def test_pipeline_results_expose_actionable_failure_details() -> None:
    backend = (ROOT / "src/services/product/radar_dashboard_service.py").read_text(encoding="utf-8")
    frontend = (ROOT / "frontend/src/views/RadarDashboardView.tsx").read_text(encoding="utf-8")
    assert '"error": error or None' in backend
    assert '"current_node": workflow.current_node' in backend
    assert "function runtimeItemDetail" in frontend
''',
    )


def main() -> None:
    repair_quality_route()
    repair_orchestration_nodes()
    repair_radar_service()
    repair_worker()
    repair_compose()
    repair_discovery_sources()
    repair_frontend()
    write_regression_tests()
    print("runtime output repairs applied")


if __name__ == "__main__":
    main()
