"""Product readiness and capability status service.

Aggregates capability registry, configuration registry, and optional
dependency checks to report product readiness, missing configuration,
and setup checklist.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from src.services.product.capability_registry import (
    CAPABILITIES,
    CapabilityDefinition,
    CapabilityStatus,
)
from src.services.product.config_registry import (
    is_extra_installed,
    resolve_config_values,
)

# Checked extras cache
_EXTRA_CACHE: dict[str, bool | None] = {}


@dataclass
class ResolvedCapability:
    capability_id: str
    name: str
    description: str
    category: str
    required: bool
    enabled_by_default: bool
    status: CapabilityStatus
    status_reason: str = ""
    required_env_vars: list[str] = field(default_factory=list)
    optional_env_vars: list[str] = field(default_factory=list)
    required_extras: list[str] = field(default_factory=list)
    required_services: list[str] = field(default_factory=list)
    setup_instructions: str = ""
    failure_mode: str = ""
    user_visible: bool = True
    documentation_ref: str = ""


@dataclass
class ProductReadinessReport:
    ready: bool
    blocking_missing_config: list[dict[str, Any]] = field(default_factory=list)
    optional_missing_config: list[dict[str, Any]] = field(default_factory=list)
    unavailable_capabilities: list[dict[str, Any]] = field(default_factory=list)
    degraded_capabilities: list[dict[str, Any]] = field(default_factory=list)
    setup_checklist: list[dict[str, Any]] = field(default_factory=list)
    user_messages: list[str] = field(default_factory=list)


class ProductReadinessService:
    """Aggregates capability and config status for product readiness."""

    def __init__(self, session: Any | None = None) -> None:
        self.session = session

    def list_capabilities(self) -> list[ResolvedCapability]:
        return [_resolve_capability(c) for c in CAPABILITIES.values()]

    def get_capability_status(self, capability_id: str) -> ResolvedCapability | None:
        cap = CAPABILITIES.get(capability_id)
        if cap is None:
            return None
        return _resolve_capability(cap)

    def list_required_configuration(self) -> list[dict[str, Any]]:
        items = resolve_config_values()
        return [
            {
                "key": item.key,
                "description": item.description,
                "required": item.required,
                "secret": item.secret,
                "default": item.default,
                "current_value": item.current_value,
                "is_set": item.is_set(),
            }
            for item in items
        ]

    def validate_configuration(self) -> list[dict[str, Any]]:
        items = resolve_config_values()
        missing: list[dict[str, Any]] = []
        for item in items:
            if item.required and not item.is_set():
                missing.append(
                    {
                        "key": item.key,
                        "description": item.description,
                        "required_for": item.required_for,
                        "user_message": item.user_message
                        or f"Set {item.key} in your .env file or environment.",
                    }
                )
        return missing

    def get_product_readiness(self) -> ProductReadinessReport:
        capabilities = self.list_capabilities()
        config_items = resolve_config_values()

        blocking: list[dict[str, Any]] = []
        optional_missing: list[dict[str, Any]] = []
        unavailable: list[dict[str, Any]] = []
        degraded: list[dict[str, Any]] = []
        messages: list[str] = []
        checklist: list[dict[str, Any]] = []

        for cap in capabilities:
            if cap.status == CapabilityStatus.not_configured and cap.required:
                blocking.append(
                    {
                        "capability_id": cap.capability_id,
                        "name": cap.name,
                        "reason": cap.status_reason,
                        "setup_instructions": cap.setup_instructions,
                    }
                )
                messages.append(
                    f"Required capability '{cap.name}' is not configured: " f"{cap.status_reason}"
                )
            elif cap.status == CapabilityStatus.not_configured and not cap.required:
                optional_missing.append(
                    {
                        "capability_id": cap.capability_id,
                        "name": cap.name,
                        "reason": cap.status_reason,
                        "setup_instructions": cap.setup_instructions,
                    }
                )
            elif cap.status in (
                CapabilityStatus.unavailable,
                CapabilityStatus.missing_dependency,
            ):
                unavailable.append(
                    {
                        "capability_id": cap.capability_id,
                        "name": cap.name,
                        "reason": cap.status_reason,
                    }
                )
            elif cap.status == CapabilityStatus.degraded:
                degraded.append(
                    {
                        "capability_id": cap.capability_id,
                        "name": cap.name,
                        "reason": cap.status_reason,
                    }
                )

        for item in config_items:
            if item.required:
                checklist.append(
                    {
                        "key": item.key,
                        "description": item.description,
                        "is_set": item.is_set() or bool(item.current_value),
                        "required": True,
                    }
                )

        checklist.append(
            {
                "key": "product_database_connection",
                "description": "Product database is reachable",
                "is_set": len(blocking) == 0,
                "required": True,
            }
        )

        ready = len(blocking) == 0

        return ProductReadinessReport(
            ready=ready,
            blocking_missing_config=blocking,
            optional_missing_config=optional_missing,
            unavailable_capabilities=unavailable,
            degraded_capabilities=degraded,
            setup_checklist=checklist,
            user_messages=list(set(messages)),
        )

    def get_setup_checklist(self) -> list[dict[str, Any]]:
        readiness = self.get_product_readiness()
        return readiness.setup_checklist

    def get_missing_configuration(self) -> list[dict[str, Any]]:
        return self.validate_configuration()

    def get_optional_features_status(self) -> list[dict[str, Any]]:
        capabilities = self.list_capabilities()
        return [
            {
                "capability_id": c.capability_id,
                "name": c.name,
                "status": c.status.value,
                "reason": c.status_reason,
                "setup_instructions": c.setup_instructions,
            }
            for c in capabilities
            if not c.required and c.status not in (CapabilityStatus.available,)
        ]


def _resolve_capability(cap: CapabilityDefinition) -> ResolvedCapability:
    status, reason = _compute_status(cap)
    return ResolvedCapability(
        capability_id=cap.capability_id,
        name=cap.name,
        description=cap.description,
        category=cap.category.value,
        required=cap.required,
        enabled_by_default=cap.enabled_by_default,
        status=status,
        status_reason=reason,
        required_env_vars=list(cap.required_env_vars),
        optional_env_vars=list(cap.optional_env_vars),
        required_extras=list(cap.required_extras),
        required_services=list(cap.required_services),
        setup_instructions=cap.setup_instructions,
        failure_mode=cap.failure_mode,
        user_visible=cap.user_visible,
        documentation_ref=cap.documentation_ref,
    )


def _compute_status(
    cap: CapabilityDefinition,
) -> tuple[CapabilityStatus, str]:
    if not cap.enabled_by_default and not cap.required:
        optional = cap.required_env_vars or cap.required_extras
        if not optional:
            return CapabilityStatus.disabled, "Disabled by default. Enable explicitly."

    for extra in cap.required_extras:
        if not _check_extra(extra):
            return (
                CapabilityStatus.missing_dependency,
                f"Missing extra: [{extra}]. Install with `pip install -e .[{extra}]`.",
            )

    for var in cap.required_env_vars:
        if not os.environ.get(var):
            return (
                CapabilityStatus.not_configured,
                f"Required env var '{var}' is not set.",
            )

    return CapabilityStatus.available, ""


def _check_extra(extra: str) -> bool:
    if extra not in _EXTRA_CACHE:
        _EXTRA_CACHE[extra] = is_extra_installed(extra)
    result = _EXTRA_CACHE[extra]
    return result is True
