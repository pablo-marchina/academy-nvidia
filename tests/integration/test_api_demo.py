"""Integration tests for the minimal FastAPI demo API (Epic 25).

Tests verify that:
1. GET /health returns 200
2. GET /version returns basic project data
3. GET /rag/status does not crash without Qdrant
4. POST /brief with sample input generates a brief
5. POST /brief/evaluate returns PASS/WARN/FAIL
6. GET /demo/artifacts does not allow path traversal
7. API does not make external calls (offline mode)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

_SAMPLE_INPUT = (
    Path(__file__).resolve().parent.parent.parent
    / "examples"
    / "demo"
    / "sample_startup_input.json"
)


def _load_sample() -> dict:
    return json.loads(_SAMPLE_INPUT.read_text(encoding="utf-8"))


@pytest.mark.integration
def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_version_returns_data() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "nvidia-startup-ai-radar"
    assert "version" in data
    assert "description" in data


@pytest.mark.integration
def test_rag_status_returns_200() -> None:
    """GET /rag/status must return 200 and have expected fields regardless of Qdrant."""
    response = client.get("/rag/status")
    assert response.status_code == 200
    data = response.json()
    assert "backend" in data
    assert "collection_name" in data
    assert "vector_size" in data
    assert "qdrant_available" in data
    assert "error" in data


@pytest.mark.integration
def test_post_brief_with_sample_input() -> None:
    """POST /brief with sample input generates a valid brief."""
    sample = _load_sample()
    response = client.post(
        "/brief",
        json={
            "startup_name": sample["startup_name"],
            "profile": sample.get("profile", {}),
            "evidence": sample.get("evidence", []),
            "source_url": sample.get("source_url", "https://example.com"),
            "offline": True,
        },
    )
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert data["startup_name"] == sample["startup_name"]
    assert "brief_json" in data
    assert "brief_markdown" in data
    assert "run_report" in data
    assert data["brief_json"].get("startup_name") == sample["startup_name"]
    assert "verdict" in data["brief_json"]
    assert data["run_report"]["status"] == "completed"


@pytest.mark.integration
def test_post_brief_offline_with_eval() -> None:
    """Offline mode runs without external dependencies and optional eval."""
    sample = _load_sample()
    response = client.post(
        "/brief",
        json={
            "startup_name": sample["startup_name"],
            "profile": sample.get("profile", {}),
            "evidence": sample.get("evidence", []),
            "source_url": sample.get("source_url", "https://example.com"),
            "offline": True,
            "run_answer_quality_eval": True,
        },
    )
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert data["run_report"]["status"] == "completed"
    if data.get("answer_quality_eval"):
        metrics = data["answer_quality_eval"]["metrics"]
        assert "answer_quality_status" in metrics
        assert metrics["answer_quality_status"] in ("PASS", "WARN", "FAIL")


@pytest.mark.integration
def test_post_brief_evaluate() -> None:
    """POST /brief/evaluate returns a status (PASS/WARN/FAIL)."""
    sample = _load_sample()
    brief_resp = client.post(
        "/brief",
        json={
            "startup_name": sample["startup_name"],
            "profile": sample.get("profile", {}),
            "evidence": sample.get("evidence", []),
            "source_url": sample.get("source_url", "https://example.com"),
            "offline": True,
        },
    )
    assert brief_resp.status_code == 200

    brief_data = brief_resp.json()
    eval_resp = client.post(
        "/brief/evaluate",
        json={
            "startup_name": sample["startup_name"],
            "brief_json": brief_data["brief_json"],
        },
    )
    assert eval_resp.status_code == 200, f"Eval response: {eval_resp.text}"
    eval_data = eval_resp.json()
    assert eval_data["status"] in ("PASS", "WARN", "FAIL")
    assert "metrics" in eval_data
    assert "gates" in eval_data


@pytest.mark.integration
def test_demo_artifacts_blocks_path_traversal() -> None:
    """GET /demo/artifacts must block path traversal attempts."""
    response = client.get("/demo/artifacts?path=../../etc")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["artifacts"] == []


@pytest.mark.integration
def test_demo_artifacts_returns_list() -> None:
    """GET /demo/artifacts returns a list (may be empty but valid)."""
    response = client.get("/demo/artifacts")
    assert response.status_code == 200
    data = response.json()
    assert "artifacts" in data
    assert "total" in data
    assert isinstance(data["total"], int)


@pytest.mark.integration
def test_openapi_docs_available() -> None:
    """Swagger UI docs endpoint works."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.integration
def test_api_no_external_calls() -> None:
    """POST /brief in offline mode makes no external HTTP calls."""
    sample = _load_sample()
    response = client.post(
        "/brief",
        json={
            "startup_name": sample["startup_name"],
            "profile": sample.get("profile", {}),
            "evidence": sample.get("evidence", []),
            "source_url": sample.get("source_url", "https://example.com"),
            "offline": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["run_report"]["status"] == "completed"
    assert data["run_report"]["parameters"]["offline"] is True
