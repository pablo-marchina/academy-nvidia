from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.database.session import configure_product_database, reset_product_database_runtime


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("APP_MODE", "product")
    monkeypatch.setenv("ENABLE_PRODUCT_PERSISTENCE", "true")
    monkeypatch.setenv("QDRANT_URL", "")
    configure_product_database(f"sqlite:///{(tmp_path / 'workflow_api.db').as_posix()}")
    with TestClient(app) as test_client:
        yield test_client
    reset_product_database_runtime()


@pytest.fixture
def startup_id(client: TestClient) -> str:
    resp = client.post(
        "/startups",
        json={
            "name": "Workflow Startup",
            "website": "https://workflow.example.com",
            "sector": "AI",
            "description": "Workflow test startup",
            "product_summary": "AI product testing",
            "tags": ["ai-native", "testing"],
            "evidence": [
                {
                    "claim": "Uses AI in production",
                    "source_url": "https://workflow.example.com/tech",
                    "source_type": "official_site",
                    "quote_or_evidence": "Uses AI inference in production.",
                    "confidence": "high",
                }
            ],
        },
    )
    assert resp.status_code == 201, f"Create startup failed: {resp.text}"
    return resp.json()["id"]


def test_create_product_workflow_run(client: TestClient, startup_id: str) -> None:
    resp = client.post(
        "/workflows/product-runs",
        json={
            "startup_id": startup_id,
        },
    )
    assert resp.status_code == 201, f"Create workflow failed: {resp.text}"
    data = resp.json()
    assert data["id"] is not None
    assert data["startup_id"] == startup_id
    assert data["status"] in ("queued", "running", "completed", "degraded", "failed")


def test_create_product_workflow_run_without_startup(client: TestClient) -> None:
    resp = client.post(
        "/workflows/product-runs",
        json={
            "startup_id": "nonexistent",
        },
    )
    assert resp.status_code == 201, f"Create workflow failed: {resp.text}"
    assert resp.json()["startup_id"] == "nonexistent"


def test_get_product_workflow_run(client: TestClient, startup_id: str) -> None:
    create_resp = client.post("/workflows/product-runs", json={"startup_id": startup_id})
    assert create_resp.status_code == 201
    run_id = create_resp.json()["id"]

    resp = client.get(f"/workflows/product-runs/{run_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == run_id
    assert data["startup_id"] == startup_id


def test_get_product_workflow_run_not_found(client: TestClient) -> None:
    resp = client.get("/workflows/product-runs/nonexistent")
    assert resp.status_code == 404


def test_list_product_workflow_runs(client: TestClient, startup_id: str) -> None:
    client.post("/workflows/product-runs", json={"startup_id": startup_id})
    client.post("/workflows/product-runs", json={"startup_id": startup_id})

    resp = client.get("/workflows/product-runs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


def test_list_product_workflow_runs_filter_by_status(client: TestClient, startup_id: str) -> None:
    client.post("/workflows/product-runs", json={"startup_id": startup_id})

    resp = client.get("/workflows/product-runs?status=queued")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 0


def test_get_workflow_nodes(client: TestClient, startup_id: str) -> None:
    create_resp = client.post("/workflows/product-runs", json={"startup_id": startup_id})
    assert create_resp.status_code == 201
    run_id = create_resp.json()["id"]

    resp = client.get(f"/workflows/product-runs/{run_id}/nodes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_get_workflow_nodes_not_found(client: TestClient) -> None:
    resp = client.get("/workflows/product-runs/nonexistent/nodes")
    assert resp.status_code == 404


def test_analysis_run_workflow_link(client: TestClient, startup_id: str) -> None:
    resp = client.post(
        "/workflows/product-runs", json={"startup_id": startup_id, "analysis_run_id": "ar-1"}
    )
    assert resp.status_code == 201

    resp = client.get("/analysis-runs/ar-1/workflow")
    assert resp.status_code == 200
    data = resp.json()
    assert data["analysis_run_id"] == "ar-1"


def test_analysis_run_workflow_link_not_found(client: TestClient) -> None:
    resp = client.get("/analysis-runs/nonexistent/workflow")
    assert resp.status_code == 404


def test_langgraph_status_endpoint(client: TestClient) -> None:
    resp = client.get("/workflows/langgraph-status")
    assert resp.status_code == 200
    data = resp.json()
    assert "langgraph_available" in data
    assert isinstance(data["langgraph_available"], bool)


def test_workflow_run_created_at_populated(client: TestClient, startup_id: str) -> None:
    resp = client.post("/workflows/product-runs", json={"startup_id": startup_id})
    assert resp.status_code == 201
    data = resp.json()
    assert data["created_at"] is not None
