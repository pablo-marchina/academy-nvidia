from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping


REQUIRED_PRODUCT_ENV = (
    "APP_MODE",
    "PRODUCT_DB_URL",
    "RAG_VECTOR_BACKEND",
    "RAG_REQUIRED_FOR_PRODUCT",
    "RAG_EMBEDDING_MODEL",
    "QDRANT_URL",
    "QDRANT_COLLECTION",
    "QDRANT_VECTOR_SIZE",
    "AGENT_ORCHESTRATION_ENABLED",
)


@dataclass(frozen=True)
class ProductConfigurationCheck:
    check_id: str
    status: str
    reason: str


@dataclass(frozen=True)
class ProductConfigurationReport:
    status: str
    checks: list[ProductConfigurationCheck] = field(default_factory=list)

    @property
    def failures(self) -> list[ProductConfigurationCheck]:
        return [check for check in self.checks if check.status == "FAIL"]

    def model_dump(self) -> dict[str, object]:
        return {
            "report_id": "product_configuration_report",
            "status": self.status,
            "checks": [check.__dict__ for check in self.checks],
            "failure_count": len(self.failures),
        }


def validate_product_configuration(env: Mapping[str, str] | None = None) -> ProductConfigurationReport:
    values = env or os.environ
    checks: list[ProductConfigurationCheck] = []

    for key in REQUIRED_PRODUCT_ENV:
        checks.append(
            ProductConfigurationCheck(
                check_id=f"env.{key.lower()}",
                status="PASS" if values.get(key, "").strip() else "FAIL",
                reason=f"{key} is {'set' if values.get(key, '').strip() else 'missing'}",
            )
        )

    app_mode = values.get("APP_MODE", "product").lower()
    db_url = values.get("PRODUCT_DB_URL", "")
    checks.append(
        ProductConfigurationCheck(
            check_id="database.postgresql_required",
            status="PASS" if app_mode != "product" or db_url.startswith(("postgresql://", "postgresql+")) else "FAIL",
            reason="APP_MODE=product requires PRODUCT_DB_URL to be PostgreSQL.",
        )
    )
    checks.append(
        ProductConfigurationCheck(
            check_id="rag.qdrant_required",
            status="PASS" if app_mode != "product" or values.get("RAG_VECTOR_BACKEND", "").lower() == "qdrant" else "FAIL",
            reason="APP_MODE=product requires RAG_VECTOR_BACKEND=qdrant.",
        )
    )
    checks.append(
        ProductConfigurationCheck(
            check_id="rag.required_for_recommendations",
            status="PASS"
            if app_mode != "product" or values.get("RAG_REQUIRED_FOR_PRODUCT", "").lower() == "true"
            else "FAIL",
            reason="APP_MODE=product requires RAG_REQUIRED_FOR_PRODUCT=true.",
        )
    )
    checks.append(
        ProductConfigurationCheck(
            check_id="runtime.no_demo_or_mock",
            status="PASS" if _no_demo_or_mock_runtime(values) else "FAIL",
            reason="Product runtime cannot enable demo or mock providers.",
        )
    )
    checks.append(
        ProductConfigurationCheck(
            check_id="runtime.agent_orchestration_required",
            status="PASS"
            if app_mode != "product" or values.get("AGENT_ORCHESTRATION_ENABLED", "").lower() == "true"
            else "FAIL",
            reason="APP_MODE=product requires AGENT_ORCHESTRATION_ENABLED=true.",
        )
    )
    status = "PASS" if all(check.status == "PASS" for check in checks) else "FAIL"
    return ProductConfigurationReport(status=status, checks=checks)


def _no_demo_or_mock_runtime(values: Mapping[str, str]) -> bool:
    forbidden_keys = (
        "DEMO_MODE",
        "USE_DEMO_DATA",
        "MOCK_PROVIDER",
        "USE_MOCK_PROVIDER",
        "ALLOW_MOCK_RUNTIME",
    )
    truthy = {"1", "true", "yes", "on"}
    return all(values.get(key, "").casefold() not in truthy for key in forbidden_keys)
