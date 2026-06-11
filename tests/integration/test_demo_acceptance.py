"""Demo acceptance tests for API + generated brief outputs (Epic 27).

These tests intentionally exercise the local/offline demo path. They do not
require Qdrant, do not call an LLM, and do not change scoring, diagnosis,
recommendation, RAG retrieval, or Action Brief logic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SAMPLE_INPUT = _PROJECT_ROOT / "examples" / "demo" / "sample_startup_input.json"


def _load_sample() -> dict[str, Any]:
    return json.loads(_SAMPLE_INPUT.read_text(encoding="utf-8"))


def _brief_payload(sample: dict[str, Any]) -> dict[str, Any]:
    return {
        "startup_name": sample["startup_name"],
        "profile": sample.get("profile", {}),
        "evidence": sample.get("evidence", []),
        "source_url": sample.get("source_url", "https://example.com"),
        "offline": True,
        "use_rag": False,
        "run_answer_quality_eval": False,
    }


@pytest.mark.integration
def test_demo_health_endpoint_is_available() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_demo_rag_status_is_resilient_without_qdrant() -> None:
    response = client.get("/rag/status")

    assert response.status_code == 200
    data = response.json()
    assert data["collection_name"]
    assert data["vector_size"] == 384
    assert isinstance(data["qdrant_available"], bool)
    assert "error" in data


@pytest.mark.integration
def test_demo_brief_acceptance_output_contract() -> None:
    sample = _load_sample()

    response = client.post("/brief", json=_brief_payload(sample))

    assert response.status_code == 200, response.text
    data = response.json()
    brief_json = data["brief_json"]
    run_report = data["run_report"]

    assert data["startup_name"] == sample["startup_name"]
    assert isinstance(brief_json, dict)
    assert isinstance(data["brief_markdown"], str)
    assert data["brief_markdown"].startswith("# Startup Action Brief:")
    assert isinstance(run_report, dict)
    assert run_report["status"] == "completed"
    assert isinstance(data["warnings"], list)

    assert brief_json["startup_name"] == sample["startup_name"]
    assert brief_json["recommended_motion"]
    assert 0 <= brief_json["final_priority_score"] <= 100
    assert brief_json["defensibility_score"]
    assert brief_json["inception_fit_score"]
    assert brief_json["production_readiness_score"]
    assert brief_json["composite_score"]
    assert len(brief_json["diagnosed_gaps"]) > 0
    assert len(brief_json["nvidia_technology_candidates"]) > 0
    assert len(brief_json["evidence_used"]) > 0
    assert "missing_evidence" in brief_json
    assert "uncertainties" in brief_json


@pytest.mark.integration
def test_demo_brief_evaluate_returns_acceptance_status() -> None:
    sample = _load_sample()
    brief_response = client.post("/brief", json=_brief_payload(sample))
    assert brief_response.status_code == 200, brief_response.text

    evaluate_response = client.post(
        "/brief/evaluate",
        json={
            "startup_name": sample["startup_name"],
            "brief_json": brief_response.json()["brief_json"],
        },
    )

    assert evaluate_response.status_code == 200, evaluate_response.text
    data = evaluate_response.json()
    assert data["status"] in {"PASS", "WARN", "FAIL"}
    assert isinstance(data["metrics"], dict)
    assert isinstance(data["gates"], list)
    assert isinstance(data["warnings"], list)


@pytest.mark.integration
def test_demo_artifacts_reject_path_traversal() -> None:
    response = client.get("/demo/artifacts", params={"path": "../../etc"})

    assert response.status_code == 200
    data = response.json()
    assert data == {"artifacts": [], "total": 0}
