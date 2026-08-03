#!/usr/bin/env python3
"""Run live validation against the persisted workflow state.

The canonical validator intentionally remains unchanged. This wrapper makes the
POST response observable by replacing only its JSON view with the subsequent
GET /workflows/product-runs/{id} representation, then enriches the artifact with
mapping-level provenance and blockers from PostgreSQL.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

import validate_live_outputs as base


class _PersistedResponseProxy:
    def __init__(self, created_response: Any, persisted_response: Any) -> None:
        self.status_code = created_response.status_code
        self.headers = persisted_response.headers
        self.text = persisted_response.text
        self._persisted_response = persisted_response

    def json(self) -> Any:
        return self._persisted_response.json()


class _PersistedWorkflowClient:
    def __init__(self, client: TestClient) -> None:
        self._client = client

    def post(self, path: str, *args: Any, **kwargs: Any) -> Any:
        response = self._client.post(path, *args, **kwargs)
        if path != "/workflows/product-runs" or response.status_code != 201:
            return response
        workflow_id = response.json().get("id")
        if not workflow_id:
            return response
        persisted = self._client.get(f"/workflows/product-runs/{workflow_id}")
        if persisted.status_code != 200:
            return response
        return _PersistedResponseProxy(response, persisted)

    def get(self, path: str, *args: Any, **kwargs: Any) -> Any:
        return self._client.get(path, *args, **kwargs)


_BASE_RUN_CASE = base._run_case


def _run_case_with_persisted_state(client: TestClient, case: dict[str, Any]) -> dict[str, Any]:
    return _BASE_RUN_CASE(_PersistedWorkflowClient(client), case)


def _mapping_diagnostics(mapping_output: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "mapping_id": mapping.get("mapping_id"),
            "gap_type": mapping.get("gap_type"),
            "nvidia_technology": mapping.get("nvidia_technology"),
            "mapping_score": mapping.get("mapping_score"),
            "mapping_confidence": mapping.get("mapping_confidence"),
            "production_allowed": mapping.get("production_allowed"),
            "supporting_rag_context_ids": mapping.get("supporting_rag_context_ids", []),
            "supporting_evidence_ids": mapping.get("supporting_evidence_ids", []),
            "blockers": mapping.get("blockers", []),
        }
        for mapping in mapping_output.get("nvidia_technology_mappings", [])
        if isinstance(mapping, dict)
    ]


def _enrich_report() -> int:
    report_path = Path(base.REPORT_PATH)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    database_url = os.environ.get(
        "PRODUCT_DB_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/startup_radar",
    )
    base.configure_product_database(database_url, create_schema=False)
    try:
        with TestClient(base.app) as client:
            for company in report.get("companies", []):
                workflow_id = company.get("workflow_id")
                if not workflow_id:
                    continue
                response = client.get(f"/workflows/product-runs/{workflow_id}")
                if response.status_code != 200:
                    company["persisted_state_fetch_status"] = response.status_code
                    continue
                workflow = response.json()
                state = workflow.get("state") or {}
                node_outputs = state.get("node_outputs") or {}
                mapping_output = node_outputs.get("mapping_output") or {}
                rag_output = node_outputs.get("rag_output") or {}
                gap_output = node_outputs.get("gap_output") or {}
                company["persisted_state_fetch_status"] = 200
                company["persisted_current_node"] = workflow.get("current_node")
                company["mapping_status"] = mapping_output.get("mapping_status")
                company["mapping_metrics"] = mapping_output.get("nvidia_mapping_metrics", {})
                company["mapping_diagnostics"] = _mapping_diagnostics(mapping_output)
                company["rag_retrieval_status"] = rag_output.get(
                    "rag_retrieval_status",
                    company.get("rag_retrieval_status", "missing"),
                )
                company["rag_metrics"] = rag_output.get(
                    "rag_retrieval_metrics",
                    company.get("rag_metrics", {}),
                )
                company["gap_diagnosis_status"] = gap_output.get(
                    "gap_diagnosis_status",
                    company.get("gap_diagnosis_status"),
                )
                company["gap_metrics"] = gap_output.get("metrics", company.get("gap_metrics", {}))
    finally:
        base.reset_product_database_runtime()

    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    return base._validation_exit_code(report.get("companies", []))


def main() -> int:
    base._run_case = _run_case_with_persisted_state
    base.main()
    return _enrich_report()


if __name__ == "__main__":
    raise SystemExit(main())
