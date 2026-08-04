from __future__ import annotations


def test_activation_playbook_abstention_is_noncritical() -> None:
    import src.orchestration.node_impl  # noqa: F401
    from src.orchestration.nodes import WORKFLOW_NODES

    nodes = {node.name: node for node in WORKFLOW_NODES}
    assert nodes["match_activation_playbooks"].critical is False


def test_dossier_service_declares_no_playbook_uncertainty() -> None:
    from pathlib import Path

    source = Path("src/services/product/dossier_service.py").read_text(encoding="utf-8")
    assert 'if playbook_data.get("total") == 0:' in source
    assert '"source": "no_playbook_match"' in source
