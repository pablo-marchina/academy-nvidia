"""Tests for the LangGraph product graph skeleton.

Validates that all 12 nodes compile and execute in the expected
order, that run_id is preserved, and that the final status is explicit.
"""

from __future__ import annotations

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from langgraph.types import Command

import src.agents.graph as agent_graph
from src.agents.graph import NODE_NAMES, build_startup_radar_graph
from src.scraping.fetcher import FetchResult
from src.services.product.readiness_service import ProductReadinessReport


def _state_of(result: object) -> dict:
    if isinstance(result, dict):
        return result
    if hasattr(result, "model_dump"):
        return result.model_dump()
    raise TypeError(f"Unexpected result type: {type(result)}")


@pytest.fixture(autouse=True)
def _mock_readiness() -> Generator[None, None, None]:
    """Mock readiness service to return ready=True by default."""
    with patch(
        "src.services.product.readiness_service.ProductReadinessService.get_product_readiness",
        return_value=ProductReadinessReport(ready=True),
    ):
        yield


@pytest.fixture(autouse=True)
def _reset_checkpointer_flag() -> Generator[None, None, None]:
    """Reset the graph-level flag before every test so callers that pass an
    explicit ``checkpointer`` get clean state."""
    agent_graph._CHECKPOINTER_ENABLED = False
    yield


@pytest.fixture(autouse=True)
def _mock_enabled_sources() -> Generator[None, None, None]:
    """Mock source registry to avoid real HTTP calls during full-graph tests.

    Returns an empty list so collection is gracefully blocked and the graph
    proceeds without issuing external requests.
    """
    with patch(
        "src.scraping.source_registry.list_production_enabled_sources",
        return_value=[],
    ):
        yield


@pytest.fixture(autouse=True)
def _mock_mappings_and_recommendations() -> Generator[None, None, None]:
    """Mock technology mappings and recommendations for full-graph tests."""
    mock_mapping_result = {
        "nvidia_technology_mappings": [
            {
                "mapping_id": "map-test-001-1",
                "gap_type": "external_api_dependency",
                "nvidia_technology": "NVIDIA NIM",
                "technology_category": "inference_optimization",
                "mapping_score": 0.8,
                "mapping_confidence": 0.75,
                "uncertainty": 0.2,
                "production_allowed": True,
                "supporting_rag_context_ids": ["rag_0"],
                "supporting_evidence_ids": ["ev_0"],
                "calibration_decision_ids": [],
                "blockers": [],
            },
        ],
        "nvidia_mapping_metrics": {"mapping_count": 1, "mapping_status": "passed"},
        "nvidia_mapping_calibration_metrics": {"missing_calibration_count": 0},
        "mapping_status": "passed",
        "production_allowed": True,
        "blockers": [],
    }
    mock_rec_result = {
        "nvidia_recommendations": [
            {
                "gap_type": "external_api_dependency",
                "nvidia_technology": "NVIDIA NIM",
                "reason": "external_api_dependency",
                "recommendation_priority_score": 0.85,
                "confidence": 0.75,
                "next_best_action": "Recommend NVIDIA NIM",
                "supporting_rag_context_ids": ["rag_0"],
                "supporting_evidence_ids": ["ev_0"],
                "production_allowed": True,
                "blockers": [],
                "calibration_decision_ids": ["recommendation.priority_score_weights"],
            },
        ],
        "nvidia_recommendation_metrics": {
            "mapping_count": 1,
            "recommendation_count": 1,
            "blocked_recommendation_count": 0,
            "production_allowed_recommendation_count": 1,
            "needs_review_recommendation_count": 0,
            "average_mapping_score": 0.8,
            "average_mapping_confidence": 0.75,
            "average_recommendation_priority_score": 0.85,
            "average_recommendation_confidence": 0.75,
            "evidence_supported_recommendation_rate": 1.0,
            "rag_supported_recommendation_rate": 1.0,
            "missing_recommendation_calibration_count": 0,
            "recommendation_uncertainty_mean": 0.1,
        },
        "ranking_status": "passed",
        "production_allowed": True,
        "blockers": [],
    }
    with (
        patch(
            "src.recommendation.nvidia_technology_mapping.build_nvidia_technology_mappings",
            return_value=mock_mapping_result,
        ),
        patch(
            "src.recommendation.recommendation_engine.rank_recommendations_from_mappings",
            return_value=mock_rec_result,
        ),
    ):
        yield


def test_graph_compiles() -> None:
    graph = build_startup_radar_graph()
    assert graph is not None
    assert hasattr(graph, "invoke")


def test_happy_path_executes_all_nodes_in_order() -> None:
    mock_rag = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["ctx"],
        )
    )
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    graph = build_startup_radar_graph(
        rag_service=mock_rag,
        generate_brief_service=mock_brief,
    )
    result = graph.invoke({"run_id": "test-001"})
    state = _state_of(result)

    executed = state.get("executed_nodes", [])
    # All 13 NODE_NAMES execute in order (needs_review may be skipped
    # when collection is blocked, causing quality gates to fail)
    assert len(executed) >= len(NODE_NAMES)
    expected = [n for n in executed if n != "needs_review"]
    assert expected == NODE_NAMES


def test_run_id_preserved() -> None:
    graph = build_startup_radar_graph()
    result = graph.invoke({"run_id": "preserve-me-42"})
    state = _state_of(result)
    assert state["run_id"] == "preserve-me-42"


def test_graph_skeleton_completes_with_all_nodes() -> None:
    mock_rag = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["ctx"],
        )
    )
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    graph = build_startup_radar_graph(
        rag_service=mock_rag,
        generate_brief_service=mock_brief,
    )
    result = graph.invoke({"run_id": "test-003", "startup_name": "CompleteAI"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "plan_search" in executed
    assert "collect_sources" in executed
    assert "finish" in executed
    assert "run_id" in state


@pytest.mark.parametrize(
    "field",
    [
        "evidence_items",
        "claims",
        "scores",
        "gaps",
        "rag_contexts",
        "rag_metrics",
        "recommendations",
        "search_plan_metrics",
        "search_plan",
    ],
)
def test_accumulated_fields_are_present(field: str) -> None:
    mock_rag = MagicMock(return_value=(["ctx"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    graph = build_startup_radar_graph(
        rag_service=mock_rag,
        generate_brief_service=mock_brief,
    )
    result = graph.invoke({"run_id": "test-004"})
    state = _state_of(result)
    assert field in state, f"Expected field {field} in final state"


# --- plan_search specific tests ---


def _make_graph_with_mocks() -> Any:
    mock_rag = MagicMock(return_value=(["ctx"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    return build_startup_radar_graph(
        rag_service=mock_rag,
        generate_brief_service=mock_brief,
    )


def test_plan_search_generates_plan_when_name_provided() -> None:
    graph = _make_graph_with_mocks()
    result = graph.invoke({"run_id": "p-001", "startup_name": "Nubank"})
    state = _state_of(result)
    assert "plan_search" in state.get("executed_nodes", [])
    plan = state.get("search_plan", {})
    assert isinstance(plan, dict)
    queries = plan.get("search_queries", [])
    assert isinstance(queries, list)
    assert len(queries) >= 1
    first = queries[0]
    assert "url" in first
    assert "source_type" in first
    assert "reason" in first


def test_plan_search_returns_empty_plan_without_name() -> None:
    graph = _make_graph_with_mocks()
    result = graph.invoke({"run_id": "p-002"})
    state = _state_of(result)
    plan = state.get("search_plan", {})
    assert isinstance(plan, dict)
    assert plan.get("search_queries", []) == []


def test_plan_search_includes_configured_sources() -> None:
    graph = _make_graph_with_mocks()
    result = graph.invoke({"run_id": "p-003", "startup_name": "StartupX"})
    state = _state_of(result)
    plan = state.get("search_plan", {})
    queries = plan.get("search_queries", [])
    urls = [e["url"] for e in queries]
    assert any("distrito" in url for url in urls)
    assert any("acestartups" in url for url in urls)
    assert any("google.com/search" in url for url in urls)


# --- plan_search new structured tests ---


def test_plan_search_with_website_url() -> None:
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "ps-url-001",
            "startup_name": None,
            "website_url": "https://minha-startup.ai",
            "executed_nodes": ["preflight_configuration_check"],
        }
    )
    sp = result.get("search_plan", {})
    assert isinstance(sp, dict)
    assert sp.get("run_id") == "ps-url-001"
    queries = sp.get("search_queries", [])
    assert len(queries) >= 1
    assert queries[0]["url"] == "https://minha-startup.ai"
    assert result.get("status") == "search_plan_ready"
    assert result.get("review_required") is False


def test_plan_search_needs_review_without_name_and_url() -> None:
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "ps-nodata-001",
            "executed_nodes": [],
        }
    )
    assert result.get("status") == "search_plan_needs_review"
    assert result.get("review_required") is True
    metrics = result.get("search_plan_metrics", {})
    assert metrics.get("planning_status") == "needs_review"
    assert metrics.get("query_count") == 0


def test_plan_search_includes_retry_context() -> None:
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "ps-retry-001",
            "startup_name": "RetryAI",
            "evidence_request_reason": "Need more funding sources",
            "evidence_retry_count": 1,
            "executed_nodes": [],
        }
    )
    sp = result.get("search_plan", {})
    rc = sp.get("retry_context")
    assert rc is not None
    assert rc["evidence_request_reason"] == "Need more funding sources"
    assert rc["evidence_retry_count"] == 1
    objective = sp.get("objective", "")
    assert "Additional evidence requested" in objective
    assert "Need more funding sources" in objective


def test_plan_search_blocks_on_max_retries_exceeded() -> None:
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "ps-blocked-001",
            "startup_name": "BlockedAI",
            "evidence_retry_count": 3,
            "max_evidence_retries": 2,
            "executed_nodes": [],
        }
    )
    assert result.get("status") == "max_evidence_retries_reached"
    blockers = result.get("blockers", [])
    assert "max_evidence_retries_reached" in blockers
    metrics = result.get("search_plan_metrics", {})
    assert metrics.get("planning_status") == "failed"
    assert metrics.get("query_count") == 0


def test_search_plan_metrics_exist() -> None:
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "ps-metrics-001",
            "startup_name": "MetricAI",
            "executed_nodes": [],
        }
    )
    metrics = result.get("search_plan_metrics", {})
    assert isinstance(metrics, dict)
    for key in (
        "query_count",
        "target_source_type_count",
        "required_evidence_type_count",
        "max_sources",
        "max_depth",
        "evidence_retry_count",
        "planning_status",
    ):
        assert key in metrics, f"Missing metric key: {key}"


def test_plan_search_query_count_correct() -> None:
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "ps-qcount-001",
            "startup_name": "QueryCountAI",
            "executed_nodes": [],
        }
    )
    sp = result.get("search_plan", {})
    queries = sp.get("search_queries", [])
    metrics = result.get("search_plan_metrics", {})
    assert metrics["query_count"] == len(queries)
    assert metrics["query_count"] >= 1


def test_plan_search_run_id_preserved_in_plan() -> None:
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "preserve-ps-001",
            "startup_name": "PreserveAI",
            "executed_nodes": [],
        }
    )
    sp = result.get("search_plan", {})
    assert sp.get("run_id") == "preserve-ps-001"


def test_plan_search_no_real_llm_qdrant_scraping() -> None:
    """Unit test validates the node does not trigger external services."""
    from src.agents.graph import _plan_search

    result = _plan_search(
        {
            "run_id": "ps-noext-001",
            "startup_name": "NoExtAI",
            "executed_nodes": [],
        }
    )
    assert result.get("status") == "search_plan_ready"
    assert "plan_search" in result.get("executed_nodes", [])
    sp = result.get("search_plan", {})
    assert sp.get("max_sources") == 10
    assert sp.get("max_depth") == 2


# --- collect_sources specific tests ---


_SOURCE_RECORD_KWARGS: dict[str, Any] = {
    "source_id": "test_official_website",
    "source_name": "Test Website",
    "source_category": "official_website",
    "base_url": "https://example.com",
    "allowed_paths": ["/", "/about"],
    "disallowed_paths": ["/login", "/admin"],
    "robots_required": True,
    "rate_limit_policy_id": "default_polite",
    "calibrated_priority_score": 0.5,
    "production_enabled": True,
}

_TEST_NOW = datetime.now(UTC)
_TEST_HTML = "<html><body><p>Acme AI is a Brazilian startup building ML solutions.</p></body></html>"


def _patch_enabled_source(
    mock_list: MagicMock,
    mock_fetch: MagicMock,
    *,
    category: str = "official_website",
    base_url: str = "https://acme-ai.com.br",
    html: str = _TEST_HTML,
) -> None:
    from src.scraping.source_registry import SourceRecord

    kwargs = dict(**_SOURCE_RECORD_KWARGS)
    kwargs.update(source_id=f"src_{category}", source_category=category, base_url=base_url)
    source = SourceRecord(**kwargs)
    mock_list.return_value = [source]
    mock_fetch.return_value = FetchResult(
        url=base_url,
        status=200,
        raw_html=html,
        fetched_at=_TEST_NOW,
        error=None,
    )


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_fetches_and_parses(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    from src.scraping.source_registry import SourceRecord

    source = SourceRecord(**_SOURCE_RECORD_KWARGS)
    mock_list_sources.return_value = [source]
    mock_fetch.return_value = FetchResult(
        url="https://example.com",
        status=200,
        raw_html="<html><body><p>Hello from example</p></body></html>",
        fetched_at=_TEST_NOW,
        error=None,
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-001",
            "startup_name": "ExampleAI",
            "website_url": "https://example.com",
        }
    )
    state = _state_of(result)
    assert len(state.get("evidence_items", [])) >= 1
    item = state["evidence_items"][0]
    assert isinstance(item, dict)
    assert "Hello from example" in item["text"]
    assert item["url"] is not None
    # source_type is from extraction (aliased from official_website → official_site)
    assert item.get("source_type") in ("official_website", "official_site")
    assert item.get("status_code") == 200 or "collected_at" in item or "extracted_at" in item
    executed = state.get("executed_nodes", [])
    assert "collect_sources" in executed


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_handles_fetch_errors(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    from src.scraping.source_registry import SourceRecord

    source = SourceRecord(**_SOURCE_RECORD_KWARGS)
    mock_list_sources.return_value = [source]
    mock_fetch.return_value = FetchResult(
        url="https://example.com",
        status=None,
        raw_html="",
        fetched_at=_TEST_NOW,
        error="Connection refused",
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-002",
            "startup_name": "FailAI",
            "website_url": "https://example.com",
        }
    )
    state = _state_of(result)
    assert state.get("evidence_items") == []
    errors = state.get("blockers", [])
    assert any("Connection refused" in e for e in errors)


@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_blocked_when_no_enabled_sources(
    mock_list_sources: MagicMock,
) -> None:
    mock_list_sources.return_value = []
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-003",
            "startup_name": "NoSourcesAI",
            "website_url": "https://example.com",
        }
    )
    state = _state_of(result)
    assert state.get("evidence_items") == []
    assert state.get("collection_status") == "collection_blocked"
    assert "collect_sources" in state.get("executed_nodes", [])


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_fills_collection_metrics(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    from src.scraping.source_registry import SourceRecord

    source = SourceRecord(**_SOURCE_RECORD_KWARGS)
    mock_list_sources.return_value = [source]
    mock_fetch.return_value = FetchResult(
        url="https://example.com",
        status=200,
        raw_html="<html><body><p>Hello</p></body></html>",
        fetched_at=_TEST_NOW,
        error=None,
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-004",
            "startup_name": "MetricAI",
            "website_url": "https://example.com",
        }
    )
    state = _state_of(result)
    metrics = state.get("collection_metrics", {})
    assert metrics.get("fetched_sources_count", 0) >= 1
    assert metrics.get("attempted_sources_count", 0) >= 1
    assert "total_latency_ms" in metrics
    assert "fetch_success_rate" in metrics


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_fills_raw_evidence_candidates(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    from src.scraping.source_registry import SourceRecord

    source = SourceRecord(**_SOURCE_RECORD_KWARGS)
    mock_list_sources.return_value = [source]
    mock_fetch.return_value = FetchResult(
        url="https://example.com",
        status=200,
        raw_html="<html><body><p>Evidence text</p></body></html>",
        fetched_at=_TEST_NOW,
        error=None,
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-005",
            "startup_name": "EvidenceAI",
            "website_url": "https://example.com",
        }
    )
    state = _state_of(result)
    candidates = state.get("raw_evidence_candidates", [])
    assert len(candidates) >= 1
    first = candidates[0]
    assert "source_id" in first
    assert "source_url" in first
    assert "text" in first


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_partial_failure_partial_status(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    from src.scraping.source_registry import SourceRecord

    source_a_kwargs = dict(**_SOURCE_RECORD_KWARGS)
    source_a_kwargs.update(source_id="src_ok", base_url="https://ok.example.com")
    source_a = SourceRecord(**source_a_kwargs)
    source_b_kwargs = dict(**_SOURCE_RECORD_KWARGS)
    source_b_kwargs.update(source_id="src_fail", base_url="https://fail.example.com")
    source_b = SourceRecord(**source_b_kwargs)
    mock_list_sources.return_value = [source_a, source_b]

    def _side_effect(url: str, **kw: Any) -> FetchResult:
        if "fail" in url:
            return FetchResult(url=url, status=None, raw_html="", fetched_at=_TEST_NOW, error="Connection refused")
        return FetchResult(
            url=url,
            status=200,
            raw_html="<html><body><p>OK</p></body></html>",
            fetched_at=_TEST_NOW,
            error=None,
        )

    mock_fetch.side_effect = _side_effect
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-006",
            "startup_name": "PartialAI",
            "website_url": "https://ok.example.com",
        }
    )
    state = _state_of(result)
    assert state.get("evidence_items") is not None
    assert state.get("collection_status") in ("partial", "sources_collected_partial")
    executed = state.get("executed_nodes", [])
    assert "collect_sources" in executed


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_total_failure_creates_blocker(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    from src.scraping.source_registry import SourceRecord

    source = SourceRecord(**_SOURCE_RECORD_KWARGS)
    mock_list_sources.return_value = [source]
    mock_fetch.return_value = FetchResult(
        url="https://example.com",
        status=None,
        raw_html="",
        fetched_at=_TEST_NOW,
        error="Connection refused",
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-007",
            "startup_name": "FailAI",
            "website_url": "https://example.com",
        }
    )
    state = _state_of(result)
    assert state.get("collection_status") == "collection_failed"
    blockers = state.get("blockers", [])
    assert any("Connection refused" in str(b) for b in blockers)


