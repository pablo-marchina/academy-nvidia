from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one match in {path}, found {count}: {old[:220]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_activation_node() -> None:
    path = ROOT / "src/orchestration/node_impl.py"
    replace_once(
        path,
        '''    try:\n        act_service = ActivationPlaybookService(session)\n        recs = act_service.generate_recommendations_for_run(analysis_run_id)\n''',
        '''    try:\n        # Gap and mapping nodes commit their terminal snapshots and product\n        # records before this node runs. Expire identity-map relationships so\n        # ActivationPlaybookService reads the newly persisted gaps/mappings\n        # instead of collections cached when the AnalysisRun was created.\n        session.expire_all()\n        act_service = ActivationPlaybookService(session)\n        recs = act_service.generate_recommendations_for_run(analysis_run_id)\n''',
    )


def patch_mapping_test_fixture() -> None:
    path = ROOT / "tests/unit/test_mapping_selected_scope_contract.py"
    replace_once(
        path,
        '''from src.diagnosis.schemas import GapType\nfrom src.recommendation.nvidia_technology_mapping import (\n''',
        '''from src.diagnosis.schemas import GapType\nfrom src.orchestration.node_impl import _runtime_decision_inventory\nfrom src.recommendation.nvidia_technology_mapping import (\n''',
    )
    replace_once(
        path,
        '''        gap_metrics=diagnosis.metrics,\n        evidence_items=evidence,\n    )\n''',
        '''        gap_metrics=diagnosis.metrics,\n        evidence_items=evidence,\n        inventory=_runtime_decision_inventory(),\n    )\n''',
    )


def add_activation_test() -> None:
    path = ROOT / "tests/unit/test_activation_playbook_session_refresh.py"
    path.write_text(
        '''from __future__ import annotations\n\nfrom src.orchestration.node_impl import node_match_activation_playbooks\nfrom src.orchestration.state import NodeStatus, ProductWorkflowState\n\n\nclass _FakeSession:\n    def __init__(self) -> None:\n        self.expired = False\n\n    def expire_all(self) -> None:\n        self.expired = True\n\n\nclass _FakeActivationRepo:\n    def __init__(self) -> None:\n        self.persisted = False\n\n    def replace_recommendations_for_analysis_run(self, analysis_run_id, recs):  # noqa: ANN001\n        assert analysis_run_id == "analysis-test"\n        assert recs\n        self.persisted = True\n\n\nclass _FakeActivationService:\n    created: list["_FakeActivationService"] = []\n\n    def __init__(self, session: _FakeSession) -> None:\n        assert session.expired is True\n        self.activation_repo = _FakeActivationRepo()\n        self.__class__.created.append(self)\n\n    def generate_recommendations_for_run(self, analysis_run_id: str):  # noqa: ANN201\n        assert analysis_run_id == "analysis-test"\n        return [{"id": "activation-1"}]\n\n\ndef test_activation_node_refreshes_session_before_reading_persisted_gaps_and_mappings(\n    monkeypatch,  # noqa: ANN001\n) -> None:\n    _FakeActivationService.created.clear()\n    monkeypatch.setattr(\n        "src.orchestration.node_impl.ActivationPlaybookService",\n        _FakeActivationService,\n    )\n    session = _FakeSession()\n    state = ProductWorkflowState(\n        workflow_id="workflow-test",\n        analysis_run_id="analysis-test",\n        metadata_json={"_session": session},\n    )\n\n    result = node_match_activation_playbooks(state)\n\n    assert result.status == NodeStatus.COMPLETED\n    assert result.state_updates["activation_recommendation_ids"] == ["activation-1"]\n    assert _FakeActivationService.created[0].activation_repo.persisted is True\n''',
        encoding="utf-8",
    )


def main() -> None:
    patch_activation_node()
    patch_mapping_test_fixture()
    add_activation_test()


if __name__ == "__main__":
    main()
