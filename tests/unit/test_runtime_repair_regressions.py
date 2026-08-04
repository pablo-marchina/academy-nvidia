from __future__ import annotations

from datetime import UTC, datetime


def test_network_retry_returns_fetch_result(monkeypatch):
    import src.scraping.http_collector as module
    from src.scraping.fetcher import FetchResult

    def fake_fetch(url, **kwargs):
        return FetchResult(
            url=url,
            status=None,
            raw_html="",
            fetched_at=datetime.now(UTC),
            error="simulated network failure",
        )

    monkeypatch.setattr(module, "fetch_page", fake_fetch)
    result = module.HttpSourceCollector._fetch_with_tenacity(
        url="https://example.invalid",
        timeout_s=1,
        max_retries=1,
        backoff_base=0.01,
        cached_etag=None,
        cached_last_modified=None,
    )
    assert isinstance(result, FetchResult)
    assert result.error == "simulated network failure"


def test_gap_feature_extractors_define_matching_items():
    from src.diagnosis.gap_diagnosis_scoring import (
        extract_gap_confidence_features,
        extract_gap_severity_features,
    )
    from src.diagnosis.schemas import GapType

    gap = GapType.COMPUTE_ACCELERATION_GAP
    severity = extract_gap_severity_features(gap, [], [], [], [], {}, {})
    confidence = extract_gap_confidence_features(gap, [], [], [], {}, {})
    assert severity.relevant_signal_absence == 1.0
    assert confidence.supporting_evidence_count == 0.0


def test_needs_more_evidence_produces_auditable_negative_recommendation():
    from src.orchestration.node_impl import _runtime_decision_inventory
    from src.recommendation.recommendation_engine import rank_recommendations_from_mappings

    result = rank_recommendations_from_mappings(
        run_id="run-test",
        mapping_status="needs_more_evidence",
        inventory=_runtime_decision_inventory(),
        nvidia_technology_mappings=[
            {
                "mapping_id": "map-test-1",
                "gap_type": "compute_acceleration_gap",
                "nvidia_technology": "CUDA",
                "mapping_score": 0.1,
                "mapping_confidence": 0.1,
                "uncertainty": 0.9,
                "supporting_rag_context_ids": [],
                "supporting_evidence_ids": [],
                "calibration_decision_ids": [],
                "production_allowed": False,
                "blockers": ["Insufficient evidence"],
            }
        ],
    )
    assert result["ranking_status"] == "needs_review"
    assert len(result["nvidia_recommendations"]) == 1
    recommendation = result["nvidia_recommendations"][0]
    assert recommendation["production_allowed"] is False
    assert recommendation["recommendation_action"] == "not_recommended"
    assert recommendation["why_not"]


def test_runtime_nodes_allow_declared_degradation():
    import src.orchestration.node_impl  # noqa: F401
    from src.orchestration.nodes import WORKFLOW_NODES

    nodes = {node.name: node for node in WORKFLOW_NODES}
    assert nodes["collect_sources"].critical is False
    assert nodes["map_nvidia_technologies"].critical is False


def test_proxy_timeout_matches_verifier_timeout():
    from pathlib import Path

    config = Path("frontend/nginx.conf").read_text(encoding="utf-8")
    assert "proxy_read_timeout 1800s;" in config
    assert "proxy_send_timeout 1800s;" in config