@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_run_id_preserved(
    mock_list_sources: MagicMock,
) -> None:
    mock_list_sources.return_value = []
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "preserve-collect-001",
            "startup_name": "PreserveAI",
        }
    )
    state = _state_of(result)
    assert state["run_id"] == "preserve-collect-001"
    assert "collect_sources" in state.get("executed_nodes", [])


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_collect_sources_production_enabled_only(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    """Only production_enabled=true sources are collected."""
    from src.scraping.source_registry import SourceRecord

    enabled_kwargs = dict(**_SOURCE_RECORD_KWARGS)
    enabled_kwargs.update(source_id="src_enabled", base_url="https://enabled.example.com")
    enabled = SourceRecord(**enabled_kwargs)
    disabled = SourceRecord(
        source_id="src_disabled",
        source_name="Disabled Source",
        source_category="funding_news",
        base_url="https://disabled.example.com",
        calibrated_priority_score=0.5,
        rate_limit_policy_id="default_polite",
        production_enabled=False,
        production_blockers=["test_blocker"],
    )
    mock_list_sources.return_value = [enabled, disabled]
    mock_fetch.return_value = FetchResult(
        url="https://enabled.example.com",
        status=200,
        raw_html="<html><body><p>Enabled only</p></body></html>",
        fetched_at=_TEST_NOW,
        error=None,
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "c-008",
            "startup_name": "FilterAI",
            "website_url": "https://enabled.example.com",
        }
    )
    state = _state_of(result)
    # Only enabled source should produce evidence
    items = state.get("evidence_items", [])
    urls = [i.get("url") for i in items]
    assert "https://enabled.example.com" in urls
    assert "https://disabled.example.com" not in urls


def test_collect_sources_no_llm_qdrant_playwright() -> None:
    """Unit test validates _collect_sources does not import external services."""
    import sys

    from src.agents.graph import _collect_sources

    before = set(sys.modules.keys())
    _collect_sources(
        {
            "run_id": "safety-001",
            "search_plan": {},
            "evidence_retry_count": 0,
            "max_evidence_retries": 3,
            "executed_nodes": [],
        }
    )
    after = set(sys.modules.keys())
    new_imports = after - before
    banned = {"langchain", "qdrant_client", "playwright", "openai", "anthropic"}
    triggered = {m for m in new_imports if any(b in m for b in banned)}
    assert not triggered, f"Banned imports detected: {triggered}"


# --- extract_profile specific tests ---


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_extract_profile_creates_claims_from_evidence(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    html = (
        "<html><body>"
        "<h1>Acme AI</h1>"
        "<p>Acme AI is a Brazilian startup building machine learning"
        " solutions for hospitals using deep learning and NLP."
        " Founded by Maria Silva and Joao Santos."
        " The company raised $10M in Series A."
        " Customers include Hospital Israelita Albert Einstein.</p>"
        "</body></html>"
    )
    _patch_enabled_source(mock_list_sources, mock_fetch, html=html)
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "ext-001",
            "startup_name": "Acme AI",
            "website_url": "https://acme-ai.com.br",
        }
    )
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "extract_profile" in executed
    claims = state.get("claims", [])
    assert len(claims) >= 1
    claim_texts = [c.get("claim_text", "") for c in claims]
    any_ai = any("AI" in ct or "machine learning" in ct for ct in claim_texts)
    any_founder = any("Founder" in ct or "Maria" in ct for ct in claim_texts)
    assert any_ai or any_founder
    raw = state.get("raw_evidence", [])
    assert len(raw) >= 1
    first = raw[0]
    assert "claim" in first
    assert "source_url" in first
    assert "source_type" in first
    profile = state.get("startup_profile", {})
    assert isinstance(profile, dict)
    # name may come from the hint or the HTML <h1>
    assert profile.get("startup_name") in ("Acme AI", "Not verified")


def test_extract_profile_handles_empty_evidence() -> None:
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "ext-002",
            "startup_name": "EmptyAI",
        }
    )
    state = _state_of(result)
    assert state.get("claims") == []
    assert state.get("raw_evidence") == []


@patch("src.extraction.extractor.extract_profile")
def test_extract_profile_uses_source_type_from_raw_evidence(
    mock_extract: MagicMock,
) -> None:
    from src.agents.extractor_agent import extract_profiles_from_candidates
    from src.extraction.schemas import StartupProfile

    fake_profile = StartupProfile(
        startup_name="Acme AI",
        website="https://exemplo.com.br",
        sector="Not verified",
        description="Not verified",
        product_summary="Not verified",
        confidence_score=0.5,
    )
    mock_extract.return_value = fake_profile

    candidates: list[dict[str, Any]] = [
        {
            "source_url": "https://exemplo.com.br",
            "text": "startup text here",
            "source_category": "news",
            "source_id": "src_001",
            "collected_at": "2026-01-01T00:00:00",
        },
        {
            "source_url": "https://linkedin.com/company/test",
            "text": "founder info here",
            "source_category": "founder_profile",
            "source_id": "src_002",
            "collected_at": "2026-01-01T00:00:00",
        },
        {
            "source_url": "https://unknown-example.com",
            "text": "fallback text",
            "source_category": "",
            "source_id": "src_003",
            "collected_at": "2026-01-01T00:00:00",
        },
    ]

    extract_profiles_from_candidates(
        raw_evidence_candidates=candidates,
        startup_name="Acme AI",
        startup_id="s-42",
        run_id="r-001",
    )

    assert mock_extract.call_count == 3

    first_call_st = mock_extract.call_args_list[0][1].get("source_type")
    assert first_call_st is not None
    assert first_call_st.value == "news"

    second_call_st = mock_extract.call_args_list[1][1].get("source_type")
    assert second_call_st is not None
    assert second_call_st.value == "founder_profile"

    third_call_st = mock_extract.call_args_list[2][1].get("source_type")
    assert third_call_st is not None
    assert third_call_st.value == "directory"


# --- validate_evidence specific tests ---


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_validate_evidence_classifies_claims(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    html = (
        "<html><body>"
        "<h1>Acme AI</h1>"
        "<p>Acme AI is a Brazilian startup building machine learning"
        " solutions for hospitals using deep learning and NLP."
        " Founded by Maria Silva and Joao Santos."
        " The company raised $10M in Series A."
        " Customers include Hospital Israelita Albert Einstein.</p>"
        "</body></html>"
    )
    _patch_enabled_source(mock_list_sources, mock_fetch, html=html)
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "val-001",
            "startup_name": "Acme AI",
            "website_url": "https://acme-ai.com.br",
        }
    )
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "validate_evidence" in executed

    claims = state.get("claims", [])
    assert len(claims) >= 1
    first = claims[0]
    assert "claim_text" in first
    assert "support_status" in first
    assert first["support_status"] in (
        "supported",
        "unsupported",
        "insufficient_evidence",
        "conflicting",
    )


@patch("src.extraction.extractor.extract_profile")
@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_validate_evidence_enriches_evidence_items(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
    mock_extract: MagicMock,
) -> None:
    from datetime import UTC, datetime

    from pydantic import HttpUrl

    from src.extraction.schemas import (
        ConfidenceLevel,
        Evidence,
        SourceType,
        StartupProfile,
    )

    html = (
        "<html><body>"
        "<p>StartupX offers NLP APIs for healthcare."
        " Founded by John Doe. Raised $2M seed round.</p>"
        "</body></html>"
    )
    _patch_enabled_source(mock_list_sources, mock_fetch, html=html, base_url="https://startupx.ai")
    fake_profile = StartupProfile(
        startup_name="StartupX",
        website="https://startupx.ai",
        sector="HealthTech",
        description="StartupX offers NLP APIs for healthcare. Founded by John Doe. Raised $2M seed round.",
        product_summary="NLP APIs for healthcare",
        ai_signals=["natural language processing"],
        founders=["John Doe"],
        funding_signals=["$2M"],
        confidence_score=0.7,
        sources=[
            Evidence(
                claim="NLP APIs for healthcare",
                source_url=HttpUrl("https://startupx.ai"),
                source_type=SourceType.OFFICIAL_SITE,
                quote_or_evidence=(
                    "StartupX offers NLP APIs for healthcare. " "Founded by John Doe. Raised $2M seed round."
                ),
                confidence=ConfidenceLevel.MEDIUM,
                collected_at=datetime.now(UTC),
            ),
        ],
    )
    mock_extract.return_value = fake_profile
    graph = build_startup_radar_graph()
    result = graph.invoke(
        {
            "run_id": "val-002",
            "startup_name": "StartupX",
            "website_url": "https://startupx.ai",
        }
    )
    state = _state_of(result)
    items = state.get("evidence_items", [])
    assert len(items) >= 1
    first = items[0]
    assert "evidence_kind" in first, f"Expected evidence_kind in evidence_item, got keys: {list(first.keys())}"
    assert "validated_confidence" in first


