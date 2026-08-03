from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:200]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_all(path: Path, old: str, new: str, expected: int) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"Expected {expected} matches in {path}, found {count}: {old[:200]}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def patch_api_schema() -> None:
    path = ROOT / "src/api/product_schemas.py"
    replace_once(
        path,
        '''class ProductWorkflowNodeRunRead(BaseModel):\n    id: str\n    workflow_run_id: str\n    node_name: str\n    status: str\n    started_at: datetime | None = None\n    completed_at: datetime | None = None\n    error_message: str | None = None\n    retry_count: int = 0\n    created_at: datetime\n''',
        '''class ProductWorkflowNodeRunRead(BaseModel):\n    id: str\n    workflow_run_id: str\n    node_name: str\n    status: str\n    started_at: datetime | None = None\n    completed_at: datetime | None = None\n    error_message: str | None = None\n    retry_count: int = 0\n    input_snapshot: dict[str, Any] = Field(default_factory=dict)\n    output_snapshot: dict[str, Any] = Field(default_factory=dict)\n    metadata: dict[str, Any] = Field(default_factory=dict)\n    created_at: datetime\n''',
    )


def patch_api_routes() -> None:
    path = ROOT / "src/api/workflow_routes.py"
    old = '''            error_message=nr.error_message,\n            retry_count=nr.retry_count,\n            created_at=nr.created_at,\n'''
    new = '''            error_message=nr.error_message,\n            retry_count=nr.retry_count,\n            input_snapshot=nr.input_snapshot_json or {},\n            output_snapshot=nr.output_snapshot_json or {},\n            metadata=nr.metadata_json or {},\n            created_at=nr.created_at,\n'''
    replace_all(path, old, new, expected=2)


def patch_persisted_validator() -> None:
    path = ROOT / "scripts/validate_live_outputs_persisted.py"
    replace_once(
        path,
        '''class _PersistedResponseProxy:\n    def __init__(self, created_response: Any, persisted_response: Any) -> None:\n        self.status_code = created_response.status_code\n        self.headers = persisted_response.headers\n        self.text = persisted_response.text\n        self._persisted_response = persisted_response\n\n    def json(self) -> Any:\n        return self._persisted_response.json()\n''',
        '''def _merge_state(base_state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:\n    merged = dict(base_state)\n    for key, value in update.items():\n        current = merged.get(key)\n        if isinstance(current, dict) and isinstance(value, dict):\n            merged[key] = _merge_state(current, value)\n        else:\n            merged[key] = value\n    return merged\n\n\ndef _reconstruct_state(workflow: dict[str, Any]) -> dict[str, Any]:\n    state = dict(workflow.get("state") or {})\n    for node in workflow.get("nodes") or []:\n        if not isinstance(node, dict):\n            continue\n        output_snapshot = node.get("output_snapshot") or {}\n        if isinstance(output_snapshot, dict):\n            state = _merge_state(state, output_snapshot)\n    state["current_node"] = workflow.get("current_node") or state.get("current_node", "")\n    if workflow.get("error_message"):\n        state["error_message"] = workflow["error_message"]\n    return state\n\n\nclass _PersistedResponseProxy:\n    def __init__(self, created_response: Any, payload: dict[str, Any]) -> None:\n        self.status_code = created_response.status_code\n        self.headers = created_response.headers\n        self.text = json.dumps(payload, ensure_ascii=False, default=str)\n        self._payload = payload\n\n    def json(self) -> Any:\n        return self._payload\n''',
    )
    replace_once(
        path,
        '''        persisted = self._client.get(f"/workflows/product-runs/{workflow_id}")\n        if persisted.status_code != 200:\n            return response\n        return _PersistedResponseProxy(response, persisted)\n''',
        '''        persisted = self._client.get(f"/workflows/product-runs/{workflow_id}")\n        if persisted.status_code != 200:\n            return response\n        payload = persisted.json()\n        payload["state"] = _reconstruct_state(payload)\n        return _PersistedResponseProxy(response, payload)\n''',
    )
    replace_once(
        path,
        '''                workflow = response.json()\n                state = workflow.get("state") or {}\n                node_outputs = state.get("node_outputs") or {}\n''',
        '''                workflow = response.json()\n                state = _reconstruct_state(workflow)\n                node_outputs = state.get("node_outputs") or {}\n                company["reconstructed_state_node_count"] = len(workflow.get("nodes") or [])\n''',
    )


def patch_api_test() -> None:
    path = ROOT / "tests/integration/test_product_workflow_api.py"
    replace_once(
        path,
        'from src.database.models import ActionBriefRecord, AnalysisRun, WorkflowRun',
        'from src.database.models import ActionBriefRecord, AnalysisRun, WorkflowNodeRun, WorkflowRun',
    )
    test = '''\n\ndef test_workflow_node_api_exposes_persisted_snapshots(\n    client: TestClient, startup_id: str\n) -> None:\n    session = next(get_db_session())\n    try:\n        analysis_run_id = _create_analysis_run_record(session, startup_id)\n        workflow_id = _create_workflow_run_record(session, analysis_run_id, startup_id)\n        node = WorkflowNodeRun(\n            workflow_run_id=workflow_id,\n            node_name="map_nvidia_technologies",\n            status="failed",\n            input_snapshot_json={"startup_id": startup_id},\n            output_snapshot_json={\n                "node_outputs": {\n                    "mapping_output": {\n                        "mapping_status": "needs_more_evidence",\n                        "nvidia_mapping_metrics": {"total_mapping_count": 3},\n                    }\n                }\n            },\n            metadata_json={"attempt": 1},\n            error_message="mapping needs more evidence",\n        )\n        session.add(node)\n        session.commit()\n    finally:\n        session.close()\n\n    response = client.get(f"/workflows/product-runs/{workflow_id}")\n    assert response.status_code == 200\n    nodes = response.json()["nodes"]\n    persisted = next(item for item in nodes if item["node_name"] == "map_nvidia_technologies")\n    assert persisted["input_snapshot"] == {"startup_id": startup_id}\n    assert persisted["output_snapshot"]["node_outputs"]["mapping_output"]["mapping_status"] == (\n        "needs_more_evidence"\n    )\n    assert persisted["metadata"] == {"attempt": 1}\n'''
    text = path.read_text(encoding="utf-8")
    if "test_workflow_node_api_exposes_persisted_snapshots" in text:
        raise RuntimeError("Snapshot API test already exists")
    path.write_text(text + test, encoding="utf-8")


def main() -> None:
    patch_api_schema()
    patch_api_routes()
    patch_persisted_validator()
    patch_api_test()


if __name__ == "__main__":
    main()
