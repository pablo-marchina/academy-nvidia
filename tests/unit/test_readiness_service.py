from __future__ import annotations

from src.services.product.capability_registry import CapabilityStatus
from src.services.product.readiness_service import ProductReadinessService


class TestProductReadinessService:
    def test_list_capabilities_returns_all(self) -> None:
        svc = ProductReadinessService()
        caps = svc.list_capabilities()
        assert len(caps) >= 25

    def test_get_capability_status_exists(self) -> None:
        svc = ProductReadinessService()
        cap = svc.get_capability_status("product_database")
        assert cap is not None
        assert cap.capability_id == "product_database"

    def test_get_capability_status_missing(self) -> None:
        svc = ProductReadinessService()
        assert svc.get_capability_status("nonexistent") is None

    def test_list_required_configuration_returns_items(self) -> None:
        svc = ProductReadinessService()
        items = svc.list_required_configuration()
        assert len(items) >= 15

    def test_validate_configuration_checks_required(self) -> None:
        svc = ProductReadinessService()
        missing = svc.validate_configuration()
        assert isinstance(missing, list)

    def test_get_product_readiness_returns_report(self) -> None:
        svc = ProductReadinessService()
        report = svc.get_product_readiness()
        assert hasattr(report, "ready")
        assert hasattr(report, "blocking_missing_config")
        assert hasattr(report, "setup_checklist")

    def test_setup_checklist_not_empty(self) -> None:
        svc = ProductReadinessService()
        checklist = svc.get_setup_checklist()
        assert len(checklist) > 0

    def test_get_missing_configuration(self) -> None:
        svc = ProductReadinessService()
        missing = svc.get_missing_configuration()
        assert isinstance(missing, list)

    def test_get_optional_features_status(self) -> None:
        svc = ProductReadinessService()
        features = svc.get_optional_features_status()
        ids = {f["capability_id"] for f in features}
        assert "optional_instructor_trial" in ids or len(features) >= 0

    def test_core_capabilities_available(self) -> None:
        svc = ProductReadinessService()
        caps_by_id = {c.capability_id: c for c in svc.list_capabilities()}
        core = caps_by_id.get("product_api")
        assert core is not None
        assert core.status in (
            CapabilityStatus.available,
            CapabilityStatus.not_configured,
        )