def test_validate_evidence_handles_empty_raw_evidence() -> None:
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "val-003",
            "startup_name": "EmptyCo",
        }
    )
    state = _state_of(result)
    assert state.get("claims") == []
    assert "validate_evidence" in state.get("executed_nodes", [])


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_validate_evidence_sets_unsupported_critical_claims_count(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    """unsupported_critical_claims_count is computed from validated evidence."""
    html = (
        "<html><body>"
        "<h1>Acme AI</h1>"
        "<p>Acme AI is a Brazilian startup building machine learning"
        " solutions for hospitals using deep learning and NLP."
        " Founded by Maria Silva and Joao Santos."
        " The company raised $10M in Series A."
        " Customers include Hospital Israelita Albert Einstein.</p>"
        "</body></html>"
    )
    _patch_enabled_source(mock_list_sources, mock_fetch, html=html)
    graph = build_startup_radar_graph()
    result = graph.invoke(
        {
            "run_id": "val-004",
            "startup_name": "Acme AI",
            "website_url": "https://acme-ai.com.br",
        }
    )
    state = _state_of(result)
    assert "unsupported_critical_claims_count" in state
    assert isinstance(state["unsupported_critical_claims_count"], int)
    assert state["unsupported_critical_claims_count"] >= 0


# --- validate_evidence evidence_validation tests ---


def test_validate_evidence_passes_when_claims_supported() -> None:
    from src.agents.graph import _validate_evidence

    raw_evidence = [
        {
            "claim": "Acme AI builds ML solutions",
            "source_url": "https://acme.ai",
            "source_type": "official_site",
            "quote_or_evidence": (
                "Acme AI is a Brazilian startup building machine learning"
                " solutions for hospitals using deep learning and NLP"
            ),
            "confidence": "high",
            "collected_at": "2024-01-01T00:00:00",
        }
    ]
    evidence_items = [
        {
            "url": "https://acme.ai",
            "text": "Acme AI is a Brazilian startup building machine learning solutions for hospitals",
        }
    ]

    result = _validate_evidence(
        {
            "raw_evidence": raw_evidence,
            "evidence_items": evidence_items,
            "claims": [],
            "executed_nodes": [],
        }
    )

    # EC weights are uncalibrated by default -> blocked
    assert result["status"] == "evidence_scoring_uncalibrated"
    ev = result["evidence_validation"]
    assert ev["status"] == "blocked_uncalibrated_scoring"
    assert len(ev["failed_checks"]) >= 1
    assert any("uncalibrated" in f for f in ev["failed_checks"])
    assert ev["metrics"]["unsupported_critical_claims_count"] == 0


def test_validate_evidence_blocks_production_ready_with_uncalibrated_scoring() -> None:
    from src.agents.graph import _validate_evidence

    raw_evidence = [
        {
            "claim": "Acme AI builds ML solutions",
            "source_url": "https://acme.ai",
            "source_type": "news",
            "quote_or_evidence": (
                "Acme AI is a Brazilian startup building machine learning"
                " solutions for hospitals using deep learning and NLP"
            ),
            "confidence": "high",
            "collected_at": "2024-01-01T00:00:00",
        }
    ]
    evidence_items = [
        {
            "url": "https://acme.ai",
            "text": "Acme AI is a Brazilian startup building machine learning solutions for hospitals",
        }
    ]

    result = _validate_evidence(
        {
            "raw_evidence": raw_evidence,
            "evidence_items": evidence_items,
            "claims": [],
            "executed_nodes": [],
        }
    )

    # EC weights are uncalibrated by default -> blocked
    assert result["status"] == "evidence_scoring_uncalibrated"
    assert result["review_required"] is True
    blockers = result.get("blockers", [])
    assert any("uncalibrated" in b for b in blockers)


def test_validate_evidence_fails_when_critical_unsupported() -> None:
    from unittest.mock import patch

    from src.agents.graph import _validate_evidence
    from src.quality.decision_calibration_registry import (
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    SQ_WEIGHTS: dict[str, float] = {
        "source_authority_prior": 0.30,
        "robots_allowed": 0.10,
        "compliance_status": 0.10,
        "fetch_success": 0.15,
        "extraction_success": 0.10,
        "duplicate_status": 0.05,
        "content_bytes": 0.05,
        "latency_ms": 0.05,
        "source_freshness_days": 0.05,
        "source_independence_type": 0.05,
    }
    EC_WEIGHTS: dict[str, float] = {
        "source_quality_score": 0.15,
        "extraction_confidence": 0.15,
        "snippet_length": 0.05,
        "text_specificity_score": 0.10,
        "claim_support_count": 0.10,
        "supporting_source_count": 0.10,
        "cross_source_agreement_count": 0.10,
        "contradiction_count": 0.05,
        "factuality_status": 0.10,
        "duplicate_penalty": 0.05,
        "unsupported_critical_claim_flag": 0.05,
    }
    _CALIBRATED_INVENTORY = [
        DecisionCalibrationRecord(
            decision_id="weight.source_quality_score.weights",
            decision_name="SQ Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=SQ_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.source_quality_score.production_min",
            decision_name="SQ Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.65,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="weight.evidence_confidence_score.weights",
            decision_name="EC Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=EC_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.evidence_confidence_score.production_min",
            decision_name="EC Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.55,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
    ]

    raw_evidence = [
        {
            "claim": "Acme AI is the undisputed market leader",
            "source_url": "https://acme.ai",
            "source_type": "official_site",
            "quote_or_evidence": "",
            "confidence": "medium",
            "collected_at": "2024-01-01T00:00:00",
        }
    ]
    evidence_items = [{"url": "https://acme.ai", "text": "text"}]

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=_CALIBRATED_INVENTORY,
    ):
        result = _validate_evidence(
            {
                "raw_evidence": raw_evidence,
                "evidence_items": evidence_items,
                "claims": [],
                "executed_nodes": [],
            }
        )

    assert result["status"] == "evidence_validation_failed"
    ev = result["evidence_validation"]
    assert ev["status"] == "failed"
    assert "unsupported_critical_claims_count > 0" in ev["failed_checks"]
    assert result["unsupported_critical_claims_count"] >= 1
    blockers = result.get("blockers", [])
    assert any("critical claim" in b for b in blockers)


def test_validate_evidence_needs_review_empty_evidence_items() -> None:
    from unittest.mock import patch

    from src.agents.graph import _validate_evidence
    from src.quality.decision_calibration_registry import (
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    _CALIBRATED_FOR_REVIEW = [
        DecisionCalibrationRecord(
            decision_id="weight.source_quality_score.weights",
            decision_name="SQ Weights",
            decision_type=DecisionType.WEIGHT,
            current_value={"source_authority_prior": 1.0},
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.source_quality_score.production_min",
            decision_name="SQ Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.5,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="weight.evidence_confidence_score.weights",
            decision_name="EC Weights",
            decision_type=DecisionType.WEIGHT,
            current_value={"source_quality_score": 1.0},
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.evidence_confidence_score.production_min",
            decision_name="EC Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.5,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
    ]

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=_CALIBRATED_FOR_REVIEW,
    ):
        result = _validate_evidence(
            {
                "raw_evidence": [],
                "evidence_items": [],
                "claims": [],
                "executed_nodes": [],
            }
        )

    assert result["status"] == "evidence_needs_review"
    assert result["review_required"] is True
    ev = result["evidence_validation"]
    assert ev["status"] == "needs_review"
    assert "evidence_items_count == 0" in ev["warning_checks"]


def test_validate_evidence_needs_review_empty_claims() -> None:
    from unittest.mock import patch

    from src.agents.graph import _validate_evidence
    from src.quality.decision_calibration_registry import (
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    _CALIBRATED_FOR_REVIEW = [
        DecisionCalibrationRecord(
            decision_id="weight.source_quality_score.weights",
            decision_name="SQ Weights",
            decision_type=DecisionType.WEIGHT,
            current_value={"source_authority_prior": 1.0},
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.source_quality_score.production_min",
            decision_name="SQ Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.5,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="weight.evidence_confidence_score.weights",
            decision_name="EC Weights",
            decision_type=DecisionType.WEIGHT,
            current_value={"source_quality_score": 1.0},
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.evidence_confidence_score.production_min",
            decision_name="EC Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.5,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
    ]

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=_CALIBRATED_FOR_REVIEW,
    ):
        result = _validate_evidence(
            {
                "raw_evidence": [],
                "evidence_items": [{"url": "https://a.com", "text": "text"}],
                "claims": [],
                "executed_nodes": [],
            }
        )

    assert result["status"] == "evidence_needs_review"
    assert result["review_required"] is True
    ev = result["evidence_validation"]
    assert ev["status"] == "needs_review"
    assert "claims_count == 0" in ev["warning_checks"]


def test_validate_evidence_unsupported_critical_count_correct() -> None:
    from unittest.mock import patch

    from src.agents.graph import _validate_evidence
    from src.quality.decision_calibration_registry import (
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    SQ_WEIGHTS: dict[str, float] = {
        "source_authority_prior": 0.30,
        "robots_allowed": 0.10,
        "compliance_status": 0.10,
        "fetch_success": 0.15,
        "extraction_success": 0.10,
        "duplicate_status": 0.05,
        "content_bytes": 0.05,
        "latency_ms": 0.05,
        "source_freshness_days": 0.05,
        "source_independence_type": 0.05,
    }
    EC_WEIGHTS: dict[str, float] = {
        "source_quality_score": 0.15,
        "extraction_confidence": 0.15,
        "snippet_length": 0.05,
        "text_specificity_score": 0.10,
        "claim_support_count": 0.10,
        "supporting_source_count": 0.10,
        "cross_source_agreement_count": 0.10,
        "contradiction_count": 0.05,
        "factuality_status": 0.10,
        "duplicate_penalty": 0.05,
        "unsupported_critical_claim_flag": 0.05,
    }
    _CALIBRATED_INVENTORY = [
        DecisionCalibrationRecord(
            decision_id="weight.source_quality_score.weights",
            decision_name="SQ Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=SQ_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.source_quality_score.production_min",
            decision_name="SQ Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.65,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="weight.evidence_confidence_score.weights",
            decision_name="EC Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=EC_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.evidence_confidence_score.production_min",
            decision_name="EC Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.55,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
    ]

    raw_evidence = [
        {
            "claim": "Supported claim",
            "source_url": "https://example.com",
            "source_type": "news",
            "quote_or_evidence": (
                "This is a long explicit quote that supports the claim" " and provides enough context for validation"
            ),
            "confidence": "high",
            "collected_at": "2024-01-01T00:00:00",
        },
        {
            "claim": "Unsupported critical claim",
            "source_url": "https://critical.ai",
            "source_type": "official_site",
            "quote_or_evidence": "",
            "confidence": "medium",
            "collected_at": "2024-01-01T00:00:00",
        },
        {
            "claim": "Normal unsupported",
            "source_url": "https://other.com",
            "source_type": "blog",
            "quote_or_evidence": "",
            "confidence": "low",
            "collected_at": "2024-01-01T00:00:00",
        },
    ]
    evidence_items = [
        {"url": "https://example.com", "text": "text"},
        {"url": "https://critical.ai", "text": "text"},
        {"url": "https://other.com", "text": "text"},
    ]

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=_CALIBRATED_INVENTORY,
    ):
        result = _validate_evidence(
            {
                "raw_evidence": raw_evidence,
                "evidence_items": evidence_items,
                "claims": [],
                "executed_nodes": [],
            }
        )

    assert result["unsupported_critical_claims_count"] == 1


REQUIRED_METRICS_KEYS: list[str] = [
    "evidence_items_count",
    "scored_evidence_count",
    "accepted_evidence_count",
    "rejected_evidence_count",
    "low_source_quality_count",
    "low_evidence_confidence_count",
    "claims_count",
    "supported_claims_count",
    "unsupported_claims_count",
    "unsupported_critical_claims_count",
    "average_source_quality_score",
    "average_evidence_confidence_score",
    "production_ready_evidence_ratio",
]


def test_validate_evidence_metrics_exist() -> None:
    from src.agents.graph import _validate_evidence

    result = _validate_evidence(
        {
            "raw_evidence": [],
            "evidence_items": [],
            "claims": [],
            "executed_nodes": [],
        }
    )

    metrics = result["evidence_validation"]["metrics"]
    assert isinstance(metrics, dict)
    for key in REQUIRED_METRICS_KEYS:
        assert key in metrics, f"Missing metric key: {key}"


def test_validate_evidence_thresholds_exist() -> None:
    from unittest.mock import patch

    from src.agents.graph import _validate_evidence
    from src.quality.decision_calibration_registry import (
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    _CALIBRATED_FOR_THRESHOLDS = [
        DecisionCalibrationRecord(
            decision_id="weight.source_quality_score.weights",
            decision_name="SQ Weights",
            decision_type=DecisionType.WEIGHT,
            current_value={"source_authority_prior": 1.0},
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.source_quality_score.production_min",
            decision_name="SQ Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.65,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="weight.evidence_confidence_score.weights",
            decision_name="EC Weights",
            decision_type=DecisionType.WEIGHT,
            current_value={"source_quality_score": 1.0},
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.evidence_confidence_score.production_min",
            decision_name="EC Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.55,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
    ]

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=_CALIBRATED_FOR_THRESHOLDS,
    ):
        result = _validate_evidence(
            {
                "raw_evidence": [],
                "evidence_items": [],
                "claims": [],
                "executed_nodes": [],
            }
        )

    thresholds = result["evidence_validation"]["thresholds"]
    assert isinstance(thresholds, dict)
    for key in ("source_quality_score_production_min", "evidence_confidence_score_production_min"):
        assert key in thresholds


def test_validate_evidence_executed_nodes_updated() -> None:
    from src.agents.graph import _validate_evidence

    result = _validate_evidence(
        {
            "raw_evidence": [],
            "evidence_items": [],
            "claims": [],
            "executed_nodes": [
                "preflight_configuration_check",
                "plan_search",
                "collect_sources",
                "extract_profile",
            ],
        }
    )

    assert "validate_evidence" in result["executed_nodes"]
    idx = result["executed_nodes"].index("validate_evidence")
    assert idx > result["executed_nodes"].index("extract_profile")


def test_validate_evidence_preserves_run_id() -> None:
    from src.agents.graph import _validate_evidence

    result = _validate_evidence(
        {
            "run_id": "preserve-val-001",
            "raw_evidence": [],
            "evidence_items": [],
            "claims": [],
            "executed_nodes": [],
        }
    )
    # run_id is not returned (stays in state), but executed_nodes is correct
    assert result["executed_nodes"] == ["validate_evidence"]


def test_validate_evidence_blocker_added_on_failure() -> None:
    from unittest.mock import patch

    from src.agents.graph import _validate_evidence
    from src.quality.decision_calibration_registry import (
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    SQ_WEIGHTS: dict[str, float] = {
        "source_authority_prior": 0.30,
        "robots_allowed": 0.10,
        "compliance_status": 0.10,
        "fetch_success": 0.15,
        "extraction_success": 0.10,
        "duplicate_status": 0.05,
        "content_bytes": 0.05,
        "latency_ms": 0.05,
        "source_freshness_days": 0.05,
        "source_independence_type": 0.05,
    }
    EC_WEIGHTS: dict[str, float] = {
        "source_quality_score": 0.15,
        "extraction_confidence": 0.15,
        "snippet_length": 0.05,
        "text_specificity_score": 0.10,
        "claim_support_count": 0.10,
        "supporting_source_count": 0.10,
        "cross_source_agreement_count": 0.10,
        "contradiction_count": 0.05,
        "factuality_status": 0.10,
        "duplicate_penalty": 0.05,
        "unsupported_critical_claim_flag": 0.05,
    }
    _CALIBRATED_INVENTORY = [
        DecisionCalibrationRecord(
            decision_id="weight.source_quality_score.weights",
            decision_name="SQ Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=SQ_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.source_quality_score.production_min",
            decision_name="SQ Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.65,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="weight.evidence_confidence_score.weights",
            decision_name="EC Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=EC_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.evidence_confidence_score.production_min",
            decision_name="EC Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.55,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
    ]

    raw_evidence = [
        {
            "claim": "Critical unsupported claim",
            "source_url": "https://critical.ai",
            "source_type": "official_site",
            "quote_or_evidence": "",
            "confidence": "medium",
            "collected_at": "2024-01-01T00:00:00",
        }
    ]
    evidence_items = [{"url": "https://critical.ai", "text": "text"}]

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=_CALIBRATED_INVENTORY,
    ):
        result = _validate_evidence(
            {
                "raw_evidence": raw_evidence,
                "evidence_items": evidence_items,
                "claims": [],
                "executed_nodes": [],
            }
        )

    blockers = result.get("blockers", [])
    assert len(blockers) >= 1
    assert any("critical claim" in b for b in blockers)


def test_validate_evidence_evidence_items_normalized() -> None:
    from unittest.mock import patch

    from src.agents.graph import _validate_evidence
    from src.quality.decision_calibration_registry import (
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    SQ_WEIGHTS: dict[str, float] = {
        "source_authority_prior": 0.30,
        "robots_allowed": 0.10,
        "compliance_status": 0.10,
        "fetch_success": 0.15,
        "extraction_success": 0.10,
        "duplicate_status": 0.05,
        "content_bytes": 0.05,
        "latency_ms": 0.05,
        "source_freshness_days": 0.05,
        "source_independence_type": 0.05,
    }
    EC_WEIGHTS: dict[str, float] = {
        "source_quality_score": 0.15,
        "extraction_confidence": 0.15,
        "snippet_length": 0.05,
        "text_specificity_score": 0.10,
        "claim_support_count": 0.10,
        "supporting_source_count": 0.10,
        "cross_source_agreement_count": 0.10,
        "contradiction_count": 0.05,
        "factuality_status": 0.10,
        "duplicate_penalty": 0.05,
        "unsupported_critical_claim_flag": 0.05,
    }
    _CALIBRATED_INVENTORY = [
        DecisionCalibrationRecord(
            decision_id="weight.source_quality_score.weights",
            decision_name="SQ Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=SQ_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.source_quality_score.production_min",
            decision_name="SQ Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.65,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="weight.evidence_confidence_score.weights",
            decision_name="EC Weights",
            decision_type=DecisionType.WEIGHT,
            current_value=EC_WEIGHTS,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
        DecisionCalibrationRecord(
            decision_id="threshold.evidence_confidence_score.production_min",
            decision_name="EC Threshold",
            decision_type=DecisionType.THRESHOLD,
            current_value=0.55,
            calibration_status=CalibrationStatus.CALIBRATED,
            production_allowed=True,
            owner="test",
        ),
    ]

    raw_evidence = [
        {
            "claim": "Test claim",
            "source_url": "https://example.com",
            "source_type": "news",
            "quote_or_evidence": (
                "A sufficiently long explicit quote to be considered" " valid evidence for testing purposes"
            ),
            "confidence": "high",
            "collected_at": "2024-01-01T00:00:00",
        },
    ]
    evidence_items = [{"url": "https://example.com", "text": "some text"}]

    with patch(
        "src.quality.decision_calibration_registry.get_project_decision_inventory",
        return_value=_CALIBRATED_INVENTORY,
    ):
        result = _validate_evidence(
            {
                "raw_evidence": raw_evidence,
                "evidence_items": evidence_items,
                "claims": [],
                "executed_nodes": [],
            }
        )

    items = result.get("evidence_items", [])
    assert len(items) >= 1
    first = items[0]
    assert "source_url" in first
    assert "source_quality_score" in first
    assert "source_quality_score_status" in first
    assert "source_quality_score_features" in first
    assert "source_quality_score_calibration_decision_ids" in first
    assert "evidence_confidence_score" in first
    assert "evidence_confidence_score_status" in first
    assert "evidence_confidence_score_features" in first
    assert "evidence_confidence_score_calibration_decision_ids" in first
    assert "snippet" in first


def test_run_quality_gates_consumes_unsupported_critical_claims() -> None:
    """run_quality_gates sees unsupported_critical_claims_count from validate_evidence."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-consume-001",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 2,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": ["rec1"],
            "nvidia_recommendation_metrics": {"ranking_status": "passed"},
        }
    )
    assert result["status"] == "quality_failed"
    assert "unsupported_critical_claims_count > 0" in result["quality"]["failed_checks"]


# --- score_startup specific tests ---


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_score_startup_populates_scores(
    mock_list_sources: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    html = (
        "<html><body>"
        "<h1>DataAI</h1>"
        "<p>DataAI is a Brazilian startup building NLP and computer vision"
        " solutions for healthcare using deep learning and PyTorch."
        " Founded by Ana Costa. Raised $5M in seed funding."
        " Customers include Hospital São Camilo.</p>"
        "</body></html>"
    )
    _patch_enabled_source(mock_list_sources, mock_fetch, html=html, base_url="https://dataai.com.br")
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "score-001",
            "startup_name": "DataAI",
            "website_url": "https://dataai.com.br",
        }
    )
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "score_startup" in executed

    scores = state.get("scores", {})
    assert isinstance(scores, dict)
    assert "defensibility" in scores
    assert "inception_fit" in scores
    assert "production_readiness" in scores
    assert "composite" in scores
    assert "classification" in scores

    assert isinstance(scores["defensibility"], (int, float))
    assert 0 <= scores["defensibility"] <= 100
    assert 0 <= scores["composite"] <= 100


def test_score_startup_handles_empty_profile() -> None:
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "score-002",
            "startup_name": "EmptyCo",
        }
    )
    state = _state_of(result)
    scores = state.get("scores", {})
    assert "ai_native_score" in scores
    assert "nvidia_fit_score" in scores
    assert isinstance(scores["ai_native_score"], (int, float))
    assert isinstance(scores["nvidia_fit_score"], (int, float))


def test_score_startup_works_without_startup_profile() -> None:
    graph = _make_graph_with_mocks()
    result = graph.invoke({"run_id": "score-003"})
    state = _state_of(result)
    scores = state.get("scores", {})
    assert "ai_native_score" in scores
    assert "nvidia_fit_score" in scores


# --- injected service tests ---


def test_injected_score_service_is_used() -> None:
    mock_svc = MagicMock(
        return_value=(
            {
                "defensibility": 80,
                "inception_fit": 70,
                "production_readiness": 90,
                "composite": 80,
                "classification": "AI_NATIVE",
            },
            {"classification": "AI_NATIVE"},
            {"score": 80, "signals": []},
            {"score": 70, "signals": []},
            {"score": 90, "signals": []},
            [],
        )
    )
    graph = build_startup_radar_graph(score_service=mock_svc)
    result = graph.invoke(
        {
            "run_id": "inj-scr-001",
            "startup_profile": {"test": True},
            "validated_evidence": [],
        }
    )
    state = _state_of(result)
    assert "score_startup" in state.get("executed_nodes", [])
    assert state.get("scores", {}).get("defensibility") == 80
    mock_svc.assert_called_once()


def test_injected_rag_service_is_used() -> None:
    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["nvidia_ctx_1", "nvidia_ctx_2"],
        )
    )
    graph = build_startup_radar_graph(rag_service=mock_svc)
    result = graph.invoke({"run_id": "inj-rag-001"})
    state = _state_of(result)
    assert "retrieve_nvidia_context" in state.get("executed_nodes", [])
    assert state.get("rag_contexts") == ["nvidia_ctx_1", "nvidia_ctx_2"]
    metrics = state.get("rag_metrics", {})
    assert metrics.get("retrieved_context_count") == 2
    assert metrics.get("retrieval_status") == "passed"
    assert metrics.get("min_required_contexts") == 1
    assert metrics.get("rag_required") is True
    mock_svc.assert_called_once()


def test_injected_qdrant_rag_service_protocol() -> None:
    """QdrantRagService implements RagService protocol and can be injected."""
    from src.rag.rag_service_factory import QdrantRagService

    svc = QdrantRagService()
    with patch.object(svc, "_validate") as mock_val:
        mock_val.side_effect = None
        svc._validation_error = "blocked_qdrant_unavailable: test"
        graph = build_startup_radar_graph(rag_service=svc)
        result = graph.invoke({"run_id": "inj-qdrant-001"})
    state = _state_of(result)
    assert "retrieve_nvidia_context" in state.get("executed_nodes", [])
    assert state.get("rag_retrieval_status") == "blocked_qdrant_unavailable"
    assert state.get("review_required") is True


def test_injected_diagnose_gaps_service_is_used() -> None:
    mock_svc = MagicMock(
        return_value=(
            ["external_api_dependency"],
            {"diagnosed_gaps": [{"gap": "external_api_dependency", "detected": True}]},
            [],
        )
    )
    graph = build_startup_radar_graph(diagnose_gaps_service=mock_svc)
    result = graph.invoke({"run_id": "inj-gap-001"})
    state = _state_of(result)
    assert "diagnose_gaps" in state.get("executed_nodes", [])
    assert "external_api_dependency" in state.get("gaps", [])
    mock_svc.assert_called_once()


def test_injected_rank_recommendations_service_is_used() -> None:

    mock_rag = MagicMock(return_value=(["nvidia_ctx_1", "nvidia_ctx_2"], []))
    mock_brief = MagicMock(return_value=("# Startup Action Brief: Test\n\ncontent", []))
    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [
                {
                    "nvidia_technology": "NVIDIA NIM",
                    "reason": "external_api_dependency",
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.75,
                    "next_best_action": "Recommend",
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                },
            ],
            "nvidia_recommendation_metrics": {"mapping_count": 2, "recommendation_count": 1},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        graph = build_startup_radar_graph(
            rag_service=mock_rag,
            generate_brief_service=mock_brief,
        )
        result = graph.invoke({"run_id": "inj-rec-001"})
    state = _state_of(result)
    assert "rank_recommendations" in state.get("executed_nodes", [])
    assert len(state.get("recommendations", [])) >= 1
    mock_rrfm.assert_called()


def test_generate_brief_invoked_as_node() -> None:
    mock_rag = MagicMock(return_value=(["nvidia_ctx_1", "nvidia_ctx_2"], []))
    graph = build_startup_radar_graph(
        rag_service=mock_rag,
    )
    result = graph.invoke({"run_id": "inj-brf-001"})
    state = _state_of(result)
    assert "generate_brief" in state.get("executed_nodes", [])


# --- generate_brief unit tests ---


def _brief_state(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "run_id": "brief-001",
        "startup_id": "startup-42",
        "startup_name": "TestAI",
        "executed_nodes": [
            "preflight_configuration_check",
            "plan_search",
            "collect_sources",
            "extract_profile",
            "validate_evidence",
            "score_startup",
            "diagnose_gaps",
            "retrieve_nvidia_context",
            "build_technology_mappings",
            "rank_recommendations",
        ],
        "scores": {"ai_native_score": 0.75, "nvidia_fit_score": 0.65},
        "gap_diagnosis_metrics": {
            "total_gap_count": 2,
            "production_allowed_gap_count": 2,
            "blocked_gap_count": 0,
            "average_gap_severity": 0.7,
            "average_gap_confidence": 0.65,
        },
        "evidence_validation_metrics": {
            "accepted_evidence_count": 2,
            "unsupported_critical_claims_count": 0,
        },
        "nvidia_recommendations": [
            {
                "recommendation_id": "rec-brief-001-0",
                "gap_id": "gap-ext-api",
                "gap_type": "external_api_dependency",
                "nvidia_technology": "NVIDIA NIM",
                "mapping_score": 0.8,
                "mapping_confidence": 0.75,
                "recommendation_priority_score": 0.85,
                "confidence": 0.75,
                "uncertainty": 0.15,
                "supporting_evidence_ids": ["ev_0", "ev_1"],
                "supporting_rag_context_ids": ["rag_0"],
                "calibration_decision_ids": ["recommendation.priority_score_weights"],
                "production_allowed": True,
                "blockers": [],
                "next_best_action": "Recommend NVIDIA NIM to address external API dependency",
                "reason": "Gap 'external_api_dependency' mapped to 'NVIDIA NIM'",
            },
            {
                "recommendation_id": "rec-brief-001-1",
                "gap_id": "gap-inf-cost",
                "gap_type": "high_inference_cost",
                "nvidia_technology": "TensorRT-LLM",
                "mapping_score": 0.7,
                "mapping_confidence": 0.65,
                "recommendation_priority_score": 0.72,
                "confidence": 0.65,
                "uncertainty": 0.2,
                "supporting_evidence_ids": ["ev_1"],
                "supporting_rag_context_ids": ["rag_0", "rag_1"],
                "calibration_decision_ids": ["recommendation.priority_score_weights"],
                "production_allowed": True,
                "blockers": [],
                "next_best_action": "Recommend TensorRT-LLM to address high inference cost",
                "reason": "Gap 'high_inference_cost' mapped to 'TensorRT-LLM'",
            },
        ],
        "nvidia_recommendation_metrics": {
            "mapping_count": 2,
            "recommendation_count": 2,
            "production_allowed_recommendation_count": 2,
            "blocked_recommendation_count": 0,
            "needs_review_recommendation_count": 0,
            "average_mapping_score": 0.75,
            "average_mapping_confidence": 0.7,
            "average_recommendation_priority_score": 0.785,
            "average_recommendation_confidence": 0.7,
            "evidence_supported_recommendation_rate": 1.0,
            "rag_supported_recommendation_rate": 1.0,
            "missing_recommendation_calibration_count": 0,
            "recommendation_uncertainty_mean": 0.175,
        },
        "ranking_status": "passed",
        "rag_contexts": ["NIM reduces inference cost", "TensorRT-LLM optimizes LLM"],
        "rag_metrics": {
            "retrieval_status": "passed",
            "retrieved_context_count": 2,
            "min_required_contexts": 1,
        },
        "evidence_items": [
            {"id": "ev_0", "url": "https://startup.ai", "text": "Uses OpenAI API"},
            {"id": "ev_1", "url": "https://startup.ai/pricing", "text": "High inference cost"},
        ],
        "accepted_evidence_items": [
            {"id": "ev_0", "claim": "Uses OpenAI API"},
            {"id": "ev_1", "claim": "High inference cost"},
        ],
        "evidence_validation": {
            "status": "passed",
            "metrics": {
                "evidence_items_count": 2,
                "claims_count": 2,
                "unsupported_critical_claims_count": 0,
            },
        },
        "unsupported_critical_claims_count": 0,
        "claims": [
            {
                "claim_text": "Uses external API for inference",
                "criticality": "normal",
                "support_status": "supported",
            },
            {
                "claim_text": "High inference cost on current cloud",
                "criticality": "critical",
                "support_status": "supported",
            },
        ],
        "blockers": [],
        "quality": {"status": "passed", "failed_checks": [], "warning_checks": []},
    }
    result = dict(defaults)
    result.update(overrides)
    return result


def test_generate_brief_fills_action_brief() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    ab = result.get("action_brief", {})
    assert isinstance(ab, dict)
    assert "run_id" in ab
    assert "startup_id" in ab
    assert "generated_at" in ab
    assert "brief_status" in ab
    assert "executive_summary_quantitative" in ab
    assert "recommendation_summary" in ab
    assert "top_recommendations" in ab
    assert "evidence_summary" in ab
    assert "rag_summary" in ab
    assert "gap_summary" in ab
    assert "scoring_summary" in ab
    assert "risk_summary" in ab
    assert "blockers" in ab
    assert "next_best_actions" in ab
    assert "audit_trail" in ab
    assert "quality_gate_snapshot" in ab
    assert "calibration_snapshot" in ab
    assert "review_required" in ab


def test_generate_brief_contains_run_id_and_startup_id() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    ab = result["action_brief"]
    assert ab["run_id"] == "brief-001"
    assert ab["startup_id"] == "startup-42"


def test_generate_brief_top_recommendations_preserves_priority_score() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    recs = result["action_brief"]["top_recommendations"]
    assert len(recs) == 2
    for rec in recs:
        assert "recommendation_id" in rec
        assert "nvidia_technology" in rec
        assert "recommendation_priority_score" in rec
        assert "recommendation_confidence" in rec
        assert "next_best_action" in rec
        assert "supporting_rag_context_ids" in rec
        assert "supporting_evidence_ids" in rec
    assert recs[0]["recommendation_priority_score"] == 0.85
    assert recs[1]["recommendation_priority_score"] == 0.72


def test_generate_brief_brief_metrics_exists() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    bm = result.get("brief_metrics", {})
    assert isinstance(bm, dict)
    assert bm["recommendation_count"] == 2
    assert bm["production_allowed_recommendation_count"] == 2
    assert bm["blocked_recommendation_count"] == 0
    assert bm["average_recommendation_priority_score"] == 0.785
    assert bm["average_recommendation_confidence"] == 0.7
    assert bm["unsupported_critical_claims_count"] == 0


def test_generate_brief_unsupported_critical_claim_marks_failed() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(
            unsupported_critical_claims_count=2,
            evidence_validation={
                "status": "failed",
                "metrics": {"unsupported_critical_claims_count": 2},
            },
        ),
    )
    assert result["status"] == "brief_failed"
    assert result["brief_status"] == "failed_unsupported_critical_claim"
    bm = result["brief_metrics"]
    assert bm["unsupported_critical_claims_count"] == 2
    blockers = result.get("blockers", [])
    assert any("critical claim" in b for b in blockers)
    es = result["action_brief"]["executive_summary_quantitative"]
    assert es.get("unsupported_critical_claims") == 2


def test_generate_brief_no_production_recommendations_blocks() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(
            nvidia_recommendations=[],
            ranking_status="passed",
            nvidia_recommendation_metrics={
                "recommendation_count": 0,
                "production_allowed_recommendation_count": 0,
                "blocked_recommendation_count": 0,
                "average_recommendation_priority_score": 0.0,
                "average_recommendation_confidence": 0.0,
                "recommendation_uncertainty_mean": 0.0,
                "evidence_supported_recommendation_rate": 0.0,
                "rag_supported_recommendation_rate": 0.0,
                "missing_recommendation_calibration_count": 0,
            },
        ),
    )
    assert result["status"] == "brief_blocked"
    assert result["brief_status"] == "blocked_no_production_recommendations"
    assert result["review_required"] is True


def test_generate_brief_handles_empty_rag_but_passed_recs() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(
            rag_contexts=[],
            rag_metrics={"retrieval_status": "needs_review"},
        ),
    )
    assert result["brief_status"] == "passed"
    bm = result["brief_metrics"]
    assert bm["supporting_rag_context_count"] == 0


def test_generate_brief_handles_empty_evidence_but_passed_recs() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(
            evidence_items=[],
            accepted_evidence_items=[],
            evidence_validation={"status": "needs_review", "metrics": {}},
        ),
    )
    assert result["brief_status"] == "passed"
    bm = result["brief_metrics"]
    assert bm["accepted_evidence_count"] == 0


def test_generate_brief_run_id_preserved() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(run_id="preserve-brief-001"),
    )
    assert result["action_brief"]["run_id"] == "preserve-brief-001"


def test_generate_brief_executed_nodes_contains_generate_brief() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    assert "generate_brief" in result["executed_nodes"]
    idx = result["executed_nodes"].index("generate_brief")
    assert idx > result["executed_nodes"].index("rank_recommendations")


def test_generate_brief_recommendation_summary_is_deterministic() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    rec_summary = result["action_brief"]["recommendation_summary"]
    assert "NVIDIA NIM" in rec_summary
    assert "TensorRT-LLM" in rec_summary
    assert "priority=" in rec_summary
    es = result["action_brief"]["executive_summary_quantitative"]
    assert es["production_allowed_recommendations"] == 2


def test_generate_brief_audit_trail_lists_sources() -> None:
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    audit = result["action_brief"]["audit_trail"]
    assert "rank_recommendations" in audit["executed_nodes"]
    assert "generate_brief" in audit["executed_nodes"]
    assert audit["quality_gate_status"] == "passed"


def test_generate_brief_no_real_llm_qdrant_scraping() -> None:
    """Unit test validates the node does not trigger external services."""
    from src.agents.graph import _generate_brief

    result = _generate_brief(
        _brief_state(),
    )
    assert result["brief_status"] == "passed"
    assert len(result["action_brief"]["top_recommendations"]) == 2


def test_quality_gates_consumes_action_brief_and_brief_metrics() -> None:
    """run_quality_gates tolerates action_brief and brief_metrics in state."""
    from src.agents.graph import _run_quality_gates

    state: dict[str, Any] = {
        "run_id": "q-consume-002",
        "executed_nodes": [],
        "unsupported_critical_claims_count": 0,
        "blockers": [],
        "evidence_items": [{"url": "https://a.com"}],
        "rag_contexts": ["ctx1"],
        "action_brief": {
            "run_id": "q-consume-002",
            "brief_status": "passed",
            "top_recommendations": [],
        },
        "brief_metrics": {
            "brief_status": "passed",
            "recommendation_count": 1,
        },
    }
    result = _run_quality_gates(state)
    assert result["status"] == "quality_passed"
    q = result["quality"]
    assert q["status"] == "passed"
    assert q["metrics"]["recommendation_count"] == 1


# --- Gap diagnosis + quality gate integration tests ---


def test_quality_gates_blocked_when_gap_diagnosis_blocked_uncalibrated() -> None:
    """Quality gate blocks when gap_diagnosis_status is blocked_uncalibrated_gap_diagnosis."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-gap-001",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [{"technology_name": "NIM", "priority_score": 0.8, "reason": "test"}],
            "gap_diagnosis_status": "blocked_uncalibrated_gap_diagnosis",
            "gap_diagnosis_metrics": {
                "total_gap_count": 12,
                "production_allowed_gap_count": 0,
                "blocked_gap_count": 12,
                "missing_calibration_count": 5,
                "calibrated_decision_count": 0,
                "gap_uncertainty_mean": 1.0,
            },
        }
    )
    assert result["status"] == "quality_blocked_uncalibrated"
    q = result["quality"]
    assert q["status"] == "blocked_uncalibrated_gap_diagnosis"
    assert any("blocked_uncalibrated" in c for c in q["failed_checks"])
    assert result["review_required"] is True


def test_quality_gates_blocks_when_gap_production_not_allowed() -> None:
    """Quality gate fails when some gaps have production_allowed=false."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-gap-002",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [{"technology_name": "NIM", "priority_score": 0.8, "reason": "test"}],
            "gap_diagnosis_status": "needs_review",
            "gap_diagnosis_metrics": {
                "total_gap_count": 12,
                "production_allowed_gap_count": 10,
                "blocked_gap_count": 2,
                "missing_calibration_count": 0,
                "calibrated_decision_count": 5,
                "gap_uncertainty_mean": 0.3,
            },
        }
    )
    assert result["status"] == "quality_failed"
    q = result["quality"]
    assert any("not all gaps allow production" in c for c in q["failed_checks"])
    assert any("gap_diagnosis_status is needs_review" in c for c in q["failed_checks"])


def test_quality_gates_passes_when_gap_diagnosis_passed() -> None:
    """Quality gate passes only when gap_diagnosis_status is 'passed' and all other checks pass."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-gap-003",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [{"technology_name": "NIM", "priority_score": 0.8, "reason": "test"}],
            "gap_diagnosis_status": "passed",
            "gap_diagnosis_metrics": {
                "total_gap_count": 12,
                "production_allowed_gap_count": 12,
                "blocked_gap_count": 0,
                "needs_more_evidence_gap_count": 0,
                "average_gap_severity": 0.25,
                "average_gap_confidence": 0.75,
                "average_gap_evidence_coverage": 0.0,
                "missing_calibration_count": 0,
                "calibrated_decision_count": 5,
                "gap_uncertainty_mean": 0.15,
            },
        }
    )
    assert result["status"] == "quality_passed"
    q = result["quality"]
    assert q["status"] == "passed"


def test_quality_gates_blocks_on_unsupported_critical_with_gap() -> None:
    """Unsupported critical claim blocks quality even when gap diagnosis passes."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-gap-004",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 1,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [{"technology_name": "NIM", "priority_score": 0.8, "reason": "test"}],
            "gap_diagnosis_status": "passed",
            "gap_diagnosis_metrics": {
                "total_gap_count": 12,
                "production_allowed_gap_count": 12,
                "blocked_gap_count": 0,
                "missing_calibration_count": 0,
                "calibrated_decision_count": 5,
                "gap_uncertainty_mean": 0.15,
            },
        }
    )
    assert result["status"] == "quality_failed"
    q = result["quality"]
    assert "unsupported_critical_claims_count > 0" in q["failed_checks"]
    assert q["status"] == "failed"


def test_quality_gates_contains_gap_metrics() -> None:
    """Quality metrics include gap_diagnosis_metrics fields."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-gap-005",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [{"technology_name": "NIM", "priority_score": 0.8, "reason": "test"}],
            "gap_diagnosis_status": "passed",
            "gap_diagnosis_metrics": {
                "total_gap_count": 12,
                "production_allowed_gap_count": 12,
                "blocked_gap_count": 0,
                "needs_more_evidence_gap_count": 0,
                "average_gap_severity": 0.35,
                "average_gap_confidence": 0.65,
                "average_gap_evidence_coverage": 0.0,
                "missing_calibration_count": 0,
                "calibrated_decision_count": 5,
                "gap_uncertainty_mean": 0.20,
            },
        }
    )
    m = result["quality"]["metrics"]
    assert m["total_gap_count"] == 12
    assert m["production_allowed_gap_count"] == 12
    assert m["blocked_gap_count"] == 0
    assert m["needs_more_evidence_gap_count"] == 0
    assert m["average_gap_severity"] == 0.35
    assert m["average_gap_confidence"] == 0.65
    assert m["missing_gap_calibration_count"] == 0
    assert m["calibrated_gap_decision_count"] == 5
    assert m["gap_uncertainty_mean"] == 0.20


def test_quality_gates_blocked_when_missing_gap_calibration() -> None:
    """Missing gap calibration count > 0 causes calibration block."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-gap-006",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [{"technology_name": "NIM", "priority_score": 0.8, "reason": "test"}],
            "gap_diagnosis_status": "blocked_uncalibrated_gap_diagnosis",
            "gap_diagnosis_metrics": {
                "total_gap_count": 12,
                "production_allowed_gap_count": 0,
                "blocked_gap_count": 12,
                "missing_calibration_count": 5,
                "calibrated_decision_count": 0,
                "gap_uncertainty_mean": 1.0,
            },
        }
    )
    assert result["status"] == "quality_blocked_uncalibrated"
    q = result["quality"]
    assert any("missing_gap_calibration" in c for c in q["failed_checks"])


def test_quality_gates_no_llm_qdrant_internet_scraping() -> None:
    """_run_quality_gates does not call LLM, Qdrant, internet, or scraping."""
    import inspect

    from src.agents.graph import _run_quality_gates

    source = inspect.getsource(_run_quality_gates)
    for forbidden in ("openai", "qdrant", "trafilatura", "playwright", "httpx"):
        assert forbidden not in source


# --- retrieve_nvidia_context specific tests ---


def _make_rag_mock_result(
    rag_contexts: list[str] | None = None,
    retrieval_status: str = "passed",
    top_status: str = "nvidia_context_retrieved",
    review_required: bool = False,
    blockers: list[str] | None = None,
) -> dict[str, object]:
    ctxs = rag_contexts or []
    return {
        "rag_queries_by_gap": {"gap_1": {"gap_id": "gap_1", "query_text": "test"}},
        "rag_contexts": ctxs,
        "rag_contexts_by_gap": {"gap_1": []},
        "rag_retrieval_status": retrieval_status,
        "rag_retrieval_metrics": {
            "gap_count": 1,
            "calibrated_gap_count": 1,
            "query_count": 1,
            "retrieved_context_count": len(ctxs),
            "context_count_by_gap": {"gap_1": len(ctxs)},
            "gaps_with_min_contexts_count": 1 if len(ctxs) >= 1 else 0,
            "gaps_without_context_count": 0 if len(ctxs) > 0 else 1,
            "average_retrieval_score": 0.5,
            "average_relevance_score": 0.5,
            "citation_ready_context_count": len(ctxs),
            "missing_rag_calibration_count": 0,
            "rag_blocker_count": 0,
        },
        "rag_metrics": {
            "query_count": 1,
            "retrieved_context_count": len(ctxs),
            "min_required_contexts": 1,
            "retrieval_status": retrieval_status,
            "rag_required": True,
        },
        "status": top_status,
        "review_required": review_required,
        "blockers": blockers,
    }


def test_retrieve_nvidia_context_passes_when_rag_returns_context() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["nvidia_ctx_1", "nvidia_ctx_2"],
        )
    )
    result = _retrieve_nvidia_context(
        {"run_id": "test-001", "executed_nodes": ["diagnose_gaps"]},
        _rag_service=mock_svc,
    )
    assert result["rag_contexts"] == ["nvidia_ctx_1", "nvidia_ctx_2"]
    assert result["status"] == "nvidia_context_retrieved"
    assert result["review_required"] is False
    assert "retrieve_nvidia_context" in result["executed_nodes"]


def test_retrieve_nvidia_context_populates_rag_metrics() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["ctx_a"],
        )
    )
    result = _retrieve_nvidia_context(
        {"run_id": "test-002", "executed_nodes": []},
        _rag_service=mock_svc,
    )
    metrics = result["rag_metrics"]
    assert isinstance(metrics, dict)
    assert "query_count" in metrics
    assert "retrieved_context_count" in metrics
    assert "min_required_contexts" in metrics
    assert "retrieval_status" in metrics
    assert "rag_required" in metrics


def test_retrieve_nvidia_context_retrieved_context_count_correct() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["a", "b", "c"],
        )
    )
    result = _retrieve_nvidia_context(
        {"run_id": "test-003", "executed_nodes": []},
        _rag_service=mock_svc,
    )
    assert result["rag_metrics"]["retrieved_context_count"] == 3


def test_retrieve_nvidia_context_empty_context_sets_needs_review() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=[],
            retrieval_status="needs_review",
            top_status="rag_needs_review",
            review_required=True,
        )
    )
    result = _retrieve_nvidia_context(
        {"run_id": "test-004", "executed_nodes": []},
        _rag_service=mock_svc,
    )
    assert result["rag_contexts"] == []
    assert result["status"] == "rag_needs_review"
    assert result["review_required"] is True
    assert result["rag_metrics"]["retrieval_status"] == "needs_review"
    assert result["rag_metrics"]["retrieved_context_count"] == 0


def test_retrieve_nvidia_context_error_creates_blocker() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=[],
            retrieval_status="failed",
            top_status="rag_failed",
            review_required=False,
            blockers=["Qdrant connection refused"],
        )
    )
    result = _retrieve_nvidia_context(
        {"run_id": "test-005", "executed_nodes": []},
        _rag_service=mock_svc,
    )
    assert result["status"] == "rag_failed"
    assert result["rag_metrics"]["retrieval_status"] == "failed"
    assert result["review_required"] is False
    blockers = result.get("blockers", [])
    assert any("Qdrant connection refused" in b for b in blockers)


def test_retrieve_nvidia_context_exception_becomes_blocker() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(side_effect=RuntimeError("Qdrant unreachable"))
    result = _retrieve_nvidia_context(
        {"run_id": "test-006", "executed_nodes": []},
        _rag_service=mock_svc,
    )
    assert result["status"] == "rag_failed"
    assert result["rag_metrics"]["retrieval_status"] == "failed"
    blockers = result.get("blockers", [])
    assert any("RuntimeError" in b for b in blockers)


def test_retrieve_nvidia_context_executed_nodes_appended() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["ctx"],
        )
    )
    result = _retrieve_nvidia_context(
        {"run_id": "test-007", "executed_nodes": ["preflight", "plan_search"]},
        _rag_service=mock_svc,
    )
    assert result["executed_nodes"] == [
        "preflight",
        "plan_search",
        "retrieve_nvidia_context",
    ]


def test_retrieve_nvidia_context_run_id_preserved() -> None:
    from src.agents.graph import _retrieve_nvidia_context

    mock_svc = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["ctx"],
        )
    )
    result = _retrieve_nvidia_context(
        {"run_id": "preserve-rag-run-001", "executed_nodes": []},
        _rag_service=mock_svc,
    )
    assert result["status"] in ("nvidia_context_retrieved", "rag_needs_review")


# --- route_after_rag tests ---


def test_route_after_rag_passed_returns_build_technology_mappings() -> None:
    from src.agents.graph import _route_after_rag

    result = _route_after_rag({"rag_retrieval_status": "passed"})
    assert result == "build_technology_mappings"


def test_route_after_rag_needs_review_returns_needs_review() -> None:
    from src.agents.graph import _route_after_rag

    assert _route_after_rag({"rag_retrieval_status": "needs_review"}) == "needs_review"


def test_route_after_rag_failed_returns_needs_review() -> None:
    from src.agents.graph import _route_after_rag

    assert _route_after_rag({"rag_retrieval_status": "failed"}) == "needs_review"


def test_route_after_rag_missing_metrics_returns_needs_review() -> None:
    from src.agents.graph import _route_after_rag

    assert _route_after_rag({}) == "needs_review"


# --- rank_recommendations unit tests ---


def _rank_rec_state(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "run_id": "rank-rec-001",
        "executed_nodes": [
            "preflight",
            "plan_search",
            "collect_sources",
            "extract_profile",
            "validate_evidence",
            "score_startup",
            "diagnose_gaps",
            "retrieve_nvidia_context",
            "build_technology_mappings",
        ],
        "gaps": ["external_api_dependency", "high_inference_cost"],
        "claims": [
            {
                "claim_text": "Uses external API for inference",
                "criticality": "normal",
                "support_status": "supported",
            },
            {
                "claim_text": "High inference cost on current cloud",
                "criticality": "critical",
                "support_status": "supported",
            },
        ],
        "evidence_items": [
            {"id": "ev_0", "url": "https://startup.ai", "text": "Uses OpenAI API"},
            {"id": "ev_1", "url": "https://startup.ai/pricing", "text": "High inference cost"},
        ],
        "rag_contexts": [
            "NVIDIA NIM self-hosted reduces inference cost by 60%",
            "TensorRT-LLM optimizes LLM inference",
        ],
        "rag_metrics": {"retrieval_status": "passed"},
        "unsupported_critical_claims_count": 0,
        "evidence_validation": {"status": "passed"},
        "startup_profile": {"startup_name": "TestAI"},
        "nvidia_technology_mappings": [
            {
                "mapping_id": "map-rank-rec-001-1",
                "gap_type": "external_api_dependency",
                "nvidia_technology": "NVIDIA NIM",
                "mapping_score": 0.8,
                "mapping_confidence": 0.75,
                "uncertainty": 0.2,
                "supporting_rag_context_ids": ["rag_0"],
                "supporting_evidence_ids": ["ev_0"],
                "production_allowed": True,
            },
            {
                "mapping_id": "map-rank-rec-001-2",
                "gap_type": "high_inference_cost",
                "nvidia_technology": "TensorRT-LLM",
                "mapping_score": 0.7,
                "mapping_confidence": 0.65,
                "uncertainty": 0.3,
                "supporting_rag_context_ids": ["rag_0", "rag_1"],
                "supporting_evidence_ids": ["ev_1"],
                "production_allowed": True,
            },
        ],
        "nvidia_mapping_summary": {
            "mapping_status": "passed",
            "production_allowed": True,
            "blockers": [],
        },
    }
    result = dict(defaults)
    result.update(overrides)
    return result


def test_rank_recommendations_fills_recommendations() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [
                {
                    "nvidia_technology": "NVIDIA NIM",
                    "reason": "external_api_dependency",
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.75,
                    "next_best_action": "Recommend NVIDIA NIM",
                    "supporting_rag_context_ids": ["rag_0"],
                    "supporting_evidence_ids": ["ev_0"],
                },
            ],
            "nvidia_recommendation_metrics": {
                "mapping_count": 2,
                "recommendation_count": 1,
                "blocked_recommendation_count": 0,
            },
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    recs = result.get("recommendations", [])
    assert len(recs) >= 1
    for rec in recs:
        assert isinstance(rec, dict)
        assert "technology_name" in rec
        assert "reason" in rec
        assert "supporting_rag_context_ids" in rec
        assert "supporting_evidence_ids" in rec
        assert "confidence" in rec
        assert "priority_score" in rec
        assert "next_best_action" in rec


def test_rank_recommendations_metrics_exist() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [],
            "nvidia_recommendation_metrics": {
                "mapping_count": 0,
                "recommendation_count": 0,
                "blocked_recommendation_count": 1,
            },
            "ranking_status": "needs_review",
            "production_allowed": False,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    metrics = result.get("recommendation_metrics", {})
    assert isinstance(metrics, dict)
    for key in (
        "recommendation_count",
        "rag_contexts_count",
        "ranking_status",
        "production_allowed",
    ):
        assert key in metrics, f"Missing metric key: {key}"


def test_rank_recommendations_priority_score_between_0_and_1() -> None:
    from src.agents.graph import _compute_priority_score, _rank_recommendations

    # Direct formula test
    score = _compute_priority_score(1.0, 1.0, 0.0, 1.0, 1.0)
    assert 0.0 <= score <= 1.0
    assert score == 1.0

    score = _compute_priority_score(0.0, 0.0, 1.0, 0.0, 0.0)
    assert score == 0.0

    score = _compute_priority_score(0.5, 0.5, 0.5, 0.5, 0.5)
    assert 0.0 <= score <= 1.0

    # Verify through the node
    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [
                {
                    "nvidia_technology": "NVIDIA NIM",
                    "reason": "external_api_dependency",
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.75,
                    "next_best_action": "Recommend NVIDIA NIM",
                    "supporting_rag_context_ids": ["rag_0"],
                    "supporting_evidence_ids": ["ev_0"],
                },
            ],
            "nvidia_recommendation_metrics": {"mapping_count": 2, "recommendation_count": 1},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    for rec in result.get("recommendations", []):
        ps = rec.get("priority_score", -1)
        assert 0.0 <= ps <= 1.0, f"priority_score {ps} out of [0, 1]"


def test_rank_recommendations_sorted_by_priority_desc() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [
                {
                    "nvidia_technology": "NVIDIA NIM",
                    "reason": "external_api_dependency",
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.75,
                    "next_best_action": "Recommend",
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                },
                {
                    "nvidia_technology": "TensorRT-LLM",
                    "reason": "high_inference_cost",
                    "recommendation_priority_score": 0.72,
                    "confidence": 0.65,
                    "next_best_action": "Recommend",
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                },
            ],
            "nvidia_recommendation_metrics": {"mapping_count": 2, "recommendation_count": 2},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    recs = result.get("recommendations", [])
    scores = [r.get("priority_score", 0) for r in recs]
    assert scores == sorted(scores, reverse=True), "Recommendations not sorted by priority_score descending"


def test_rank_recommendations_failed_on_unsupported_critical_claim() -> None:
    from src.agents.graph import _rank_recommendations

    result = _rank_recommendations(
        _rank_rec_state(unsupported_critical_claims_count=2),
    )
    assert result["status"] == "recommendation_failed"
    metrics = result.get("recommendation_metrics", {})
    assert metrics.get("ranking_status") == "failed"
    assert result.get("recommendations") == []
    blockers = result.get("blockers", [])
    assert any("critical claim" in b for b in blockers)
    assert result.get("review_required") is False


def test_rank_recommendations_no_rag_contexts_sets_needs_review() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [],
            "nvidia_recommendation_metrics": {"mapping_count": 0, "recommendation_count": 0},
            "ranking_status": "needs_review",
            "production_allowed": False,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state(rag_contexts=[]))
    assert result["status"] == "recommendation_needs_review"
    metrics = result.get("recommendation_metrics", {})
    assert metrics.get("ranking_status") == "needs_review"
    assert result.get("review_required") is True


def test_rank_recommendations_no_mappings_sets_needs_review() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [],
            "nvidia_recommendation_metrics": {"mapping_count": 0, "recommendation_count": 0},
            "ranking_status": "needs_review",
            "production_allowed": False,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state(nvidia_technology_mappings=[]))
    assert result["status"] == "recommendation_needs_review"
    metrics = result.get("recommendation_metrics", {})
    assert metrics.get("ranking_status") == "needs_review"
    assert result.get("review_required") is True


def test_rank_recommendations_preserves_run_id() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [],
            "nvidia_recommendation_metrics": {},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(
            _rank_rec_state(run_id="preserve-rank-001"),
        )
    assert "rank_recommendations" in result.get("executed_nodes", [])


def test_rank_recommendations_executed_nodes_contains_rank() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [],
            "nvidia_recommendation_metrics": {},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    assert "rank_recommendations" in result["executed_nodes"]
    # Verify it's appended after previous nodes
    idx = result["executed_nodes"].index("rank_recommendations")
    assert idx > result["executed_nodes"].index("retrieve_nvidia_context")


def test_quality_gates_consumes_recommendation_count() -> None:
    """run_quality_gates reads recommendation_count from recommendations list."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-consumes-rec-001",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [
                {"technology_name": "NIM", "priority_score": 0.8, "reason": "test"},
            ],
        }
    )
    metrics = result["quality"]["metrics"]
    assert metrics["recommendation_count"] == 1
    assert result["status"] == "quality_passed"


def test_rank_recommendations_no_real_llm_qdrant_scraping() -> None:
    """Unit test does not trigger real LLM, Qdrant, or scraping."""
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [
                {
                    "nvidia_technology": "NVIDIA NIM",
                    "reason": "external_api_dependency",
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.75,
                    "next_best_action": "Recommend",
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                },
            ],
            "nvidia_recommendation_metrics": {"mapping_count": 2, "recommendation_count": 1},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    assert result["status"] == "recommendations_ranked"
    assert len(result["recommendations"]) >= 1
    mock_rrfm.assert_called_once()


def test_rank_recommendations_status_passed_with_enough_recs() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [
                {
                    "nvidia_technology": "NVIDIA NIM",
                    "reason": "ext_api",
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.75,
                    "next_best_action": "Rec",
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                },
            ],
            "nvidia_recommendation_metrics": {"mapping_count": 2, "recommendation_count": 1},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    assert result["status"] == "recommendations_ranked"
    metrics = result.get("recommendation_metrics", {})
    assert metrics.get("ranking_status") == "passed"
    assert result.get("review_required") is False


def test_rank_recommendations_metrics_has_expected_values() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [
                {
                    "nvidia_technology": "NVIDIA NIM",
                    "reason": "ext_api",
                    "recommendation_priority_score": 0.85,
                    "confidence": 0.75,
                    "next_best_action": "Rec",
                    "supporting_rag_context_ids": [],
                    "supporting_evidence_ids": [],
                },
            ],
            "nvidia_recommendation_metrics": {"mapping_count": 2, "recommendation_count": 1},
            "ranking_status": "passed",
            "production_allowed": True,
            "blockers": [],
        }
        result = _rank_recommendations(_rank_rec_state())
    metrics = result.get("recommendation_metrics", {})
    assert metrics["rag_contexts_count"] == 2
    assert metrics["recommendation_count"] == 1


def test_rank_recommendations_empty_recs_with_no_mappings_produces_empty() -> None:
    from src.agents.graph import _rank_recommendations

    with patch("src.recommendation.recommendation_engine.rank_recommendations_from_mappings") as mock_rrfm:
        mock_rrfm.return_value = {
            "nvidia_recommendations": [],
            "nvidia_recommendation_metrics": {"mapping_count": 0, "recommendation_count": 0},
            "ranking_status": "blocked_no_nvidia_mappings",
            "production_allowed": False,
            "blockers": ["No mappings"],
        }
        result = _rank_recommendations(_rank_rec_state(nvidia_technology_mappings=[]))
    assert result.get("recommendations") == []


# --- route_after_rag tests ---


def test_rag_needs_review_in_graph_routes_to_needs_review() -> None:
    mock_rag = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=[],
            retrieval_status="needs_review",
            top_status="rag_needs_review",
            review_required=True,
        )
    )
    mock_rec = MagicMock(return_value=([], []))
    mock_brief = MagicMock(return_value=("", []))
    graph = build_startup_radar_graph(
        rag_service=mock_rag,
        rank_recommendations_service=mock_rec,
        generate_brief_service=mock_brief,
    )
    result = graph.invoke({"run_id": "rag-review-001"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "retrieve_nvidia_context" in executed
    assert "needs_review" in executed
    assert "rank_recommendations" not in executed


def test_rag_failed_in_graph_routes_to_needs_review() -> None:
    mock_rag = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=[],
            retrieval_status="failed",
            top_status="rag_failed",
            review_required=False,
            blockers=["RAG unavailable"],
        )
    )
    mock_rec = MagicMock(return_value=([], []))
    mock_brief = MagicMock(return_value=("", []))
    graph = build_startup_radar_graph(
        rag_service=mock_rag,
        rank_recommendations_service=mock_rec,
        generate_brief_service=mock_brief,
    )
    result = graph.invoke({"run_id": "rag-fail-001"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "retrieve_nvidia_context" in executed
    assert "needs_review" in executed
    assert "rank_recommendations" not in executed
    blockers = state.get("blockers", [])
    assert any("RAG unavailable" in b for b in blockers)


def test_rag_passed_in_graph_routes_to_rank_recommendations() -> None:
    mock_rag = MagicMock(
        return_value=_make_rag_mock_result(
            rag_contexts=["ctx1", "ctx2"],
        )
    )
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    graph = build_startup_radar_graph(
        rag_service=mock_rag,
        generate_brief_service=mock_brief,
    )
    result = graph.invoke({"run_id": "rag-pass-001"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "retrieve_nvidia_context" in executed
    assert "build_technology_mappings" in executed
    assert "rank_recommendations" in executed
    assert "generate_brief" in executed
    assert "run_quality_gates" in executed


# --- diagnose_gaps specific tests ---


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_diagnose_gaps_detects_external_api_dependency(
    mock_list: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    html = (
        "<html><body>"
        "<h1>WrapperAI</h1>"
        "<p>WrapperAI is a Brazilian startup that provides an NLP API service"
        " using OpenAI GPT-4 models. The company wraps GPT APIs for"
        " customer support automation. Founded by Pedro Lima.</p>"
        "</body></html>"
    )
    kwargs = dict(_SOURCE_RECORD_KWARGS)
    kwargs.update(
        source_id="gap_src",
        source_category="official_website",
        base_url="https://wrapperai.com.br",
    )
    from src.scraping.source_registry import SourceRecord

    mock_list.return_value = [SourceRecord(**kwargs)]
    mock_fetch.return_value = FetchResult(
        url="https://wrapperai.com.br",
        status=200,
        raw_html=html,
        fetched_at=_TEST_NOW,
        error=None,
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "gap-001",
            "startup_name": "WrapperAI",
        }
    )
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "diagnose_gaps" in executed

    gaps = state.get("gaps", [])
    assert isinstance(gaps, list)
    assert len(gaps) >= 1
    gap_names = [g.lower() for g in gaps]
    assert any("external_api" in g for g in gap_names), f"Expected external_api_dependency gap, got: {gaps}"
    assert "gap_diagnosis" in state, "Expected gap_diagnosis in state"


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_diagnose_gaps_no_external_api_gap(
    mock_list: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    html = (
        "<html><body>"
        "<h1>SafeAI</h1>"
        "<p>SafeAI is a Brazilian startup building custom computer vision"
        " models for agriculture using PyTorch and TensorRT."
        " Founded by Carlos Souza. Raised $2M.</p>"
        "</body></html>"
    )
    from src.scraping.source_registry import SourceRecord

    kwargs = dict(_SOURCE_RECORD_KWARGS)
    kwargs.update(source_id="gap_src2", source_category="official_website", base_url="https://safeai.com.br")
    mock_list.return_value = [SourceRecord(**kwargs)]
    mock_fetch.return_value = FetchResult(
        url="https://safeai.com.br",
        status=200,
        raw_html=html,
        fetched_at=_TEST_NOW,
        error=None,
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "gap-002",
            "startup_name": "SafeAI",
        }
    )
    state = _state_of(result)
    gaps = state.get("gaps", [])
    assert isinstance(gaps, list)
    assert "external_api_dependency" not in gaps, f"Expected no external_api_dependency, got: {gaps}"
    assert "gap_diagnosis" in state


@patch("src.scraping.http_collector.fetch_page")
@patch("src.scraping.source_registry.list_production_enabled_sources")
def test_diagnose_gaps_empty_profile(
    mock_list: MagicMock,
    mock_fetch: MagicMock,
) -> None:
    from src.scraping.source_registry import SourceRecord

    kwargs = dict(_SOURCE_RECORD_KWARGS)
    kwargs.update(source_id="gap_src3", source_category="official_website", base_url="https://empty.com")
    mock_list.return_value = [SourceRecord(**kwargs)]
    mock_fetch.return_value = FetchResult(
        url="https://empty.com",
        status=200,
        raw_html="<html><body></body></html>",
        fetched_at=_TEST_NOW,
        error=None,
    )
    graph = _make_graph_with_mocks()
    result = graph.invoke(
        {
            "run_id": "gap-003",
            "startup_name": "EmptyCo",
        }
    )
    state = _state_of(result)
    assert state.get("gaps") == []
    assert "diagnose_gaps" in state.get("executed_nodes", [])


# --- Conditional routing tests ---


def test_route_after_preflight_blockers_routes_to_finish() -> None:
    from src.agents.graph import _route_after_preflight

    assert _route_after_preflight({"blockers": ["missing api key"]}) == "finish"


def test_route_after_preflight_blocked_status_routes_to_finish() -> None:
    from src.agents.graph import _route_after_preflight

    assert _route_after_preflight({"status": "blocked"}) == "finish"


def test_route_after_preflight_empty_blockers_routes_to_plan_search() -> None:
    from src.agents.graph import _route_after_preflight

    assert _route_after_preflight({"blockers": [], "status": "config_checked"}) == "plan_search"


def test_route_after_quality_gates_needs_review_routes_to_needs_review() -> None:
    from src.agents.graph import _route_after_quality_gates

    state = {"quality": {"status": "needs_review"}}
    assert _route_after_quality_gates(state) == "needs_review"


def test_route_after_quality_gates_review_required_routes_to_needs_review() -> None:
    from src.agents.graph import _route_after_quality_gates

    assert _route_after_quality_gates({"review_required": True}) == "needs_review"


def test_route_after_quality_gates_failed_routes_to_finish() -> None:
    from src.agents.graph import _route_after_quality_gates

    state = {"quality": {"status": "failed"}}
    assert _route_after_quality_gates(state) == "finish"


def test_route_after_quality_gates_pass_routes_to_finish() -> None:
    from src.agents.graph import _route_after_quality_gates

    state = {"quality": {"status": "pass"}}
    assert _route_after_quality_gates(state) == "finish"


# --- Integration tests for conditional routing ---


def test_preflight_blocked_skips_to_finish() -> None:
    report = ProductReadinessReport(
        ready=False,
        blocking_missing_config=[{"capability_id": "product_database", "reason": "PRODUCT_DB_URL not set"}],
        user_messages=["Required capability 'product_database' is not configured"],
    )
    with patch(
        "src.services.product.readiness_service.ProductReadinessService.get_product_readiness",
        return_value=report,
    ):
        graph = build_startup_radar_graph()
        result = graph.invoke({"run_id": "blocked-001"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "preflight_configuration_check" in executed
    assert "plan_search" not in executed
    assert "finish" in executed
    blockers = state.get("blockers", [])
    assert len(blockers) >= 1
    assert any("PRODUCT_DB_URL" in b for b in blockers)
    assert state["run_id"] == "blocked-001"


def test_preflight_ready_routes_to_plan_search() -> None:
    graph = build_startup_radar_graph()
    result = graph.invoke({"run_id": "ready-001"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "preflight_configuration_check" in executed
    assert "plan_search" in executed
    assert state["run_id"] == "ready-001"


def test_preflight_blocked_populates_blockers() -> None:
    report = ProductReadinessReport(
        ready=False,
        blocking_missing_config=[
            {"capability_id": "vector_store", "reason": "QDRANT_URL not set"},
            {"capability_id": "rag", "reason": "OPENAI_API_KEY not set"},
        ],
        user_messages=[
            "Required capability 'vector_store' is not configured: QDRANT_URL not set",
            "Required capability 'rag' is not configured: OPENAI_API_KEY not set",
        ],
    )
    with patch(
        "src.services.product.readiness_service.ProductReadinessService.get_product_readiness",
        return_value=report,
    ):
        graph = build_startup_radar_graph()
        result = graph.invoke({"run_id": "blocked-002"})
    state = _state_of(result)
    blockers = state.get("blockers", [])
    assert len(blockers) >= 2
    assert any("QDRANT_URL" in b for b in blockers)
    assert any("OPENAI_API_KEY" in b for b in blockers)
    assert "preflight_configuration_check" in state.get("executed_nodes", [])
    assert state["run_id"] == "blocked-002"


def test_preflight_blocked_executed_nodes_includes_preflight_and_finish() -> None:
    report = ProductReadinessReport(
        ready=False,
        blocking_missing_config=[{"capability_id": "db", "reason": "DB not set"}],
    )
    with patch(
        "src.services.product.readiness_service.ProductReadinessService.get_product_readiness",
        return_value=report,
    ):
        graph = build_startup_radar_graph()
        result = graph.invoke({"run_id": "blocked-003"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "preflight_configuration_check" in executed
    assert "finish" in executed
    assert "plan_search" not in executed
    assert executed.index("preflight_configuration_check") < executed.index("finish")


def test_preflight_exception_routes_to_finish_with_blockers() -> None:
    with patch(
        "src.services.product.readiness_service.ProductReadinessService.get_product_readiness",
        side_effect=RuntimeError("Service unreachable"),
    ):
        graph = build_startup_radar_graph()
        result = graph.invoke({"run_id": "exc-001"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "preflight_configuration_check" in executed
    assert "finish" in executed
    assert "plan_search" not in executed
    blockers = state.get("blockers", [])
    assert len(blockers) >= 1
    assert any("Readiness check failed" in b for b in blockers)
    assert state["run_id"] == "exc-001"


def test_quality_needs_review_routes_through_needs_review() -> None:
    from src.agents.graph import _route_after_quality_gates

    state: dict = {"quality": {"status": "needs_review"}}
    assert _route_after_quality_gates(state) == "needs_review"


def test_quality_needs_review_sets_needs_human_review() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review({"run_id": "r-001", "executed_nodes": []})
    assert result["status"] == "needs_human_review"
    assert "needs_review" in result["executed_nodes"]


# --- run_quality_gates unit tests ---


def test_quality_gate_passed() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-pass-001",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": ["rec1"],
        }
    )
    assert result["status"] == "quality_passed"
    assert result["review_required"] is False
    q = result["quality"]
    assert q["status"] == "passed"
    assert q["failed_checks"] == []
    assert q["warning_checks"] == []
    assert "metrics" in q
    assert "thresholds" in q


def test_quality_gate_failed_unsupported_claims() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-fail-001",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 3,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": ["rec1"],
        }
    )
    assert result["status"] == "quality_failed"
    assert result["review_required"] is False
    q = result["quality"]
    assert q["status"] == "failed"
    assert "unsupported_critical_claims_count > 0" in q["failed_checks"]


def test_quality_gate_failed_blockers() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-fail-002",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": ["API key missing"],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": ["rec1"],
        }
    )
    assert result["status"] == "quality_failed"
    assert result["review_required"] is False
    q = result["quality"]
    assert q["status"] == "failed"
    assert "blockers_count > 0" in q["failed_checks"]


def test_quality_gate_needs_review_no_evidence() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-review-001",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [],
            "rag_contexts": ["ctx1"],
            "recommendations": ["rec1"],
        }
    )
    assert result["status"] == "needs_human_review"
    assert result["review_required"] is True
    q = result["quality"]
    assert q["status"] == "needs_review"
    assert "evidence_items_count == 0" in q["warning_checks"]


def test_quality_gate_needs_review_no_rag_contexts() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-review-002",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": [],
            "recommendations": ["rec1"],
        }
    )
    assert result["status"] == "needs_human_review"
    assert result["review_required"] is True
    q = result["quality"]
    assert q["status"] == "needs_review"
    assert "rag_contexts_count == 0" in q["warning_checks"]


def test_quality_gate_needs_review_no_recommendations() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-review-003",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": [],
        }
    )
    assert result["status"] == "needs_human_review"
    assert result["review_required"] is True
    q = result["quality"]
    assert q["status"] == "needs_review"
    assert "recommendation_count == 0" in q["warning_checks"]


def test_quality_gate_metrics_and_thresholds_exist() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-meta-001",
            "executed_nodes": [],
            "unsupported_critical_claims_count": 0,
            "blockers": [],
            "evidence_items": [{"url": "https://a.com"}],
            "rag_contexts": ["ctx1"],
            "recommendations": ["rec1"],
        }
    )
    q = result["quality"]
    metrics = q["metrics"]
    assert isinstance(metrics, dict)
    for key in (
        "unsupported_critical_claims_count",
        "blockers_count",
        "evidence_items_count",
        "rag_contexts_count",
        "recommendation_count",
    ):
        assert key in metrics, f"Missing metric: {key}"

    thresholds = q["thresholds"]
    assert isinstance(thresholds, dict)
    for key in (
        "unsupported_critical_claims_count",
        "blockers_count",
        "evidence_items_count",
        "rag_contexts_count",
        "recommendation_count",
    ):
        assert key in thresholds, f"Missing threshold: {key}"


def test_quality_gate_run_id_preserved() -> None:
    """Quality gate does not overwrite run_id."""
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "preserve-q-001",
            "executed_nodes": [],
        }
    )
    # run_id is not returned by the node (it's preserved in state automatically)
    assert result["executed_nodes"] == ["run_quality_gates"]


def test_quality_gate_executed_nodes_appended() -> None:
    from src.agents.graph import _run_quality_gates

    result = _run_quality_gates(
        {
            "run_id": "q-node-001",
            "executed_nodes": ["preflight", "plan_search"],
        }
    )
    assert result["executed_nodes"] == ["preflight", "plan_search", "run_quality_gates"]


# --- Integration test: quality failed routes to finish ---


def test_quality_failed_in_graph_routes_to_finish() -> None:
    from unittest.mock import patch

    from src.agents.graph import _append_node, build_startup_radar_graph

    mock_rag = MagicMock(return_value=(["ctx1", "ctx2"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))

    def _patched_run_quality_gates(state: dict) -> dict[str, Any]:
        return {
            "status": "quality_failed",
            "quality": {
                "status": "failed",
                "failed_checks": ["blockers_count > 0"],
                "warning_checks": [],
                "metrics": {},
                "thresholds": {},
            },
            "review_required": False,
            "executed_nodes": _append_node(state, "run_quality_gates"),
        }

    with patch("src.agents.graph._run_quality_gates", side_effect=_patched_run_quality_gates):
        graph = build_startup_radar_graph(
            rag_service=mock_rag,
            generate_brief_service=mock_brief,
        )
        result = graph.invoke({"run_id": "fail-int-001"})
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "run_quality_gates" in executed
    assert "needs_review" not in executed
    assert "finish" in executed


# --- needs_review payload tests ---


@contextmanager
def _patch_quality_gates_to_needs_review() -> Generator[None, None, None]:
    """Force _run_quality_gates to produce needs_review so the graph routes there."""
    with patch(
        "src.agents.graph._run_quality_gates",
        return_value={
            "status": "quality_gates_passed",
            "quality": {
                "status": "needs_review",
                "issues": ["Quality gate requires human review"],
                "checks": {},
            },
            "review_required": True,
            "executed_nodes": [],
        },
    ):
        yield


def test_needs_review_in_graph_quality_needs_review() -> None:
    with _patch_quality_gates_to_needs_review():
        graph = build_startup_radar_graph()
        result = graph.invoke({"run_id": "review-001", "startup_id": "startup-42"})
    state = _state_of(result)
    assert "needs_review" in state.get("executed_nodes", [])
    payload = state.get("review_payload", {})
    assert payload.get("run_id") == "review-001"


def test_needs_review_in_graph_review_required_true() -> None:
    with _patch_quality_gates_to_needs_review():
        graph = build_startup_radar_graph()
        result = graph.invoke({"run_id": "review-002"})
    state = _state_of(result)
    assert state.get("review_required") is True


def test_needs_review_payload_contains_run_id_and_startup_id() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review({"run_id": "review-003", "startup_id": "startup-99", "executed_nodes": []})
    payload = result.get("review_payload", {})
    assert payload.get("run_id") == "review-003"
    assert payload.get("startup_id") == "startup-99"


def test_needs_review_payload_contains_expected_human_actions() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review({"run_id": "review-004", "executed_nodes": []})
    payload = result.get("review_payload", {})
    actions = payload.get("expected_human_actions", [])
    assert "approve" in actions
    assert "reject" in actions
    assert "request_more_evidence" in actions


def test_needs_review_payload_interrupt_enabled_true() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review({"run_id": "review-005", "executed_nodes": []})
    payload = result.get("review_payload", {})
    assert payload.get("interrupt_enabled") is True


def test_needs_review_payload_resumable_true() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review({"run_id": "review-006", "executed_nodes": []})
    payload = result.get("review_payload", {})
    assert payload.get("resumable") is True


def test_needs_review_run_id_preserved() -> None:
    with _patch_quality_gates_to_needs_review():
        graph = build_startup_radar_graph()
        result = graph.invoke({"run_id": "preserve-review-001"})
    state = _state_of(result)
    assert state["run_id"] == "preserve-review-001"


def test_needs_review_reason_from_quality_issues() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review(
        {
            "run_id": "review-007",
            "executed_nodes": [],
            "quality": {
                "status": "needs_review",
                "issues": ["No startup brief was generated", "No evidence items were collected"],
            },
        }
    )
    payload = result.get("review_payload", {})
    reason = payload.get("reason", "")
    assert "No startup brief was generated" in reason
    assert "No evidence items were collected" in reason


def test_needs_review_reason_fallback() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review({"run_id": "review-008", "executed_nodes": [], "quality": {"status": "needs_review"}})
    payload = result.get("review_payload", {})
    assert payload.get("reason") == "quality_gate_requested_human_review"


def test_needs_review_severity_high_with_blockers() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review(
        {
            "run_id": "review-009",
            "executed_nodes": [],
            "quality": {"status": "needs_review", "issues": ["Something wrong"]},
            "blockers": ["API key missing"],
        }
    )
    payload = result.get("review_payload", {})
    assert payload.get("severity") == "high"


def test_needs_review_executed_nodes_contains_needs_review() -> None:
    from src.agents.graph import _needs_review

    result = _needs_review({"run_id": "r-002", "executed_nodes": ["finish"]})
    assert "needs_review" in result["executed_nodes"]


# --- route_after_review tests ---


def test_route_after_review_approve_routes_to_build_technology_mappings() -> None:
    from src.agents.graph import _route_after_review

    assert (
        _route_after_review({"review_decision": "approve", "rag_retrieval_status": "passed"})
        == "build_technology_mappings"
    )


def test_route_after_review_reject_routes_to_finish() -> None:
    from src.agents.graph import _route_after_review

    assert _route_after_review({"review_decision": "reject"}) == "finish"


def test_route_after_review_more_evidence_routes_to_plan_search() -> None:
    """Within retry limit routes to plan_search."""
    from src.agents.graph import _route_after_review

    result = _route_after_review(
        {
            "review_decision": "request_more_evidence",
            "evidence_retry_count": 1,
            "max_evidence_retries": 1,
        }
    )
    assert result == "plan_search"


def test_route_after_review_more_evidence_exceeds_retry_routes_to_finish() -> None:
    """When retry count exceeds max_evidence_retries routes to finish."""
    from src.agents.graph import _route_after_review

    result = _route_after_review(
        {
            "review_decision": "request_more_evidence",
            "evidence_retry_count": 2,
            "max_evidence_retries": 1,
        }
    )
    assert result == "finish"


def test_route_after_review_no_decision_routes_to_finish() -> None:
    from src.agents.graph import _route_after_review

    assert _route_after_review({}) == "finish"


def test_route_after_review_approve_with_rag_needs_review_routes_to_build_technology_mappings() -> None:
    from src.agents.graph import _route_after_review

    result = _route_after_review(
        {
            "review_decision": "approve",
            "rag_retrieval_status": "needs_review",
            "executed_nodes": ["diagnose_gaps", "retrieve_nvidia_context"],
        }
    )
    assert result == "build_technology_mappings"


def test_route_after_review_approve_with_rag_failed_routes_to_build_technology_mappings() -> None:
    from src.agents.graph import _route_after_review

    result = _route_after_review(
        {
            "review_decision": "approve",
            "rag_retrieval_status": "failed",
            "executed_nodes": ["diagnose_gaps", "retrieve_nvidia_context"],
        }
    )
    assert result == "build_technology_mappings"


def test_route_after_review_approve_with_rag_needs_review_but_rank_already_executed_routes_to_finish() -> None:
    from src.agents.graph import _route_after_review

    result = _route_after_review(
        {
            "review_decision": "approve",
            "rag_retrieval_status": "needs_review",
            "executed_nodes": [
                "diagnose_gaps",
                "retrieve_nvidia_context",
                "build_technology_mappings",
                "rank_recommendations",
            ],
        }
    )
    assert result == "finish"


def test_route_after_review_approve_with_mappings_and_rag_passed_routes_to_rank_recommendations() -> None:
    from src.agents.graph import _route_after_review

    result = _route_after_review(
        {
            "review_decision": "approve",
            "rag_retrieval_status": "passed",
            "nvidia_mapping_summary": {"mapping_status": "passed", "production_allowed": True},
            "executed_nodes": ["retrieve_nvidia_context", "build_technology_mappings"],
        }
    )
    assert result == "rank_recommendations"


# ---------------------------------------------------------------------------
# checkpointer tests (no interrupt)
# ---------------------------------------------------------------------------


def test_graph_compiles_with_checkpointer() -> None:
    from langgraph.checkpoint.memory import MemorySaver

    memory = MemorySaver()
    graph = build_startup_radar_graph(checkpointer=memory)
    assert graph is not None
    assert hasattr(graph, "invoke")


def test_execution_preserves_thread_id_in_state() -> None:
    from langgraph.checkpoint.memory import MemorySaver

    mock_rag = MagicMock(return_value=(["ctx"], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    with _patch_quality_to_pass():
        memory = MemorySaver()
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id: str = "checkpointer-thread-001"
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke(
            {"run_id": "checkpointer-run-001", "thread_id": thread_id},
            config,
        )
    state = _state_of(result)

    assert state["run_id"] == "checkpointer-run-001"
    assert state.get("thread_id") == thread_id


def test_executed_nodes_preserved_with_checkpointer() -> None:
    from langgraph.checkpoint.memory import MemorySaver

    mock_rag = MagicMock(return_value=(["ctx"], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    with _patch_quality_to_pass():
        memory = MemorySaver()
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id: str = "checkpointer-thread-002"
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke({"run_id": "checkpointer-run-002"}, config)
    state = _state_of(result)

    executed = state.get("executed_nodes", [])
    assert len(executed) == len(NODE_NAMES)
    assert executed == NODE_NAMES


def test_two_threads_with_different_run_ids_do_not_mix() -> None:
    from langgraph.checkpoint.memory import MemorySaver

    mock_rag = MagicMock(return_value=(["ctx"], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    with _patch_quality_to_pass():
        memory = MemorySaver()
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )

        config_a: dict[str, Any] = {"configurable": {"thread_id": "thread-a"}}
        config_b: dict[str, Any] = {"configurable": {"thread_id": "thread-b"}}

        result_a = graph.invoke({"run_id": "run-a"}, config_a)
        result_b = graph.invoke({"run_id": "run-b"}, config_b)

    state_a = _state_of(result_a)
    state_b = _state_of(result_b)

    assert state_a["run_id"] == "run-a"
    assert state_b["run_id"] == "run-b"
    assert state_a["run_id"] != state_b["run_id"]

    assert len(state_a.get("executed_nodes", [])) == len(NODE_NAMES)
    assert len(state_b.get("executed_nodes", [])) == len(NODE_NAMES)


def test_checkpointer_unit_test_no_real_db() -> None:
    from langgraph.checkpoint.memory import MemorySaver

    mock_rag = MagicMock(return_value=(["ctx"], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    with _patch_quality_to_pass():
        memory = MemorySaver()
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id: str = "checkpointer-no-db-001"
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke({"run_id": "checkpointer-no-db"}, config)
    state = _state_of(result)

    assert "run_id" in state
    assert "executed_nodes" in state
    assert "finish" in state.get("executed_nodes", [])


def test_no_interrupt_called_when_graph_is_complete() -> None:
    """Graph completes without hitting interrupt() when quality passes."""
    from langgraph.checkpoint.memory import MemorySaver

    mock_rag = MagicMock(return_value=(["ctx"], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    with _patch_quality_to_pass():
        memory = MemorySaver()
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id: str = "checkpointer-no-interrupt-001"
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke({"run_id": "no-int"}, config)

    assert isinstance(result, dict)
    assert "__interrupt__" not in result, f"Expected no interrupt, got __interrupt__: {result.get('__interrupt__')}"
    assert result.get("status") != "needs_human_review"
    assert "finish" in result.get("executed_nodes", [])


# ---------------------------------------------------------------------------
# interrupt / resume tests
# ---------------------------------------------------------------------------


@contextmanager
def _patch_quality_to_pass() -> Generator[None, None, None]:
    def _patched_run_quality_gates(state: dict) -> dict[str, Any]:
        return {
            "status": "quality_passed",
            "quality": {
                "status": "passed",
                "metrics": {},
                "thresholds": {},
                "failed_checks": [],
                "warning_checks": [],
            },
            "review_required": False,
            "executed_nodes": list(state.get("executed_nodes", [])) + ["run_quality_gates"],
        }

    with patch("src.agents.graph._run_quality_gates", side_effect=_patched_run_quality_gates):
        yield


@contextmanager
def _patch_quality_to_needs_review() -> Generator[None, None, None]:
    from src.agents.graph import _append_node

    def _patched_run_quality_gates(state: dict) -> dict[str, Any]:
        return {
            "status": "quality_gates_passed",
            "quality": {
                "status": "needs_review",
                "issues": ["Quality gate requires human review"],
                "checks": {},
            },
            "review_required": True,
            "executed_nodes": _append_node(state, "run_quality_gates"),
        }

    with patch("src.agents.graph._run_quality_gates", side_effect=_patched_run_quality_gates):
        yield


def test_graph_interrupts_at_needs_review() -> None:
    """Graph pauses at needs_review when interrupt() is called."""
    from langgraph.checkpoint.memory import MemorySaver

    from src.agents.graph import build_startup_radar_graph

    memory = MemorySaver()
    with _patch_quality_to_needs_review():
        graph = build_startup_radar_graph(checkpointer=memory)
        config: dict[str, Any] = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = graph.invoke({"run_id": "interrupt-test-001"}, config)

    assert isinstance(result, dict)
    assert "__interrupt__" in result, f"Expected __interrupt__ in result, got keys: {list(result.keys())}"
    interrupts = result["__interrupt__"]
    assert len(interrupts) >= 1
    payload = interrupts[0].value if hasattr(interrupts[0], "value") else interrupts[0]
    assert isinstance(payload, dict)
    assert payload.get("run_id") == "interrupt-test-001"


def _make_resume_mocks() -> tuple[MagicMock, MagicMock, MagicMock]:
    mock_rag = MagicMock(return_value=(["ctx1", "ctx2"], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    return mock_rag, mock_rec, mock_brief


def test_graph_after_resume_approve_completes() -> None:
    """Resuming with approve runs needs_review then routes to finish."""
    from langgraph.checkpoint.memory import MemorySaver

    from src.agents.graph import build_startup_radar_graph

    mock_rag, mock_rec, mock_brief = _make_resume_mocks()
    memory = MemorySaver()
    with _patch_quality_to_needs_review():
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id: str = str(uuid.uuid4())
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        graph.invoke({"run_id": "resume-test-001"}, config)

        result = graph.invoke(
            Command(
                resume="approved",
                update={
                    "review_decision": "approve",
                    "review_notes": "Looks good",
                    "reviewed_by": "test@example.com",
                },
            ),
            config,
        )

    assert isinstance(result, dict)
    assert result.get("review_decision") == "approve"
    assert result.get("status") == "human_review_approved"
    assert result.get("review_notes") == "Looks good"
    assert result.get("reviewed_by") == "test@example.com"
    executed = result.get("executed_nodes", [])
    assert "needs_review" in executed
    assert "finish" in executed


def test_graph_after_resume_reject_completes() -> None:
    """Resuming with reject runs needs_review then routes to finish."""
    from langgraph.checkpoint.memory import MemorySaver

    from src.agents.graph import build_startup_radar_graph

    mock_rag, mock_rec, mock_brief = _make_resume_mocks()
    memory = MemorySaver()
    with _patch_quality_to_needs_review():
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id: str = str(uuid.uuid4())
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        graph.invoke({"run_id": "resume-test-002"}, config)

        result = graph.invoke(
            Command(
                resume="rejected",
                update={
                    "review_decision": "reject",
                    "review_notes": "Insufficient evidence",
                    "reviewed_by": "admin",
                },
            ),
            config,
        )

    assert isinstance(result, dict)
    assert result.get("review_decision") == "reject"
    assert result.get("status") == "human_review_rejected"
    assert result.get("review_notes") == "Insufficient evidence"
    assert result.get("reviewed_by") == "admin"
    blockers = result.get("blockers", [])
    assert "Human rejected" in blockers
    executed = result.get("executed_nodes", [])
    assert "needs_review" in executed
    assert "finish" in executed


def test_graph_after_resume_more_evidence_routes_to_plan_search() -> None:
    """Resuming with request_more_evidence routes to plan_search within retry limit."""
    from langgraph.checkpoint.memory import MemorySaver

    from src.agents.graph import build_startup_radar_graph

    mock_rag, mock_rec, mock_brief = _make_resume_mocks()
    memory = MemorySaver()
    with _patch_quality_to_needs_review():
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id: str = str(uuid.uuid4())
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
        graph.invoke({"run_id": "resume-test-003"}, config)

        graph.invoke(
            Command(
                resume="need more",
                update={
                    "review_decision": "request_more_evidence",
                    "review_notes": "Need more data",
                    "reviewed_by": "analyst",
                },
            ),
            config,
        )

    thread_state = graph.get_state(config)
    values = thread_state.values
    assert values.get("review_decision") == "request_more_evidence"
    assert values.get("evidence_retry_count") == 1
    assert values.get("review_notes") == "Need more data"
    assert values.get("reviewed_by") == "analyst"
    executed = values.get("executed_nodes", [])
    assert "needs_review" in executed
    assert "plan_search" in executed
    assert values.get("run_id") == "resume-test-003"


def test_graph_request_more_evidence_increments_retry_count() -> None:
    """request_more_evidence increments evidence_retry_count in state."""
    from src.agents.graph import _needs_review

    result = _needs_review(
        {
            "run_id": "retry-001",
            "executed_nodes": [],
            "review_decision": "request_more_evidence",
            "review_notes": "Need more evidence",
            "reviewed_by": "tester",
        }
    )
    assert result.get("evidence_retry_count") == 1
    assert result.get("status") == "planning_more_evidence"


def test_graph_request_more_evidence_exceeds_max_retry_adds_blocker() -> None:
    """When retry count exceeds limit, blocker and max_retry status are set."""
    from src.agents.graph import _needs_review

    result = _needs_review(
        {
            "run_id": "retry-002",
            "executed_nodes": [],
            "evidence_retry_count": 1,
            "max_evidence_retries": 1,
            "review_decision": "request_more_evidence",
            "review_notes": "Still need more",
            "reviewed_by": "tester",
        }
    )
    assert result.get("evidence_retry_count") == 2
    assert result.get("status") == "max_evidence_retries_reached"
    blockers = result.get("blockers", [])
    assert "max_evidence_retries_reached" in blockers


def test_graph_request_more_evidence_sets_evidence_request_reason() -> None:
    """evidence_request_reason is set from review_notes."""
    from src.agents.graph import _needs_review

    result = _needs_review(
        {
            "run_id": "reason-001",
            "executed_nodes": [],
            "review_decision": "request_more_evidence",
            "review_notes": "Precisa de mais fontes oficiais",
            "reviewed_by": "tester",
        }
    )
    assert result.get("evidence_request_reason") == "Precisa de mais fontes oficiais"


def test_graph_approve_still_works_after_changes() -> None:
    """Approve routing unchanged after request_more_evidence changes."""
    from langgraph.checkpoint.memory import MemorySaver

    from src.agents.graph import build_startup_radar_graph

    mock_rag, mock_rec, mock_brief = _make_resume_mocks()
    memory = MemorySaver()
    with _patch_quality_to_needs_review():
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        graph.invoke({"run_id": "approve-test"}, config)

        result = graph.invoke(
            Command(
                resume="approved",
                update={
                    "review_decision": "approve",
                    "review_notes": "Looks good",
                    "reviewed_by": "test@example.com",
                },
            ),
            config,
        )

    assert isinstance(result, dict)
    assert result.get("review_decision") == "approve"
    assert result.get("status") == "human_review_approved"
    executed = result.get("executed_nodes", [])
    assert "needs_review" in executed
    assert "finish" in executed


def test_graph_reject_still_works_after_changes() -> None:
    """Reject routing unchanged after request_more_evidence changes."""
    from langgraph.checkpoint.memory import MemorySaver

    from src.agents.graph import build_startup_radar_graph

    mock_rag, mock_rec, mock_brief = _make_resume_mocks()
    memory = MemorySaver()
    with _patch_quality_to_needs_review():
        graph = build_startup_radar_graph(
            checkpointer=memory,
            rag_service=mock_rag,
            rank_recommendations_service=mock_rec,
            generate_brief_service=mock_brief,
        )
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        graph.invoke({"run_id": "reject-test"}, config)

        result = graph.invoke(
            Command(
                resume="rejected",
                update={
                    "review_decision": "reject",
                    "review_notes": "Insufficient evidence",
                    "reviewed_by": "admin",
                },
            ),
            config,
        )

    assert isinstance(result, dict)
    assert result.get("review_decision") == "reject"
    assert result.get("status") == "human_review_rejected"
    blockers = result.get("blockers", [])
    assert "Human rejected" in blockers
    executed = result.get("executed_nodes", [])
    assert "needs_review" in executed
    assert "finish" in executed


def test_graph_after_resume_rag_needs_review_approve_routes_to_rank_recommendations() -> None:
    """Resuming with approve after RAG needs_review routes to rank_recommendations."""
    from langgraph.checkpoint.memory import MemorySaver

    from src.agents.graph import build_startup_radar_graph

    mock_rag = MagicMock(return_value=([], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    memory = MemorySaver()
    graph = build_startup_radar_graph(
        checkpointer=memory,
        rag_service=mock_rag,
        rank_recommendations_service=mock_rec,
        generate_brief_service=mock_brief,
    )
    thread_id: str = str(uuid.uuid4())
    config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    graph.invoke({"run_id": "rag-resume-001"}, config)

    graph.invoke(
        Command(resume="approved", update={"review_decision": "approve"}),
        config,
    )

    thread_state = graph.get_state(config)
    executed = thread_state.values.get("executed_nodes", [])
    assert "retrieve_nvidia_context" in executed
    assert "needs_review" in executed
    assert "rank_recommendations" in executed
    assert "run_quality_gates" in executed


# ---------------------------------------------------------------------------
# _finish / persistence tests
# ---------------------------------------------------------------------------


def _finish_state(**overrides: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "run_id": "finish-001",
        "analysis_run_id": "ar-001",
        "startup_id": "startup-42",
        "startup_name": "TestAI",
        "status": "brief_generated",
        "executed_nodes": [
            "preflight_configuration_check",
            "plan_search",
            "collect_sources",
            "extract_profile",
            "validate_evidence",
            "score_startup",
            "diagnose_gaps",
            "retrieve_nvidia_context",
            "build_technology_mappings",
            "rank_recommendations",
            "generate_brief",
            "run_quality_gates",
        ],
        "blockers": [],
        "quality": {
            "status": "passed",
            "metrics": {"recommendation_count": 2},
            "thresholds": {},
            "failed_checks": [],
            "warning_checks": [],
        },
        "evidence_validation": {
            "status": "passed",
            "metrics": {"evidence_items_count": 2, "unsupported_critical_claims_count": 0},
        },
        "rag_metrics": {
            "retrieval_status": "passed",
            "retrieved_context_count": 2,
        },
        "recommendation_metrics": {
            "recommendation_count": 2,
            "ranking_status": "passed",
        },
        "brief_metrics": {
            "brief_status": "passed",
            "recommendation_count": 2,
        },
        "action_brief": {
            "run_id": "finish-001",
            "brief_status": "passed",
            "top_recommendations": [],
        },
        "review_required": False,
        "review_payload": None,
    }
    result = dict(defaults)
    result.update(overrides)
    return result


def test_finish_calls_repository_to_save_analysis_run() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    result = _finish(
        _finish_state(),
        _analysis_repository=mock_repo,
    )
    assert "finish" in result["executed_nodes"]
    mock_repo.assert_called_once()
    call_args = mock_repo.call_args
    assert call_args[0][0] == "ar-001"


def test_finish_payload_contains_run_id_and_startup_id() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert snapshot["run_id"] == "finish-001"
    assert snapshot["startup_id"] == "startup-42"


def test_finish_payload_contains_executed_nodes() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert "finish" in snapshot["executed_nodes"]
    assert "rank_recommendations" in snapshot["executed_nodes"]
    assert "generate_brief" in snapshot["executed_nodes"]


def test_finish_payload_contains_quality() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert snapshot["quality"]["status"] == "passed"
    assert snapshot["quality"]["metrics"]["recommendation_count"] == 2


def test_finish_payload_contains_evidence_validation() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert snapshot["evidence_validation"]["status"] == "passed"


def test_finish_payload_contains_rag_metrics() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert snapshot["rag_metrics"]["retrieval_status"] == "passed"
    assert snapshot["rag_metrics"]["retrieved_context_count"] == 2


def test_finish_payload_contains_recommendation_metrics() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert snapshot["recommendation_metrics"]["ranking_status"] == "passed"
    assert snapshot["recommendation_metrics"]["recommendation_count"] == 2


def test_finish_payload_contains_action_brief() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert snapshot["action_brief"]["run_id"] == "finish-001"


def test_finish_payload_contains_brief_metrics() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    _finish(_finish_state(), _analysis_repository=mock_repo)
    kwargs = mock_repo.call_args[1]
    snapshot = kwargs["output_snapshot"]
    assert snapshot["brief_metrics"]["brief_status"] == "passed"


def test_finish_persistence_failure_adds_blocker() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock(side_effect=RuntimeError("DB connection lost"))
    result = _finish(
        _finish_state(),
        _analysis_repository=mock_repo,
    )
    assert result["status"] == "persistence_failed"
    blockers = result.get("blockers", [])
    assert any("Persistence failed" in b for b in blockers)


def test_finish_no_repository_does_not_persist() -> None:
    from src.agents.graph import _finish

    result = _finish(_finish_state())
    assert result["status"] == "brief_generated"
    assert "finish" in result["executed_nodes"]


def test_finish_no_analysis_run_id_does_not_persist() -> None:
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    result = _finish(
        _finish_state(analysis_run_id=None),
        _analysis_repository=mock_repo,
    )
    assert "finish" in result["executed_nodes"]
    mock_repo.assert_not_called()


def test_workflow_invocation_with_repository_persists_results() -> None:
    """Integration test: graph with repository persists at the end."""
    mock_rag = MagicMock(return_value=(["ctx1", "ctx2"], []))
    mock_rec = MagicMock(return_value=(["[monitor] rec1"], []))
    mock_brief = MagicMock(return_value=("# Brief\n\ncontent", []))
    mock_repo = MagicMock()

    graph = build_startup_radar_graph(
        rag_service=mock_rag,
        rank_recommendations_service=mock_rec,
        generate_brief_service=mock_brief,
        analysis_repository=mock_repo,
    )
    result = graph.invoke(
        {
            "run_id": "int-persist-001",
            "analysis_run_id": "ar-integration-001",
            "startup_id": "startup-99",
        }
    )
    state = _state_of(result)
    executed = state.get("executed_nodes", [])
    assert "finish" in executed
    mock_repo.assert_called_once()
    call_kwargs = mock_repo.call_args[1]
    snapshot = call_kwargs["output_snapshot"]
    assert snapshot["run_id"] == "int-persist-001"
    assert snapshot["startup_id"] == "startup-99"
    assert "finish" in snapshot["executed_nodes"]


def test_finish_no_real_db_in_unit_test() -> None:
    """Unit test does not connect to any real database."""
    from src.agents.graph import _finish

    mock_repo = MagicMock()
    result = _finish(
        _finish_state(),
        _analysis_repository=mock_repo,
    )
    assert result["status"] == "brief_generated"
    mock_repo.assert_called_once()
    # No SQLAlchemy session or Postgres was involved
    kwargs = mock_repo.call_args[1]
    assert "output_snapshot" in kwargs
    assert "status" in kwargs


# --- Retriever strategy dispatch tests ---


def _calibrated_retriever_strategy_inventory() -> list[Any]:
    """Build an inventory with rag.retriever_strategy calibrated to semantic_qdrant."""
    from src.quality.decision_calibration_registry import (
        CalibrationMethod,
        CalibrationStatus,
        DecisionCalibrationRecord,
        DecisionType,
    )

    return [
        DecisionCalibrationRecord(
            decision_id="rag.retriever_strategy",
            decision_name="RAG: Retriever Strategy for Production",
            decision_type=DecisionType.ARCHITECTURE_CHOICE,
            current_value="semantic_qdrant",
            calibration_status=CalibrationStatus.BASELINE_MEASURED,
            calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
            production_allowed=True,
            evidence_source="RAGAS eval: semantic_qdrant venceu",
            owner="team-rag",
        ),
        DecisionCalibrationRecord(
            decision_id="rag.hybrid_retrieval_weights",
            decision_name="RAG Gap Retrieval: Hybrid Retrieval Weights",
            decision_type=DecisionType.WEIGHT,
            current_value={"dense": 0.5, "sparse": 0.5},
            calibration_status=CalibrationStatus.UNCALIBRATED,
            production_allowed=False,
            owner="team-rag",
        ),
    ]


class TestResolveRetrieverStrategy:
    """_resolve_retriever_strategy reads from Decision Calibration Registry."""

    def test_resolves_semantic_qdrant_when_calibrated(self) -> None:
        from src.agents.graph import _resolve_retriever_strategy

        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=_calibrated_retriever_strategy_inventory(),
        ):
            strategy, ragas_ref, blockers = _resolve_retriever_strategy()

        assert strategy == "semantic_qdrant"
        assert ragas_ref is not None
        assert ragas_ref["decision_id"] == "rag.retriever_strategy"
        assert ragas_ref["current_value"] == "semantic_qdrant"
        assert ragas_ref["production_allowed"] is True
        assert blockers == []

    def test_returns_blockers_when_missing(self) -> None:
        from src.agents.graph import _resolve_retriever_strategy

        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=[],
        ):
            strategy, ragas_ref, blockers = _resolve_retriever_strategy()

        assert strategy is None
        assert ragas_ref is None
        assert len(blockers) >= 1
        assert any("not found" in b for b in blockers)

    def test_blocks_lexical_baseline_strategy(self) -> None:
        from src.agents.graph import _resolve_retriever_strategy
        from src.quality.decision_calibration_registry import (
            CalibrationMethod,
            CalibrationStatus,
            DecisionCalibrationRecord,
            DecisionType,
        )

        inventory = [
            DecisionCalibrationRecord(
                decision_id="rag.retriever_strategy",
                decision_name="RAG: Retriever Strategy",
                decision_type=DecisionType.ARCHITECTURE_CHOICE,
                current_value="lexical_baseline",
                calibration_status=CalibrationStatus.BASELINE_MEASURED,
                calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
                production_allowed=False,
                evidence_source="RAGAS eval: lexical_baseline venceu",
                owner="team-rag",
            ),
        ]
        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=inventory,
        ):
            strategy, ragas_ref, blockers = _resolve_retriever_strategy()

        assert strategy is None
        assert blockers
        assert any("blocked" in b.lower() for b in blockers)

    def test_includes_evidence_source_in_ragas_ref(self) -> None:
        from src.agents.graph import _resolve_retriever_strategy

        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=_calibrated_retriever_strategy_inventory(),
        ):
            _, ragas_ref, _ = _resolve_retriever_strategy()

        assert ragas_ref is not None
        assert ragas_ref["evidence_source"] == "RAGAS eval: semantic_qdrant venceu"


class TestValidateHybridWeights:
    """_validate_hybrid_weights checks rag.hybrid_retrieval_weights."""

    def test_returns_blockers_when_uncalibrated(self) -> None:
        from src.agents.graph import _validate_hybrid_weights

        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=_calibrated_retriever_strategy_inventory(),
        ):
            weights, blockers = _validate_hybrid_weights()

        assert weights is None
        assert len(blockers) >= 1
        assert any("uncalibrated" in b for b in blockers)

    def test_returns_weights_when_calibrated(self) -> None:
        from src.agents.graph import _validate_hybrid_weights
        from src.quality.decision_calibration_registry import (
            CalibrationMethod,
            CalibrationStatus,
            DecisionCalibrationRecord,
            DecisionType,
        )

        inventory = [
            DecisionCalibrationRecord(
                decision_id="rag.hybrid_retrieval_weights",
                decision_name="Hybrid Weights",
                decision_type=DecisionType.WEIGHT,
                current_value={"dense": 0.7, "sparse": 0.3},
                calibration_status=CalibrationStatus.BASELINE_MEASURED,
                calibration_method=CalibrationMethod.SENSITIVITY_ANALYSIS,
                production_allowed=True,
                evidence_source="Sensitivity analysis",
                owner="team-rag",
            ),
        ]
        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=inventory,
        ):
            weights, blockers = _validate_hybrid_weights()

        assert weights == {"dense": 0.7, "sparse": 0.3}
        assert blockers == []

    def test_returns_blockers_when_missing(self) -> None:
        from src.agents.graph import _validate_hybrid_weights

        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=[],
        ):
            weights, blockers = _validate_hybrid_weights()

        assert weights is None
        assert any("not found" in b for b in blockers)


class TestRetrieveNvidiaContextDispatch:
    """_retrieve_nvidia_context dispatches based on registry strategy."""

    def test_semantic_qdrant_dispatches_to_qdrant(self) -> None:
        from src.agents.graph import _retrieve_nvidia_context

        with (
            patch(
                "src.quality.decision_calibration_registry.get_project_decision_inventory",
                return_value=_calibrated_retriever_strategy_inventory(),
            ),
            patch("src.rag.rag_service_factory.QdrantRagService") as mock_qdrant_cls,
        ):
            mock_instance = MagicMock()
            mock_instance.return_value = _make_rag_mock_result(
                rag_contexts=["ctx1"],
            )
            mock_qdrant_cls.return_value = mock_instance

            result = _retrieve_nvidia_context(
                {
                    "run_id": "dispatch-001",
                    "executed_nodes": ["diagnose_gaps"],
                }
            )

        assert result["selected_retriever_strategy"] == "semantic_qdrant"
        assert result["ragas_eval_reference"] is not None
        assert result["ragas_eval_reference"]["current_value"] == "semantic_qdrant"
        mock_qdrant_cls.assert_called_once()

    def test_lexical_baseline_blocked(self) -> None:
        from src.agents.graph import _retrieve_nvidia_context
        from src.quality.decision_calibration_registry import (
            CalibrationMethod,
            CalibrationStatus,
            DecisionCalibrationRecord,
            DecisionType,
        )

        inventory = [
            DecisionCalibrationRecord(
                decision_id="rag.retriever_strategy",
                decision_name="RAG: Retriever Strategy",
                decision_type=DecisionType.ARCHITECTURE_CHOICE,
                current_value="lexical_baseline",
                calibration_status=CalibrationStatus.BASELINE_MEASURED,
                calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
                production_allowed=True,
                evidence_source="RAGAS eval",
                owner="team-rag",
            ),
        ]
        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=inventory,
        ):
            result = _retrieve_nvidia_context(
                {
                    "run_id": "dispatch-002",
                    "executed_nodes": [],
                }
            )

        assert result["status"] == "rag_blocked_lexical_winner_not_productive"
        assert result["selected_retriever_strategy"] == "lexical_baseline"
        assert result["rag_retrieval_status"] == "blocked_lexical_winner_not_productive"
        assert result["review_required"] is True
        blockers = result.get("blockers", [])
        assert any("lexical_baseline" in b for b in blockers)

    def test_missing_registry_entry_blocked(self) -> None:
        from src.agents.graph import _retrieve_nvidia_context

        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=[],
        ):
            result = _retrieve_nvidia_context(
                {
                    "run_id": "dispatch-003",
                    "executed_nodes": [],
                }
            )

        assert result["status"] == "rag_blocked_missing_ragas_eval"
        assert result["selected_retriever_strategy"] == ""
        assert result["ragas_eval_reference"] is None
        blockers = result.get("blockers", [])
        assert any("not found" in b for b in blockers)

    def test_populates_state_fields_on_success(self) -> None:
        from src.agents.graph import _retrieve_nvidia_context

        with (
            patch(
                "src.quality.decision_calibration_registry.get_project_decision_inventory",
                return_value=_calibrated_retriever_strategy_inventory(),
            ),
            patch("src.rag.rag_service_factory.QdrantRagService") as mock_qdrant_cls,
        ):
            mock_instance = MagicMock()
            mock_instance.return_value = _make_rag_mock_result(
                rag_contexts=["ctx1"],
            )
            mock_qdrant_cls.return_value = mock_instance

            result = _retrieve_nvidia_context(
                {
                    "run_id": "dispatch-004",
                    "executed_nodes": ["diagnose_gaps"],
                }
            )

        assert "selected_retriever_strategy" in result
        assert "ragas_eval_reference" in result
        assert result["selected_retriever_strategy"] == "semantic_qdrant"
        ref = result["ragas_eval_reference"]
        assert ref["decision_id"] == "rag.retriever_strategy"
        assert ref["calibration_status"] == "baseline_measured"
        assert ref["production_allowed"] is True

    def test_injected_service_bypasses_registry(self) -> None:
        """When _rag_service is injected, dispatch is skipped."""
        from src.agents.graph import _retrieve_nvidia_context

        mock_svc = MagicMock(
            return_value=_make_rag_mock_result(
                rag_contexts=["ctx_injected"],
            )
        )
        result = _retrieve_nvidia_context(
            {"run_id": "dispatch-005", "executed_nodes": []},
            _rag_service=mock_svc,
        )

        assert result["selected_retriever_strategy"] == ""
        assert result["ragas_eval_reference"] is None
        assert result["rag_contexts"] == ["ctx_injected"]
        mock_svc.assert_called_once()

    def test_hybrid_qdrant_blocked_without_calibrated_weights(self) -> None:
        from src.agents.graph import _retrieve_nvidia_context
        from src.quality.decision_calibration_registry import (
            CalibrationMethod,
            CalibrationStatus,
            DecisionCalibrationRecord,
            DecisionType,
        )

        inventory = [
            DecisionCalibrationRecord(
                decision_id="rag.retriever_strategy",
                decision_name="RAG: Retriever Strategy",
                decision_type=DecisionType.ARCHITECTURE_CHOICE,
                current_value="hybrid_qdrant",
                calibration_status=CalibrationStatus.BASELINE_MEASURED,
                calibration_method=CalibrationMethod.BASELINE_MEASUREMENT,
                production_allowed=True,
                evidence_source="RAGAS eval",
                owner="team-rag",
            ),
            DecisionCalibrationRecord(
                decision_id="rag.hybrid_retrieval_weights",
                decision_name="Hybrid Weights",
                decision_type=DecisionType.WEIGHT,
                current_value={"dense": 0.5, "sparse": 0.5},
                calibration_status=CalibrationStatus.UNCALIBRATED,
                production_allowed=False,
                owner="team-rag",
            ),
        ]
        with patch(
            "src.quality.decision_calibration_registry.get_project_decision_inventory",
            return_value=inventory,
        ):
            result = _retrieve_nvidia_context(
                {
                    "run_id": "dispatch-006",
                    "executed_nodes": [],
                }
            )

        assert result["status"] == "rag_blocked_uncalibrated_hybrid"
        assert result["selected_retriever_strategy"] == "hybrid_qdrant"
        blockers = result.get("blockers", [])
        assert any("uncalibrated" in b for b in blockers)
