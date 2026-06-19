"""DEPRECATED: LangGraph StateGraph for legacy product workflow skeleton.

Use src/orchestration/graph.py instead. This module is kept for
backward compatibility and will be removed in a future release.
Execution is tracked via the ``executed_nodes`` list.
"""

from __future__ import annotations

from functools import partial
from typing import Any

from src.agents.interfaces import (
    DiagnoseGapsService,
    GenerateBriefService,
    PersistWorkflowResultService,
    RagService,
    RankRecommendationsService,
    ScoreService,
)
from src.agents.state import StartupRadarState
from src.extraction.schemas import SourceType
from src.quantitative.params import (
    DISCOVERY_MAX_SOURCES,
    DISCOVERY_RATE_LIMIT,
    GAP_BUSINESS_IMPACT_MAP,
    MAX_SEARCH_DEPTH,
    PRIORITY_SCORE_WEIGHTS,
    WORKFLOW_THRESHOLDS,
)
from src.scraping.source_policy import source_quality_score

LANGGRAPH_AVAILABLE: bool
_CHECKPOINTER_ENABLED: bool = False
try:
    from langgraph.graph import END, START, StateGraph  # noqa: I001
    from langgraph.types import interrupt  # noqa: I001

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


class NodeExecutionError(Exception):
    """Raised when a LangGraph node execution fails."""

    def __init__(self, node_name: str, error_message: str) -> None:
        self.node_name = node_name
        self.error_message = error_message
        super().__init__(f"[{node_name}] {error_message}")


NODE_NAMES: list[str] = [
    "preflight_configuration_check",
    "plan_search",
    "collect_sources",
    "extract_profile",
    "validate_evidence",
    "score_startup",
    "diagnose_gaps",
    "retrieve_nvidia_context",
    "build_technology_mappings",
    "rank_recommendations",
    "generate_brief",
    "run_quality_gates",
    "finish",
]


def _append_node(state: StartupRadarState, name: str) -> list[str]:
    return list(state.get("executed_nodes", [])) + [name]


def _preflight_configuration_check(state: StartupRadarState) -> dict[str, Any]:
    from src.services.product.readiness_service import ProductReadinessService

    try:
        svc = ProductReadinessService()
        report = svc.get_product_readiness()
    except Exception as exc:
        return {
            "status": "blocked",
            "blockers": [f"Readiness check failed: {type(exc).__name__}"],
            "executed_nodes": _append_node(state, "preflight_configuration_check"),
        }

    if report.ready:
        return {
            "status": "ready_for_execution",
            "executed_nodes": _append_node(state, "preflight_configuration_check"),
        }

    messages = list(report.user_messages)
    blocker_items: list[str] = list(messages)

    for item in report.blocking_missing_config:
        reason = item.get("reason", "") if isinstance(item, dict) else str(item)
        if reason and reason not in blocker_items:
            blocker_items.append(reason)

    for item in report.unavailable_capabilities:
        reason = item.get("reason", "") if isinstance(item, dict) else str(item)
        if reason and reason not in blocker_items:
            blocker_items.append(reason)

    for item in report.degraded_capabilities:
        reason = item.get("reason", "") if isinstance(item, dict) else str(item)
        if reason and reason not in blocker_items:
            blocker_items.append(reason)

    if not blocker_items:
        blocker_items.append("Product is not ready")

    return {
        "status": "blocked",
        "blockers": blocker_items,
        "executed_nodes": _append_node(state, "preflight_configuration_check"),
    }


def _route_after_preflight(state: StartupRadarState) -> str:
    blockers = state.get("blockers", [])
    if blockers or state.get("status") == "blocked":
        return "finish"
    return "plan_search"


def _plan_search(state: StartupRadarState) -> dict[str, Any]:
    from src.agents.search_planner import build_search_plan

    run_id = state.get("run_id", "unknown")
    startup_id = state.get("startup_id")
    startup_name = state.get("startup_name")
    website_url = state.get("website_url")
    notes = state.get("notes")
    evidence_request_reason = state.get("evidence_request_reason")
    evidence_retry_count = state.get("evidence_retry_count", 0)
    max_evidence_retries = state.get("max_evidence_retries", 3)
    blockers: list[str] = list(state.get("blockers", []))

    has_basis = bool(startup_name) or bool(website_url)

    objective_parts: list[str] = []
    if startup_name:
        objective_parts.append(f"Collect evidence for startup {startup_name}")
    elif website_url:
        objective_parts.append(f"Collect evidence from {website_url}")
    else:
        objective_parts.append("Collect evidence (no startup name or URL provided)")

    if evidence_request_reason:
        objective_parts.append(f"Additional evidence requested: {evidence_request_reason}")

    objective = " | ".join(objective_parts)

    # ── retry context ──────────────────────────────────────────────
    retry_context: dict[str, Any] | None = None
    if evidence_request_reason:
        retry_context = {
            "evidence_request_reason": evidence_request_reason,
            "evidence_retry_count": evidence_retry_count,
        }

    # ── evidence retry limit check ─────────────────────────────────
    if evidence_retry_count > max_evidence_retries:
        msg = "max_evidence_retries_reached"
        if msg not in blockers:
            blockers.append(msg)
        return {
            "status": "max_evidence_retries_reached",
            "blockers": blockers,
            "search_plan": {
                "run_id": run_id,
                "startup_id": startup_id,
                "objective": objective,
                "search_queries": [],
                "target_source_types": [],
                "required_evidence_types": [],
                "max_sources": 0,
                "max_depth": 0,
                "rate_limit_policy": {},
                "compliance_notes": [],
                "generated_from": {
                    "startup_name": bool(startup_name),
                    "website_url": bool(website_url),
                    "notes": bool(notes),
                },
                "retry_context": retry_context,
            },
            "search_plan_metrics": {
                "query_count": 0,
                "target_source_type_count": 0,
                "required_evidence_type_count": 0,
                "max_sources": 0,
                "max_depth": 0,
                "evidence_retry_count": evidence_retry_count,
                "planning_status": "failed",
            },
            "executed_nodes": _append_node(state, "plan_search"),
        }

    # ── build search queries ───────────────────────────────────────
    target_source_types: list[str] = [
        "official_website",
        "technical_docs",
        "funding_news",
        "jobs",
        "github_or_code",
        "ecosystem_directory",
    ]
    required_evidence_types: list[str] = [
        "ai_native_signal",
        "technical_stack",
        "product_signal",
        "traction_or_funding_signal",
        "nvidia_fit_signal",
    ]

    queries: list[dict[str, str]] = []
    if has_basis:
        if startup_name:
            try:
                queries = build_search_plan(startup_name)
            except Exception as exc:
                blockers.append(f"Search plan failed: {type(exc).__name__}")
        elif website_url:
            from urllib.parse import urlparse
            parsed = urlparse(website_url)
            host = parsed.netloc or website_url
            queries.append({
                "url": website_url,
                "source_type": "official_website",
                "reason": "Provided website URL",
            })
            domain = host.replace("www.", "")
            queries.append({
                "url": f"https://www.google.com/search?q=site:{domain}+startup+AI",
                "source_type": "technical_docs",
                "reason": "Google search for related content",
            })

    # ── generated_from ─────────────────────────────────────────────
    generated_from: dict[str, bool] = {
        "startup_name": bool(startup_name),
        "website_url": bool(website_url),
        "notes": bool(notes),
    }

    # ── compliance notes ───────────────────────────────────────────
    compliance_notes: list[str] = ["robots.txt compliant", "no_paywall_bypass"]

    # ── constants ──────────────────────────────────────────────────
    max_sources = DISCOVERY_MAX_SOURCES
    max_depth = MAX_SEARCH_DEPTH
    rate_limit_policy: dict[str, Any] = dict(DISCOVERY_RATE_LIMIT)

    # ── planning_status ────────────────────────────────────────────
    errors: list[str] = []
    if has_basis:
        if blockers:
            planning_status = "failed"
            status_val = "search_plan_failed"
            review_required = False
        else:
            planning_status = "passed"
            status_val = "search_plan_ready"
            review_required = False
    else:
        planning_status = "needs_review"
        status_val = "search_plan_needs_review"
        review_required = True

    search_plan: dict[str, Any] = {
        "run_id": run_id,
        "startup_id": startup_id,
        "objective": objective,
        "search_queries": queries,
        "target_source_types": target_source_types,
        "required_evidence_types": required_evidence_types,
        "max_sources": max_sources,
        "max_depth": max_depth,
        "rate_limit_policy": rate_limit_policy,
        "compliance_notes": compliance_notes,
        "generated_from": generated_from,
        "retry_context": retry_context,
    }

    search_plan_metrics: dict[str, Any] = {
        "query_count": len(queries),
        "target_source_type_count": len(target_source_types),
        "required_evidence_type_count": len(required_evidence_types),
        "max_sources": max_sources,
        "max_depth": max_depth,
        "evidence_retry_count": evidence_retry_count,
        "planning_status": planning_status,
    }

    updates: dict[str, Any] = {
        "status": status_val,
        "search_plan": search_plan,
        "search_plan_metrics": search_plan_metrics,
        "review_required": review_required,
        "executed_nodes": _append_node(state, "plan_search"),
    }
    if errors:
        updates["blockers"] = list(state.get("blockers", [])) + errors
    if blockers:
        updates["blockers"] = blockers
    return updates


def _collect_sources(state: StartupRadarState) -> dict[str, Any]:
    from src.quality.decision_calibration_registry import (
        get_project_decision_inventory,
        validate_decision_for_production,
    )
    from src.scraping.http_collector import (
        CollectionRequest,
        HttpSourceCollector,
    )
    from src.scraping.source_registry import list_production_enabled_sources

    run_id = state.get("run_id", "unknown")
    website_url = state.get("website_url")
    search_plan: dict[str, Any] = state.get("search_plan", {})
    blockers: list[str] = list(state.get("blockers", []))

    # ── Required calibrated decisions ───────────────────────────────
    REQUIRED_DECISIONS: list[tuple[str, str | None]] = [
        ("scraping.max_sources", None),
        ("scraping.max_depth", None),
        ("collection.http_timeout_seconds", "timeout_seconds"),
        ("collection.http_max_retries", "max_retries"),
        ("collection.http_backoff_base_seconds", "backoff_base_seconds"),
        ("collection.stop_condition", None),
    ]

    inventory = get_project_decision_inventory()
    calibrated_limits: dict[str, Any] = {}
    for decision_id, limit_key in REQUIRED_DECISIONS:
        found = False
        for rec in inventory:
            if rec.decision_id == decision_id:
                found = True
                validation_result = validate_decision_for_production(rec)
                if not validation_result.passed:
                    blockers.append(
                        f"Calibrated decision '{decision_id}' blocked: "
                        f"{'; '.join(validation_result.reasons)}"
                    )
                elif rec.calibration_status in ("UNCALIBRATED", "BLOCKED"):
                    blockers.append(
                        f"Calibrated decision '{decision_id}' is "
                        f"{rec.calibration_status}"
                    )
                elif limit_key is not None:
                    calibrated_limits[limit_key] = rec.current_value
                break
        if not found:
            blockers.append(
                f"Calibrated decision '{decision_id}' not found in registry"
            )

    if blockers:
        return {
            "status": "collection_blocked",
            "collection_status": "collection_blocked",
            "source_candidates": [],
            "raw_evidence_candidates": [],
            "evidence_items": [],
            "collection_metrics": _empty_collection_metrics(),
            "blockers": blockers,
            "review_required": True,
            "executed_nodes": _append_node(state, "collect_sources"),
        }

    # ── Get production_enabled sources ──────────────────────────────
    all_enabled = list_production_enabled_sources()
    if not all_enabled:
        return {
            "status": "collection_blocked",
            "collection_status": "collection_blocked",
            "source_candidates": [],
            "raw_evidence_candidates": [],
            "evidence_items": [],
            "collection_metrics": _empty_collection_metrics(),
            "blockers": ["No production-enabled sources available"],
            "review_required": True,
            "executed_nodes": _append_node(state, "collect_sources"),
        }

    # ── Filter by search_plan target_source_types ───────────────────
    target_types: list[str] = search_plan.get("target_source_types", [])
    max_sources: int = search_plan.get("max_sources", 10)

    if target_types:
        matching = [s for s in all_enabled if s.source_category in target_types]
    else:
        matching = list(all_enabled)

    matching = matching[:max_sources]

    # ── Resolve base_url for startup-specific sources ───────────────
    populated: list[Any] = []
    for src in matching:
        url = (src.base_url or "").strip()
        if not url and src.source_category == "official_website" and website_url:
            url = website_url
        if not url:
            continue
        populated.append(src.model_copy(update={"base_url": url}))

    if not populated:
        return {
            "status": "collection_blocked",
            "collection_status": "collection_blocked",
            "source_candidates": [],
            "raw_evidence_candidates": [],
            "evidence_items": [],
            "collection_metrics": _empty_collection_metrics(),
            "blockers": ["No collectable sources after URL resolution"],
            "review_required": True,
            "executed_nodes": _append_node(state, "collect_sources"),
        }

    # ── Call real collector ─────────────────────────────────────────
    collector = HttpSourceCollector()
    request = CollectionRequest(
        run_id=run_id,
        source_records=populated,
        calibrated_limits=calibrated_limits,
    )

    result = collector.collect(request)

    # ── Process results ─────────────────────────────────────────────
    source_candidates: list[dict[str, Any]] = []
    raw_evidence_candidates: list[dict[str, Any]] = []
    evidence_items: list[dict[str, Any]] = []
    fetch_errors: list[str] = []

    for sfr in result.sources:
        candidate: dict[str, Any] = {
            "source_id": sfr.source_id,
            "source_url": sfr.source_url,
            "status": sfr.status,
            "http_status_code": sfr.http_status_code,
            "content_hash": sfr.content_hash,
            "latency_ms": sfr.latency_ms,
            "content_bytes": sfr.content_bytes,
            "extraction_status": sfr.extraction_status,
            "robots_allowed": sfr.robots_allowed,
            "compliance_status": sfr.compliance_status,
            "error_code": sfr.error_code,
            "error_message": sfr.error_message_sanitized,
        }
        source_candidates.append(candidate)

        if sfr.status == "fetched" and sfr.extracted_text:
            ev_item: dict[str, Any] = {
                "url": sfr.source_url,
                "text": sfr.extracted_text,
                "source_type": sfr.metadata.get("source_category", "unknown"),
                "source_id": sfr.source_id,
                "reason": sfr.metadata.get("source_name", ""),
                "fetched_at": sfr.fetched_at.isoformat(),
                "status_code": sfr.http_status_code,
                "content_hash": sfr.content_hash,
                "latency_ms": sfr.latency_ms,
                "content_bytes": sfr.content_bytes,
                "extraction_status": sfr.extraction_status,
            }
            evidence_items.append(ev_item)
            raw_evidence_candidates.append({
                "source_id": sfr.source_id,
                "source_url": sfr.source_url,
                "text": sfr.extracted_text,
                "source_category": sfr.metadata.get("source_category", ""),
                "source_name": sfr.metadata.get("source_name", ""),
                "collected_at": sfr.fetched_at.isoformat(),
                "content_hash": sfr.content_hash,
                "latency_ms": sfr.latency_ms,
                "robots_allowed": sfr.robots_allowed,
                "duplicate": False,
            })
        elif sfr.status == "duplicate" and sfr.extracted_text:
            raw_evidence_candidates.append({
                "source_id": sfr.source_id,
                "source_url": sfr.source_url,
                "text": sfr.extracted_text,
                "source_category": sfr.metadata.get("source_category", ""),
                "source_name": sfr.metadata.get("source_name", ""),
                "collected_at": sfr.fetched_at.isoformat(),
                "content_hash": sfr.content_hash,
                "latency_ms": sfr.latency_ms,
                "robots_allowed": sfr.robots_allowed,
                "duplicate": True,
            })
        elif sfr.status in ("blocked", "failed"):
            msg = (
                f"{sfr.source_url}: {sfr.error_code or sfr.status}"
            )
            if sfr.error_message_sanitized:
                msg += f" — {sfr.error_message_sanitized}"
            if msg not in fetch_errors:
                fetch_errors.append(msg)

    # ── Determine status ────────────────────────────────────────────
    metrics = result.metrics
    metrics_dict: dict[str, Any] = {
        "attempted_sources_count": metrics.attempted_sources_count,
        "fetched_sources_count": metrics.fetched_sources_count,
        "blocked_sources_count": metrics.blocked_sources_count,
        "failed_sources_count": metrics.failed_sources_count,
        "robots_blocked_count": metrics.robots_blocked_count,
        "compliance_blocked_count": metrics.compliance_blocked_count,
        "duplicate_count": metrics.duplicate_count,
        "total_latency_ms": metrics.total_latency_ms,
        "median_latency_ms": metrics.median_latency_ms,
        "total_content_bytes": metrics.total_content_bytes,
        "extraction_success_rate": metrics.extraction_success_rate,
        "fetch_success_rate": metrics.fetch_success_rate,
    }

    updates_blockers = list(blockers)
    for e in fetch_errors:
        if e not in updates_blockers:
            updates_blockers.append(e)

    fetched_count = metrics.fetched_sources_count
    if fetched_count > 0 and fetch_errors:
        collection_status = "partial"
        status = "sources_collected_partial"
        review_required = False
    elif fetched_count > 0 and not fetch_errors:
        collection_status = "sources_collected"
        status = "sources_collected"
        review_required = False
    else:
        collection_status = "collection_failed"
        status = "collection_failed"
        review_required = True

    updates: dict[str, Any] = {
        "status": status,
        "collection_status": collection_status,
        "source_candidates": source_candidates,
        "raw_evidence_candidates": raw_evidence_candidates,
        "evidence_items": evidence_items,
        "collection_metrics": metrics_dict,
        "review_required": review_required,
        "executed_nodes": _append_node(state, "collect_sources"),
    }
    if updates_blockers:
        updates["blockers"] = updates_blockers

    return updates


def _empty_collection_metrics() -> dict[str, Any]:
    return {
        "attempted_sources_count": 0,
        "fetched_sources_count": 0,
        "blocked_sources_count": 0,
        "failed_sources_count": 0,
        "robots_blocked_count": 0,
        "compliance_blocked_count": 0,
        "duplicate_count": 0,
        "total_latency_ms": 0,
        "median_latency_ms": 0.0,
        "total_content_bytes": 0,
        "extraction_success_rate": 0.0,
        "fetch_success_rate": 0.0,
    }


def _build_structured_claims(
    claims_str: list[str],
    raw_evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    structured: list[dict[str, Any]] = []
    if raw_evidence:
        for ev in raw_evidence:
            refs: list[str] = []
            url = ev.get("source_url") or ev.get("url", "")
            if url:
                refs.append(str(url))
            structured.append({
                "claim_text": ev.get("claim", ""),
                "criticality": "critical" if ev.get("source_type") == "official_site" else "normal",
                "support_status": "insufficient_evidence",
                "supporting_evidence_refs": refs,
                "confidence": ev.get("confidence", "low"),
            })
    elif claims_str:
        for c in claims_str:
            structured.append({
                "claim_text": c,
                "criticality": "normal",
                "support_status": "unsupported",
                "supporting_evidence_refs": [],
                "confidence": "low",
            })
    return structured


def _extract_profile(state: StartupRadarState) -> dict[str, Any]:
    from src.agents.extractor_agent import extract_profiles_from_candidates
    from src.quality.decision_calibration_registry import (
        get_project_decision_inventory,
        validate_decision_for_production,
    )

    run_id = state.get("run_id", "unknown")
    startup_id = state.get("startup_id")
    startup_name = state.get("startup_name")
    raw_evidence_candidates: list[dict[str, Any]] = state.get("raw_evidence_candidates", [])
    blockers: list[str] = list(state.get("blockers", []))

    # ── 1. Check extractor availability ─────────────────────────────────
    try:
        from src.extraction.extractor import extract_profile as _check_extractor
        _check_extractor("test", "https://test.com")
    except ImportError:
        return {
            "status": "extractor_unavailable",
            "extraction_status": "blocked",
            "evidence_items": [],
            "claims": [],
            "raw_evidence": [],
            "startup_profile": {},
            "extraction_metrics": _empty_extraction_metrics(),
            "blockers": blockers + ["Real extractor not available (ImportError)"],
            "review_required": True,
            "executed_nodes": _append_node(state, "extract_profile"),
        }
    except Exception:
        pass

    # ── 2. Check for empty raw_evidence_candidates ──────────────────────
    if not raw_evidence_candidates:
        return {
            "status": "extraction_blocked",
            "extraction_status": "blocked",
            "evidence_items": [],
            "claims": [],
            "raw_evidence": [],
            "startup_profile": {},
            "extraction_metrics": _empty_extraction_metrics(),
            "blockers": blockers + ["raw_evidence_candidates is empty"],
            "review_required": True,
            "executed_nodes": _append_node(state, "extract_profile"),
        }

    # ── 3. Check required calibrated decisions for sufficiency ──────────
    REQUIRED_DECISIONS: list[str] = [
        "extraction.sufficiency.min_evidence_items",
        "extraction.sufficiency.min_claims",
    ]
    inventory = get_project_decision_inventory()
    sufficiency_decisions: dict[str, Any] = {}
    sufficiency_uncalibrated: bool = False
    for decision_id in REQUIRED_DECISIONS:
        found = False
        for rec in inventory:
            if rec.decision_id == decision_id:
                found = True
                validation = validate_decision_for_production(rec)
                if validation.passed:
                    sufficiency_decisions[decision_id] = rec.current_value
                else:
                    sufficiency_uncalibrated = True
                break
        if not found:
            sufficiency_uncalibrated = True

    # ── 4. Run extraction -------------------------------------------------
    result = extract_profiles_from_candidates(
        raw_evidence_candidates=raw_evidence_candidates,
        startup_name=startup_name,
        startup_id=startup_id,
        run_id=run_id,
    )

    evidence_items: list[dict[str, Any]] = result["evidence_items"]
    claims: list[dict[str, Any]] = result["claims"]
    startup_profile: dict[str, Any] = result["startup_profile"]
    extraction_metrics: dict[str, Any] = result["extraction_metrics"]
    errors: list[str] = result["errors"]

    # ── 5. Determine extraction_status ──────────────────────────────────
    ev_count = extraction_metrics.get("evidence_items_count", 0)
    cl_count = extraction_metrics.get("claims_count", 0)
    success_rate = extraction_metrics.get("extraction_success_rate", 0.0)

    if blockers:
        extraction_status = "blocked"
        status_val = "extraction_blocked"
        review_required = True
    elif ev_count == 0 and cl_count == 0:
        extraction_status = "blocked"
        status_val = "extraction_blocked"
        review_required = True
        msg = "extraction produced zero evidence_items and zero claims"
        if msg not in blockers:
            blockers.append(msg)
    elif sufficiency_uncalibrated:
        extraction_status = "partial"
        status_val = "profile_extracted_partial"
        review_required = True
    elif sufficiency_decisions:
        min_ev = int(sufficiency_decisions.get("extraction.sufficiency.min_evidence_items", 1))
        min_cl = int(sufficiency_decisions.get("extraction.sufficiency.min_claims", 1))
        if ev_count >= min_ev and cl_count >= min_cl:
            extraction_status = "passed"
            status_val = "profile_extracted"
            review_required = False
        else:
            extraction_status = "partial"
            status_val = "profile_extracted_partial"
            review_required = True
    elif success_rate < 1.0:
        extraction_status = "partial"
        status_val = "profile_extracted_partial"
        review_required = False
    else:
        extraction_status = "partial"
        status_val = "profile_extracted_partial"
        review_required = True

    updates: dict[str, Any] = {
        "status": status_val,
        "extraction_status": extraction_status,
        "evidence_items": evidence_items,
        "claims": claims,
        "raw_evidence": result.get("raw_evidence", []),
        "startup_profile": startup_profile,
        "extraction_metrics": extraction_metrics,
        "review_required": review_required,
        "executed_nodes": _append_node(state, "extract_profile"),
    }
    if errors:
        updates["blockers"] = blockers + errors
    elif blockers:
        updates["blockers"] = blockers
    return updates


def _empty_extraction_metrics() -> dict[str, Any]:
    return {
        "raw_candidates_count": 0,
        "extraction_attempt_count": 0,
        "extraction_success_count": 0,
        "extraction_failure_count": 0,
        "evidence_items_count": 0,
        "claims_count": 0,
        "empty_content_count": 0,
        "duplicate_content_count": 0,
        "source_type_coverage": {},
        "extraction_success_rate": 0.0,
        "profile_field_coverage": 0.0,
        "average_extraction_confidence": 0.0,
    }


def _validate_evidence(state: StartupRadarState) -> dict[str, Any]:
    from src.agents.evidence_validator_agent import validate_evidence
    from src.quality.decision_calibration_registry import (
        get_project_decision_inventory,
        validate_decision_for_production,
    )
    from src.scoring.evidence_confidence import (
        compute_evidence_confidence_score,
    )
    from src.scoring.source_quality import (
        compute_source_quality_score,
    )

    raw_evidence = state.get("raw_evidence", [])
    evidence_items = state.get("evidence_items", [])
    existing_claims = state.get("claims", [])

    claims_str, items_with_meta, validated_evidence, errors = validate_evidence(
        raw_evidence, evidence_items
    )

    evidence_items_count = len(items_with_meta)
    claims_count = len(validated_evidence)

    structured_claims: list[dict[str, Any]] = []
    if validated_evidence:
        for v in validated_evidence:
            refs: list[str] = []
            src_url = v.get("source_url")
            if src_url:
                refs.append(str(src_url))
            is_critical = v.get("is_critical", False)
            ek = v.get("evidence_kind", "unverified")
            if ek in ("fact", "strong_inference"):
                support_status = "supported"
            elif ek in ("weak_inference", "hypothesis"):
                support_status = "insufficient_evidence"
            else:
                support_status = "unsupported"
            structured_claims.append({
                "claim_text": v.get("claim", ""),
                "criticality": "critical" if is_critical else "normal",
                "support_status": support_status,
                "supporting_evidence_refs": refs,
                "confidence": v.get("confidence", "low"),
            })
    elif existing_claims:
        for c in existing_claims:
            if isinstance(c, dict):
                structured_claims.append(c)
            elif isinstance(c, str):
                structured_claims.append({
                    "claim_text": c,
                    "criticality": "normal",
                    "support_status": "unsupported",
                    "supporting_evidence_refs": [],
                    "confidence": "low",
                })

    unsupported_kinds: set[str] = {"unsupported", "insufficient_evidence", "conflicting"}
    unsupported_critical_claims_count = sum(
        1 for c in structured_claims
        if c.get("criticality") == "critical"
        and c.get("support_status") in unsupported_kinds
    )
    supported_claims_count = sum(
        1 for c in structured_claims
        if c.get("support_status") == "supported"
    )

    # ── 1. Check required calibration decisions ────────────────────────────
    REQUIRED_CALIBRATION_DECISIONS: list[tuple[str, str | None]] = [
        ("weight.source_quality_score.weights", None),
        ("threshold.source_quality_score.production_min", "sq_threshold"),
        ("weight.evidence_confidence_score.weights", None),
        ("threshold.evidence_confidence_score.production_min", "ec_threshold"),
    ]

    inventory = get_project_decision_inventory()
    calibration_blockers: list[str] = []
    calibrated_values: dict[str, float] = {}
    for decision_id, value_key in REQUIRED_CALIBRATION_DECISIONS:
        found = False
        for rec in inventory:
            if rec.decision_id == decision_id:
                found = True
                validation = validate_decision_for_production(rec)
                if not validation.passed:
                    calibration_blockers.append(
                        f"Calibrated decision '{decision_id}' blocked: "
                        f"{'; '.join(validation.reasons)}"
                    )
                elif value_key is not None:
                    if isinstance(rec.current_value, (int, float)):
                        calibrated_values[value_key] = float(rec.current_value)
                    else:
                        calibration_blockers.append(
                            f"Decision '{decision_id}' has non-numeric current_value"
                        )
                break
        if not found:
            calibration_blockers.append(
                f"Calibrated decision '{decision_id}' not found in registry"
            )

    sq_threshold = calibrated_values.get("sq_threshold", 0.65)
    ec_threshold = calibrated_values.get("ec_threshold", 0.55)

    # ── 2. Check optional gating decisions ─────────────────────────────────
    OPTIONAL_DECISIONS: list[str] = [
        "threshold.source_quality_score.production_ready_evidence_ratio",
        "threshold.source_quality_score.min_supported_claims",
    ]
    missing_optional: list[str] = []
    for decision_id in OPTIONAL_DECISIONS:
        found = False
        for rec in inventory:
            if rec.decision_id == decision_id:
                found = True
                break
        if not found:
            missing_optional.append(
                f"Optional gating decision '{decision_id}' not found in registry — "
                "cannot determine sufficient acceptance threshold"
            )

    # ── 3. If calibration blocked → blocked_uncalibrated_scoring ───────────
    if calibration_blockers:
        metrics_blocked: dict[str, Any] = {
            "evidence_items_count": evidence_items_count,
            "scored_evidence_count": 0,
            "accepted_evidence_count": 0,
            "rejected_evidence_count": 0,
            "low_source_quality_count": 0,
            "low_evidence_confidence_count": 0,
            "claims_count": claims_count,
            "supported_claims_count": supported_claims_count,
            "unsupported_claims_count": claims_count - supported_claims_count,
            "unsupported_critical_claims_count": unsupported_critical_claims_count,
            "average_source_quality_score": 0.0,
            "average_evidence_confidence_score": 0.0,
            "production_ready_evidence_ratio": 0.0,
        }
        evidence_validation_blocked: dict[str, Any] = {
            "status": "blocked_uncalibrated_scoring",
            "metrics": dict(metrics_blocked),
            "failed_checks": list(calibration_blockers),
            "warning_checks": [],
            "thresholds": {},
        }
        blockers_blocked = list(state.get("blockers", []))
        for b in calibration_blockers:
            if b not in blockers_blocked:
                blockers_blocked.append(b)
        return {
            "status": "evidence_scoring_uncalibrated",
            "claims": structured_claims,
            "evidence_items": items_with_meta,
            "validated_evidence": validated_evidence,
            "unsupported_critical_claims_count": unsupported_critical_claims_count,
            "evidence_validation": evidence_validation_blocked,
            "evidence_validation_metrics": metrics_blocked,
            "accepted_evidence_items": [],
            "rejected_evidence_items": [],
            "review_required": True,
            "blockers": blockers_blocked,
            "executed_nodes": _append_node(state, "validate_evidence"),
        }

    # ── 4. Score every evidence item ───────────────────────────────────────
    normalized_items: list[dict[str, Any]] = []
    accepted_items: list[dict[str, Any]] = []
    rejected_items: list[dict[str, Any]] = []
    scored_count = 0
    accepted_count = 0
    rejected_count = 0
    low_sq_count = 0
    low_ec_count = 0
    sq_scores: list[float] = []
    ec_scores: list[float] = []

    for item in items_with_meta:
        normalized: dict[str, Any] = dict(item)
        if "source_url" not in normalized and "url" in normalized:
            normalized["source_url"] = normalized["url"]

        sq_result = compute_source_quality_score(normalized, inventory=inventory)
        normalized["source_quality_score"] = sq_result.score
        normalized["source_quality_score_status"] = sq_result.score_status.value
        normalized["source_quality_score_features"] = sq_result.features.model_dump()
        normalized["source_quality_score_calibration_decision_ids"] = [sq_result.calibration_decision_id]

        normalized["source_quality_score"] = sq_result.score
        ec_result = compute_evidence_confidence_score(normalized, inventory=inventory)
        normalized["evidence_confidence_score"] = ec_result.score
        normalized["evidence_confidence_score_status"] = ec_result.score_status.value
        normalized["evidence_confidence_score_features"] = ec_result.features.model_dump()
        normalized["evidence_confidence_score_calibration_decision_ids"] = [ec_result.calibration_decision_id]

        if "snippet" not in normalized and "text" in normalized:
            normalized["snippet"] = normalized["text"]

        normalized_items.append(normalized)
        scored_count += 1
        sq_scores.append(sq_result.score)
        ec_scores.append(ec_result.score)

        ek = normalized.get("evidence_kind", "unverified")
        is_critical = normalized.get("is_critical", False)

        item_status: str
        if is_critical and ek in ("unverified", "weak_inference"):
            item_status = "rejected_unsupported_claim"
        elif sq_result.score < sq_threshold:
            item_status = "rejected_low_source_quality"
            low_sq_count += 1
        elif ec_result.score < ec_threshold:
            item_status = "rejected_low_evidence_confidence"
            low_ec_count += 1
        else:
            item_status = "accepted"
            accepted_count += 1

        normalized["evidence_item_status"] = item_status
        if item_status == "accepted":
            accepted_items.append(normalized)
        else:
            rejected_items.append(normalized)
            if item_status != "rejected_unsupported_claim":
                rejected_count += 1

    # ── 5. Aggregate metrics ──────────────────────────────────────────────
    average_sq_score = sum(sq_scores) / len(sq_scores) if sq_scores else 0.0
    average_ec_score = sum(ec_scores) / len(ec_scores) if ec_scores else 0.0
    production_ready_ratio = accepted_count / scored_count if scored_count > 0 else 0.0

    unsupported_claims_count = sum(
        1 for c in structured_claims
        if c.get("support_status") in ("unsupported", "insufficient_evidence")
    )

    evidence_validation_metrics: dict[str, Any] = {
        "evidence_items_count": evidence_items_count,
        "scored_evidence_count": scored_count,
        "accepted_evidence_count": accepted_count,
        "rejected_evidence_count": rejected_count,
        "low_source_quality_count": low_sq_count,
        "low_evidence_confidence_count": low_ec_count,
        "claims_count": claims_count,
        "supported_claims_count": supported_claims_count,
        "unsupported_claims_count": unsupported_claims_count,
        "unsupported_critical_claims_count": unsupported_critical_claims_count,
        "average_source_quality_score": round(average_sq_score, 4),
        "average_evidence_confidence_score": round(average_ec_score, 4),
        "production_ready_evidence_ratio": round(production_ready_ratio, 4),
    }

    # ── 6. Determine overall status ────────────────────────────────────────
    failed_checks: list[str] = []
    warning_checks: list[str] = list(missing_optional)

    if unsupported_critical_claims_count > 0:
        failed_checks.append("unsupported_critical_claims_count > 0")
    if evidence_items_count == 0:
        warning_checks.append("evidence_items_count == 0")
    if claims_count == 0:
        warning_checks.append("claims_count == 0")
    if accepted_count == 0 and evidence_items_count > 0:
        warning_checks.append("no evidence items accepted — all rejected or need review")

    blockers = list(state.get("blockers", []))

    if unsupported_critical_claims_count > 0:
        validation_status = "failed"
        top_status = "evidence_validation_failed"
        msg = (
            f"validate_evidence: {unsupported_critical_claims_count}"
            " critical claim(s) without supported evidence"
        )
        if msg not in blockers:
            blockers.append(msg)
        review_required = False
    elif evidence_items_count == 0 or claims_count == 0:
        validation_status = "needs_review"
        top_status = "evidence_needs_review"
        review_required = True
    elif missing_optional:
        validation_status = "needs_review"
        top_status = "evidence_needs_review"
        msg = (
            "validate_evidence: optional calibration decisions missing — "
            "cannot determine sufficient acceptance threshold"
        )
        if msg not in blockers:
            blockers.append(msg)
        review_required = True
    elif accepted_count == 0:
        validation_status = "needs_review"
        top_status = "evidence_needs_review"
        msg = "validate_evidence: no evidence items accepted"
        if msg not in blockers:
            blockers.append(msg)
        review_required = True
    else:
        validation_status = "passed"
        top_status = "evidence_validation_passed"
        review_required = False

    evidence_validation: dict[str, Any] = {
        "status": validation_status,
        "metrics": dict(evidence_validation_metrics),
        "failed_checks": failed_checks,
        "warning_checks": warning_checks,
        "thresholds": {
            "source_quality_score_production_min": sq_threshold,
            "evidence_confidence_score_production_min": ec_threshold,
        },
    }

    updates: dict[str, Any] = {
        "status": top_status,
        "claims": structured_claims,
        "evidence_items": normalized_items,
        "validated_evidence": validated_evidence,
        "unsupported_critical_claims_count": unsupported_critical_claims_count,
        "evidence_validation": evidence_validation,
        "evidence_validation_metrics": evidence_validation_metrics,
        "accepted_evidence_items": accepted_items,
        "rejected_evidence_items": rejected_items,
        "review_required": review_required,
        "executed_nodes": _append_node(state, "validate_evidence"),
        "blockers": blockers,
    }

    if errors:
        existing = list(state.get("blockers", []))
        for e in errors:
            if e not in existing:
                updates.setdefault("blockers", existing)[:] = existing + [
                    e for e in errors if e not in existing
                ]

    return updates


def _score_startup(
    state: StartupRadarState,
    *,
    _score_service: Any = None,
) -> dict[str, Any]:
    from src.quality.decision_calibration_registry import (
        get_project_decision_inventory,
    )
    from src.scoring.startup_scoring import (
        compute_startup_scoring,
        build_scoring_summary,
    )

    run_id = state.get("run_id", "unknown")
    blockers: list[str] = list(state.get("blockers", []))
    unsupported_critical_claims_count = state.get("unsupported_critical_claims_count", 0)

    claims = state.get("claims", [])
    accepted_evidence_items = state.get("accepted_evidence_items", [])
    rejected_evidence_items = state.get("rejected_evidence_items", [])
    evidence_items = state.get("evidence_items", [])
    rag_contexts = state.get("rag_contexts", [])
    ev_metrics = state.get("evidence_validation_metrics", {})

    inventory = get_project_decision_inventory()

    # ── 1. Compute startup scoring (ai_native_score + nvidia_fit_score) ──
    score_result = compute_startup_scoring(
        claims=claims,
        accepted_evidence_items=accepted_evidence_items,
        evidence_items=evidence_items,
        unsupported_critical_claims_count=unsupported_critical_claims_count,
        rag_contexts=rag_contexts,
        inventory=inventory,
    )

    accepted_evidence_count = len(accepted_evidence_items)
    rejected_evidence_count = len(rejected_evidence_items)
    accepted_claim_count = sum(
        1 for c in claims if isinstance(c, dict) and c.get("support_status") == "supported"
    )
    average_evidence_confidence = ev_metrics.get("average_evidence_confidence_score", 0.0)
    average_source_quality = ev_metrics.get("average_source_quality_score", 0.0)

    summary = build_scoring_summary(
        result=score_result,
        unsupported_critical_claims_count=unsupported_critical_claims_count,
        accepted_evidence_count=accepted_evidence_count,
        rejected_evidence_count=rejected_evidence_count,
        accepted_claim_count=accepted_claim_count,
        average_evidence_confidence=average_evidence_confidence,
        average_source_quality=average_source_quality,
    )

    # ── 2. Determine status ─────────────────────────────────────────────
    scoring_status = summary.scoring_status

    if scoring_status == "failed":
        status_val = "startup_scoring_failed"
        review_required = False
        msg = f"score_startup: {summary.score_metrics['unsupported_critical_claims_count']} critical claim(s) without supported evidence"
        if msg not in blockers:
            blockers.append(msg)
    elif scoring_status == "blocked_uncalibrated_scoring":
        status_val = "startup_scoring_blocked"
        review_required = True
        for b in summary.blockers:
            if b not in blockers:
                blockers.append(b)
    elif scoring_status == "passed":
        status_val = "startup_scored"
        review_required = False
    else:
        status_val = "startup_scoring_needs_review"
        review_required = True

    # ── 3. Build scores dict ─────────────────────────────────────────────
    scores: dict[str, float] = dict(state.get("scores", {}))
    scores["ai_native_score"] = summary.ai_native_score
    scores["nvidia_fit_score"] = summary.nvidia_fit_score

    # ── 4. Call legacy classifier for backward compatibility ────────────
    legacy_errors: list[str] = []
    try:
        svc = _score_service
        if svc is None:
            from src.agents.classifier_agent import score_startup as svc
        profile_dict = state.get("startup_profile")
        validated_evidence_dicts = state.get("validated_evidence", [])
        (legacy_scores, classification_result, defensibility_result,
         inception_fit_result, production_readiness_result,
         legacy_errors) = svc(profile_dict, validated_evidence_dicts, run_id)
        scores.update(legacy_scores)
    except Exception as exc:
        legacy_errors = [f"Legacy classifier error: {type(exc).__name__}"]
        classification_result = {}
        defensibility_result = {}
        inception_fit_result = {}
        production_readiness_result = {}

    for err in legacy_errors:
        if err not in blockers:
            blockers.append(err)

    updates: dict[str, Any] = {
        "status": status_val,
        "scores": scores,
        "classification_result": classification_result,
        "defensibility_result": defensibility_result,
        "inception_fit_result": inception_fit_result,
        "production_readiness_result": production_readiness_result,
        "startup_scoring_summary": summary.model_dump(mode="json"),
        "review_required": review_required,
        "executed_nodes": _append_node(state, "score_startup"),
    }
    if blockers:
        updates["blockers"] = blockers
    return updates


def _diagnose_gaps(
    state: StartupRadarState,
    *,
    _gaps_service: Any = None,
) -> dict[str, Any]:
    svc = _gaps_service
    if svc is None:
        from src.agents.recommendation_agent import diagnose_gaps as svc

    startup_name = state.get("startup_name") or "Unknown"
    profile_raw = state.get("startup_profile")
    validated_evidence_dicts = state.get("validated_evidence", [])
    classification_raw = state.get("classification_result")
    defensibility_raw = state.get("defensibility_result")
    inception_fit_raw = state.get("inception_fit_result")
    production_readiness_raw = state.get("production_readiness_result")

    gaps, gap_diagnosis, errors = svc(
        startup_name,
        profile_raw,
        validated_evidence_dicts,
        classification_raw,
        defensibility_raw,
        inception_fit_raw,
        production_readiness_raw,
    )

    # ── Quantitative gap diagnosis ──────────────────────────────────────
    from src.diagnosis.gap_diagnosis_scoring import diagnose_gaps_quantitative

    run_id = state.get("run_id", "")
    evidence_items = state.get("evidence_items", [])
    accepted_evidence_items = state.get("accepted_evidence_items", [])
    rejected_evidence_items = state.get("rejected_evidence_items", [])
    claims = state.get("claims", [])
    evidence_validation = state.get("evidence_validation")
    ai_native_score = state.get("scores", {}).get("ai_native_score")
    nvidia_fit_score = state.get("scores", {}).get("nvidia_fit_score")
    scoring_metrics = state.get("startup_scoring_summary", {}).get("score_metrics")
    collection_metrics = state.get("collection_metrics")
    extraction_metrics = state.get("extraction_metrics")

    q_summary = diagnose_gaps_quantitative(
        run_id=run_id,
        startup_id=state.get("startup_id"),
        startup_profile=profile_raw,
        evidence_items=evidence_items,
        accepted_evidence_items=accepted_evidence_items,
        rejected_evidence_items=rejected_evidence_items,
        claims=claims,
        evidence_validation=evidence_validation,
        ai_native_score=ai_native_score,
        nvidia_fit_score=nvidia_fit_score,
        scoring_metrics=scoring_metrics,
        collection_metrics=collection_metrics,
        extraction_metrics=extraction_metrics,
    )

    updates: dict[str, Any] = {
        "status": "gaps_diagnosed",
        "gaps": gaps,
        "gap_diagnosis": gap_diagnosis,
        "gap_diagnosis_summary": q_summary.model_dump(mode="json"),
        "gap_diagnosis_status": q_summary.gap_diagnosis_status.value,
        "gap_diagnosis_metrics": (
            q_summary.metrics.model_dump(mode="json") if q_summary.metrics else None
        ),
        "executed_nodes": _append_node(state, "diagnose_gaps"),
    }
    if errors:
        updates["blockers"] = list(state.get("blockers", [])) + errors
    return updates


def _resolve_retriever_strategy() -> tuple[str | None, dict[str, Any] | None, list[str]]:
    """Read ``rag.retriever_strategy`` from the Decision Calibration Registry.

    Returns
    -------
    tuple[str | None, dict[str, Any] | None, list[str]]
        (strategy, ragas_eval_reference, blockers).
        *strategy* is ``None`` when production is blocked.
        *ragas_eval_reference* is a snapshot of the registry record.
        *blockers* explains why production is blocked.
    """
    from src.quality.decision_calibration_registry import (
        get_project_decision_inventory,
        validate_decision_for_production,
    )

    inventory = get_project_decision_inventory()
    blockers: list[str] = []
    strategy: str | None = None
    ragas_ref: dict[str, Any] | None = None

    for rec in inventory:
        if rec.decision_id == "rag.retriever_strategy":
            validation = validate_decision_for_production(rec)
            if not validation.passed:
                blockers.append(
                    f"RAG retriever strategy blocked: {'; '.join(validation.reasons)}"
                )
            elif not rec.production_allowed or rec.calibration_status.value in ("uncalibrated", "blocked"):
                blockers.append(
                    f"RAG retriever strategy '{rec.current_value}' is "
                    f"{rec.calibration_status.value} (production_allowed={rec.production_allowed})"
                )
            else:
                raw = rec.current_value
                strategy = str(raw) if raw is not None else None
                ragas_ref = {
                    "decision_id": rec.decision_id,
                    "current_value": rec.current_value,
                    "calibration_status": rec.calibration_status.value,
                    "calibration_method": rec.calibration_method.value if rec.calibration_method else None,
                    "evidence_source": rec.evidence_source,
                    "production_allowed": rec.production_allowed,
                }
            break

    if strategy is None and not blockers:
        blockers.append(
            "rag.retriever_strategy not found in Decision Calibration Registry"
        )

    return strategy, ragas_ref, blockers


def _validate_hybrid_weights() -> tuple[dict[str, Any] | None, list[str]]:
    """Validate that ``rag.hybrid_retrieval_weights`` is production-ready.

    Returns
    -------
    tuple[dict[str, Any] | None, list[str]]
        (weights_dict, blockers). *weights_dict* is ``None`` when blocked.
    """
    from src.quality.decision_calibration_registry import (
        get_project_decision_inventory,
        validate_decision_for_production,
    )

    inventory = get_project_decision_inventory()
    blockers: list[str] = []

    for rec in inventory:
        if rec.decision_id == "rag.hybrid_retrieval_weights":
            validation = validate_decision_for_production(rec)
            if not validation.passed:
                blockers.append(
                    f"Hybrid weights blocked: {'; '.join(validation.reasons)}"
                )
            elif not rec.production_allowed:
                blockers.append(
                    f"rag.hybrid_retrieval_weights is {rec.calibration_status.value} "
                    f"(production_allowed={rec.production_allowed})"
                )
            else:
                weights = rec.current_value
                if isinstance(weights, dict):
                    return weights, []
                blockers.append(
                    f"rag.hybrid_retrieval_weights has unexpected type: {type(weights).__name__}"
                )
            break

    if not blockers:
        blockers.append(
            "rag.hybrid_retrieval_weights not found in Decision Calibration Registry"
        )
    return None, blockers


def _blocked_rag_result(
    status_key: str,
    blockers: list[str],
    *,
    strategy: str | None = None,
    ragas_ref: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a blocked/failed RAG result dict."""
    rag_retrieval_status = status_key
    top_status = f"rag_{status_key}"
    return {
        "rag_queries_by_gap": {},
        "rag_contexts": [],
        "rag_contexts_by_gap": {},
        "rag_retrieval_status": rag_retrieval_status,
        "rag_retrieval_metrics": _empty_rag_metrics(),
        "rag_metrics": {
            "query_count": 0,
            "retrieved_context_count": 0,
            "min_required_contexts": 0,
            "retrieval_status": rag_retrieval_status,
            "rag_required": True,
        },
        "selected_retriever_strategy": strategy or "",
        "ragas_eval_reference": ragas_ref,
        "status": top_status,
        "review_required": True,
        "blockers": blockers,
    }


def _retrieve_nvidia_context(
    state: StartupRadarState,
    *,
    _rag_service: Any = None,
) -> dict[str, Any]:
    svc = _rag_service
    resolved_strategy: str | None = None
    resolved_ragas_ref: dict[str, Any] | None = None

    if svc is None:
        strategy, ragas_ref, blockers = _resolve_retriever_strategy()
        resolved_strategy = strategy
        resolved_ragas_ref = ragas_ref

        if blockers:
            return _blocked_rag_result(
                "blocked_missing_ragas_eval",
                blockers,
                strategy=resolved_strategy,
                ragas_ref=resolved_ragas_ref,
            )

        # lexical_baseline is never allowed in production
        if strategy == "lexical_baseline":
            return _blocked_rag_result(
                "blocked_lexical_winner_not_productive",
                ["lexical_baseline venceu a avaliação RAGAS mas não pode ser "
                 "retriever produtivo — bloquear produção para revisão manual"],
                strategy=strategy,
                ragas_ref=ragas_ref,
            )

        # semantic_qdrant → QdrantRagService
        if strategy == "semantic_qdrant":
            from src.rag.rag_service_factory import QdrantRagService

            svc = QdrantRagService()

        # hybrid_qdrant → validate weights, then build hybrid service
        if strategy == "hybrid_qdrant":
            weights, weight_blockers = _validate_hybrid_weights()
            if weight_blockers:
                return _blocked_rag_result(
                    "blocked_uncalibrated_hybrid",
                    weight_blockers,
                    strategy=strategy,
                    ragas_ref=ragas_ref,
                )
            from src.rag.rag_service_factory import QdrantRagService

            svc = QdrantRagService()

    run_id = state.get("run_id", "unknown")
    gap_diagnosis_summary = state.get("gap_diagnosis_summary")
    startup_profile = state.get("startup_profile")
    accepted_evidence_items = state.get("accepted_evidence_items", [])
    claims = state.get("claims", [])
    scores = state.get("scores", {})
    ai_native_score = scores.get("ai_native_score")
    nvidia_fit_score = scores.get("nvidia_fit_score")

    try:
        result_raw = svc(
            run_id=run_id,
            gap_diagnosis_summary=gap_diagnosis_summary,
            startup_profile=startup_profile,
            accepted_evidence_items=accepted_evidence_items,
            claims=claims,
            ai_native_score=ai_native_score,
            nvidia_fit_score=nvidia_fit_score,
        )
    except Exception as exc:
        result = {
            "rag_queries_by_gap": {},
            "rag_contexts": [],
            "rag_contexts_by_gap": {},
            "rag_retrieval_status": "failed",
            "rag_retrieval_metrics": _empty_rag_metrics(),
            "status": "rag_failed",
            "review_required": False,
            "blockers": [f"RAG service error: {type(exc).__name__}"],
            "selected_retriever_strategy": resolved_strategy or "",
            "ragas_eval_reference": resolved_ragas_ref,
        }
    else:
        result = _normalize_rag_result(result_raw)
        result["selected_retriever_strategy"] = resolved_strategy or ""
        result["ragas_eval_reference"] = resolved_ragas_ref

    blockers = list(state.get("blockers", []))
    result_blockers = result.get("blockers")
    if result_blockers:
        if isinstance(result_blockers, list):
            for b in result_blockers:
                if b not in blockers:
                    blockers.append(b)
        else:
            b = str(result_blockers)
            if b not in blockers:
                blockers.append(b)

    updates: dict[str, Any] = {
        "status": result.get("status", "rag_failed"),
        "rag_contexts": result.get("rag_contexts", []),
        "rag_queries_by_gap": result.get("rag_queries_by_gap", {}),
        "rag_contexts_by_gap": result.get("rag_contexts_by_gap", {}),
        "rag_retrieval_status": result.get("rag_retrieval_status", "failed"),
        "selected_retriever_strategy": result.get("selected_retriever_strategy", ""),
        "ragas_eval_reference": result.get("ragas_eval_reference"),
        "rag_retrieval_metrics": result.get("rag_retrieval_metrics", _empty_rag_metrics()),
        "rag_metrics": result.get("rag_metrics", {
            "query_count": 0,
            "retrieved_context_count": 0,
            "min_required_contexts": 0,
            "retrieval_status": result.get("rag_retrieval_status", "failed"),
            "rag_required": True,
        }),
        "review_required": result.get("review_required", False),
        "executed_nodes": _append_node(state, "retrieve_nvidia_context"),
    }
    if blockers:
        updates["blockers"] = blockers
    return updates


def _normalize_rag_result(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    if isinstance(result, (list, tuple)) and len(result) == 2:
        ctxs, errors = result
        retrieval_status = "failed" if errors else ("passed" if ctxs else "needs_review")
        return {
            "rag_queries_by_gap": {},
            "rag_contexts": list(ctxs) if isinstance(ctxs, (list, tuple)) else [],
            "rag_contexts_by_gap": {},
            "rag_retrieval_status": retrieval_status,
            "rag_retrieval_metrics": _empty_rag_metrics(),
            "rag_metrics": {
                "query_count": 1,
                "retrieved_context_count": len(ctxs) if isinstance(ctxs, (list, tuple)) else 0,
                "min_required_contexts": 1,
                "retrieval_status": retrieval_status,
                "rag_required": True,
            },
            "status": f"rag_{retrieval_status}" if retrieval_status != "passed" else "nvidia_context_retrieved",
            "review_required": retrieval_status in ("needs_review", "failed"),
            "blockers": list(errors) if errors else None,
        }
    return {
        "rag_queries_by_gap": {},
        "rag_contexts": [],
        "rag_contexts_by_gap": {},
        "rag_retrieval_status": "failed",
        "rag_retrieval_metrics": _empty_rag_metrics(),
        "status": "rag_failed",
        "review_required": False,
        "blockers": [f"Unexpected RAG result type: {type(result).__name__}"],
    }


def _empty_rag_metrics() -> dict[str, Any]:
    return {
        "gap_count": 0,
        "calibrated_gap_count": 0,
        "query_count": 0,
        "retrieved_context_count": 0,
        "context_count_by_gap": {},
        "gaps_with_min_contexts_count": 0,
        "gaps_without_context_count": 0,
        "average_retrieval_score": 0.0,
        "average_relevance_score": 0.0,
        "citation_ready_context_count": 0,
        "missing_rag_calibration_count": 0,
        "rag_blocker_count": 0,
    }


def _build_technology_mappings(state: StartupRadarState) -> dict[str, Any]:
    """Build NVIDIA technology mappings from RAG contexts and gap results."""
    from src.recommendation.nvidia_technology_mapping import (
        build_nvidia_technology_mappings,
    )

    run_id = state.get("run_id", "unknown")
    rag_contexts_by_gap: dict[str, list[dict[str, Any]]] = state.get(
        "rag_contexts_by_gap", {}
    )
    gap_diagnosis_summary = state.get("gap_diagnosis_summary")
    gap_diagnosis_metrics = state.get("gap_diagnosis_metrics")
    evidence_items: list[dict[str, Any]] = state.get("evidence_items", [])

    gap_results: list[Any] = []
    gap_metrics: Any = None
    if gap_diagnosis_summary and isinstance(gap_diagnosis_summary, dict):
        gap_results_raw = gap_diagnosis_summary.get("gaps", [])
        for g in gap_results_raw:
            if isinstance(g, dict):
                try:
                    from src.diagnosis.schemas import GapDiagnosisResultItem
                    item = GapDiagnosisResultItem.model_validate(g)
                    gap_results.append(item)
                except Exception:
                    pass
    if gap_diagnosis_metrics and isinstance(gap_diagnosis_metrics, dict):
        try:
            from src.diagnosis.schemas import GapDiagnosisMetrics
            gap_metrics = GapDiagnosisMetrics.model_validate(gap_diagnosis_metrics)
        except Exception:
            pass

    mapping_result = build_nvidia_technology_mappings(
        run_id=run_id,
        rag_contexts_by_gap=rag_contexts_by_gap,
        gap_results=gap_results,
        gap_metrics=gap_metrics,
        evidence_items=evidence_items,
    )

    state_blockers = list(state.get("blockers", []))
    mapping_blockers = mapping_result.get("blockers", [])
    if isinstance(mapping_blockers, list):
        for b in mapping_blockers:
            if b not in state_blockers:
                state_blockers.append(b)

    return {
        "nvidia_technology_mappings": mapping_result.get("nvidia_technology_mappings", []),
        "nvidia_mapping_metrics": mapping_result.get("nvidia_mapping_metrics", {}),
        "nvidia_mapping_calibration_metrics": mapping_result.get(
            "nvidia_mapping_calibration_metrics", {}
        ),
        "nvidia_mapping_summary": {
            "mapping_status": mapping_result.get("mapping_status", "failed"),
            "production_allowed": mapping_result.get("production_allowed", False),
            "blockers": mapping_result.get("blockers", []),
        },
        "status": "technology_mappings_built",
        "blockers": state_blockers,
        "executed_nodes": _append_node(state, "build_technology_mappings"),
    }


# ── gap → technology / impact / complexity mappings ──────────────────────
# Fallback defaults used when RAG context is unavailable.
# TODO: Replace with RAG vector store queries once full RAG integration
#       is complete. src/diagnosis/nvidia_mapping.py has the canonical mapping.

_GAP_TECH_MAP: dict[str, str] = {
    "external_api_dependency": "NVIDIA NIM",
    "high_inference_cost": "TensorRT-LLM",
    "high_latency": "Triton Inference Server",
    "slow_data_pipeline": "cuDF",
    "heavy_tabular_processing": "cuML",
    "computer_vision_need": "NVIDIA TensorRT",
    "voice_need": "NVIDIA Riva",
    "agent_governance_gap": "NeMo Guardrails",
    "privacy_or_controlled_deployment_gap": "NVIDIA AI Enterprise",
    "ai_cybersecurity_need": "NVIDIA Morpheus",
    "healthcare_compliance_need": "MONAI",
    "robotics_need": "NVIDIA Isaac",
    "simulation_need": "NVIDIA Omniverse",
    "model_evaluation_gap": "NVIDIA NeMo",
    "observability_gap": "NVIDIA AI Enterprise",
}

_GAP_IMPACT_MAP: dict[str, float] = GAP_BUSINESS_IMPACT_MAP

_TECH_COMPLEXITY_MAP: dict[str, float] = {
    "NVIDIA NIM": 0.0,
    "cuDF": 0.0,
    "cuML": 0.0,
    "TensorRT-LLM": 0.5,
    "Triton Inference Server": 0.5,
    "NVIDIA RAPIDS": 0.5,
    "NVIDIA Riva": 0.5,
    "NVIDIA NeMo": 0.5,
    "NeMo Guardrails": 0.5,
    "NVIDIA TensorRT": 0.5,
    "MONAI": 0.5,
    "NVIDIA Omniverse": 1.0,
    "NVIDIA Isaac": 1.0,
    "NVIDIA Clara": 1.0,
    "NVIDIA Morpheus": 1.0,
    "NVIDIA AI Enterprise": 1.0,
}


def _compute_priority_score(
    confidence: float,
    business_impact: float,
    implementation_complexity: float,
    rag_support: float,
    evidence_support: float,
) -> float:
    return (
        PRIORITY_SCORE_WEIGHTS["confidence"] * confidence
        + PRIORITY_SCORE_WEIGHTS["business_impact"] * business_impact
        + PRIORITY_SCORE_WEIGHTS["implementation_complexity_inverse"]
        * max(0.0, 1.0 - implementation_complexity)
        + PRIORITY_SCORE_WEIGHTS["rag_support"] * rag_support
        + PRIORITY_SCORE_WEIGHTS["evidence_support"] * evidence_support
    )


def _get_tech_for_gap(gap_name: str) -> str:
    return _GAP_TECH_MAP.get(gap_name, "NVIDIA AI Enterprise")


def _get_impact_for_gap(gap_name: str) -> float:
    return _GAP_IMPACT_MAP.get(gap_name, 0.5)


def _get_complexity_numeric(tech_name: str) -> float:
    return _TECH_COMPLEXITY_MAP.get(tech_name, 0.5)


def _build_rec_from_gap(
    gap: str,
    claims: list[dict[str, Any]],
    rag_contexts: list[str],
    evidence_items: list[dict[str, Any]],
    rec_strings: list[str],
) -> dict[str, Any]:
    tech = _get_tech_for_gap(gap)
    reason = gap
    for rs in rec_strings:
        if gap in rs:
            reason = rs
            break
    rag_ids = [f"rag_{i}" for i in range(len(rag_contexts))]
    ev_ids = []
    for i, item in enumerate(evidence_items):
        if isinstance(item, dict):
            ev_ids.append(item.get("id", f"ev_{i}"))
        else:
            ev_ids.append(f"ev_{i}")
    gap_keywords = gap.replace("_", " ").lower()
    gap_claims = [
        c
        for c in claims
        if isinstance(c, dict) and gap_keywords in c.get("claim_text", "").lower()
    ]
    if gap_claims:
        supported = sum(1 for c in gap_claims if c.get("support_status") == "supported")
        confidence = supported / len(gap_claims)
    else:
        confidence = 0.5
    business_impact = _get_impact_for_gap(gap)
    complexity = _get_complexity_numeric(tech)
    if rag_contexts:
        matching_rag = sum(
            1 for ctx in rag_contexts if isinstance(ctx, str) and gap_keywords in ctx.lower()
        )
        rag_support = matching_rag / len(rag_contexts)
    else:
        rag_support = 0.0
    total_valid = [c for c in claims if isinstance(c, dict)]
    if total_valid:
        supported = sum(1 for c in total_valid if c.get("support_status") == "supported")
        evidence_support = supported / len(total_valid)
    else:
        evidence_support = 0.0
    priority_score = _compute_priority_score(
        confidence=confidence,
        business_impact=business_impact,
        implementation_complexity=complexity,
        rag_support=rag_support,
        evidence_support=evidence_support,
    )
    if confidence >= 0.7:
        next_action = f"Recommend {tech} to address {gap.replace('_', ' ')}"
    else:
        next_action = f"Gather more evidence on {gap.replace('_', ' ')} before recommending {tech}"
    return {
        "technology_name": tech,
        "recommendation_type": "technology_adoption",
        "reason": reason,
        "supporting_rag_context_ids": rag_ids,
        "supporting_evidence_ids": ev_ids,
        "confidence": round(confidence, 4),
        "business_impact": round(business_impact, 4),
        "implementation_complexity": round(complexity, 4),
        "priority_score": round(priority_score, 4),
        "next_best_action": next_action,
    }


def _build_rec_from_string(
    s: str,
    rag_contexts: list[str],
    evidence_items: list[dict[str, Any]],
) -> dict[str, Any]:
    rag_ids = [f"rag_{i}" for i in range(len(rag_contexts))]
    ev_ids = (
        [item.get("id", f"ev_{i}") for i, item in enumerate(evidence_items)]
        if evidence_items else []
    )
    ev_qualities = [
        item.get("source_quality_score", 0.5)
        for item in evidence_items
        if isinstance(item.get("source_quality_score"), (int, float))
    ]
    avg_quality = sum(ev_qualities) / len(ev_qualities) if ev_qualities else 0.5
    confidence = round(avg_quality, 2)
    business_impact = round(0.3 + 0.4 * (1.0 if rag_contexts else 0.0) + 0.3 * avg_quality, 2)
    priority_score = _compute_priority_score(
        confidence=confidence,
        business_impact=business_impact,
        implementation_complexity=0.5,
        rag_support=0.5 if rag_contexts else 0.0,
        evidence_support=avg_quality if evidence_items else 0.0,
    )
    return {
        "technology_name": "NVIDIA AI Enterprise",
        "recommendation_type": "technology_adoption",
        "reason": s,
        "supporting_rag_context_ids": rag_ids,
        "supporting_evidence_ids": ev_ids,
        "confidence": confidence,
        "business_impact": business_impact,
        "implementation_complexity": 0.5,
        "priority_score": round(priority_score, 4),
        "next_best_action": "Evaluate startup for NVIDIA technology adoption opportunities",
    }


def _build_structured_recommendations(
    gaps: list[str],
    claims: list[dict[str, Any]],
    rag_contexts: list[str],
    evidence_items: list[dict[str, Any]],
    rec_strings: list[str],
) -> list[dict[str, Any]]:
    if gaps:
        return [_build_rec_from_gap(gap, claims, rag_contexts, evidence_items, rec_strings) for gap in gaps]
    return [_build_rec_from_string(s, rag_contexts, evidence_items) for s in rec_strings]


def _rank_recommendations(
    state: StartupRadarState,
    *,
    _recommendations_service: Any = None,
) -> dict[str, Any]:
    from src.recommendation.recommendation_engine import (
        rank_recommendations_from_mappings,
    )

    run_id = state.get("run_id", "unknown")
    unsupported_critical_claims_count = state.get("unsupported_critical_claims_count", 0)
    blockers = list(state.get("blockers", []))

    # ── 1. Check critical claims ─────────────────────────────────────────
    if unsupported_critical_claims_count > 0:
        msg = (
            f"rank_recommendations: {unsupported_critical_claims_count}"
            " critical claim(s) without supported evidence"
        )
        if msg not in blockers:
            blockers.append(msg)
        return {
            "status": "recommendation_failed",
            "recommendations": [],
            "recommendation_metrics": {
                "recommendation_count": 0,
                "ranking_status": "failed",
                "unsupported_critical_claims_count": unsupported_critical_claims_count,
            },
            "nvidia_recommendations": [],
            "nvidia_recommendation_metrics": {},
            "nvidia_recommendation_summary": None,
            "blockers": blockers,
            "review_required": False,
            "executed_nodes": _append_node(state, "rank_recommendations"),
        }

    # ── 2. Get mappings from state ───────────────────────────────────────
    nvidia_technology_mappings: list[dict[str, Any]] = state.get(
        "nvidia_technology_mappings", []
    )
    nvidia_mapping_summary = state.get("nvidia_mapping_summary") or {}
    mapping_status: str = ""

    if isinstance(nvidia_mapping_summary, dict):
        mapping_status = nvidia_mapping_summary.get("mapping_status", "")

    # ── 3. Run rank_recommendations_from_mappings ────────────────────────
    result = rank_recommendations_from_mappings(
        run_id=run_id,
        nvidia_technology_mappings=nvidia_technology_mappings,
        mapping_status=mapping_status,
    )

    nvidia_recommendations = result.get("nvidia_recommendations", [])
    nvidia_recommendation_metrics = result.get("nvidia_recommendation_metrics", {})
    ranking_status = result.get("ranking_status", "failed")
    ranking_production_allowed = result.get("production_allowed", False)
    result_blockers = result.get("blockers", [])

    for b in result_blockers:
        if b not in blockers:
            blockers.append(b)

    # ── 4. Determine status ──────────────────────────────────────────────
    top_status: str
    review_required: bool

    if ranking_status in (
        "blocked_no_nvidia_mappings",
        "blocked_uncalibrated_mapping",
        "blocked_uncalibrated_recommendation",
        "failed",
    ):
        top_status = f"recommendation_{ranking_status}"
        review_required = ranking_status not in ("failed",)
    elif ranking_status == "needs_review":
        top_status = "recommendation_needs_review"
        review_required = True
    elif ranking_status == "passed":
        top_status = "recommendations_ranked"
        review_required = False
    else:
        top_status = "recommendation_needs_review"
        review_required = True

    recommendation_count = len(nvidia_recommendations)
    rag_contexts = state.get("rag_contexts", [])

    recommendation_metrics: dict[str, Any] = {
        "recommendation_count": recommendation_count,
        "rag_contexts_count": len(rag_contexts),
        "ranking_status": ranking_status,
        "production_allowed": ranking_production_allowed,
    }

    # ── 5. Build backward-compatible recommendations list ────────────────
    recommendations: list[dict[str, Any]] = []
    for rec in nvidia_recommendations:
        if isinstance(rec, dict):
            recommendations.append({
                "technology_name": rec.get("nvidia_technology", ""),
                "reason": rec.get("reason", ""),
                "priority_score": rec.get("recommendation_priority_score", 0.0),
                "confidence": rec.get("confidence", 0.0),
                "next_best_action": rec.get("next_best_action", ""),
                "supporting_rag_context_ids": rec.get("supporting_rag_context_ids", []),
                "supporting_evidence_ids": rec.get("supporting_evidence_ids", []),
            })

    updates: dict[str, Any] = {
        "status": top_status,
        "recommendations": recommendations,
        "recommendation_metrics": recommendation_metrics,
        "nvidia_recommendations": nvidia_recommendations,
        "nvidia_recommendation_metrics": nvidia_recommendation_metrics,
        "nvidia_recommendation_summary": {
            "ranking_status": ranking_status,
            "production_allowed": ranking_production_allowed,
            "recommendation_count": recommendation_count,
        },
        "ranking_status": ranking_status,
        "recommendation_production_allowed": ranking_production_allowed,
        "review_required": review_required,
        "executed_nodes": _append_node(state, "rank_recommendations"),
    }
    if blockers:
        updates["blockers"] = blockers
    return updates


def _generate_brief(
    state: StartupRadarState,
    *,
    _brief_service: Any = None,
) -> dict[str, Any]:
    from src.briefing.quantitative_brief import build_quantitative_brief

    result = build_quantitative_brief(dict(state))
    new_executed = _append_node(state, "generate_brief")

    action_brief = dict(result.get("action_brief", {}))
    audit_trail = dict(action_brief.get("audit_trail", {}))
    audit_trail["executed_nodes"] = list(new_executed)
    action_brief["audit_trail"] = audit_trail

    updates: dict[str, Any] = {
        "status": result["status"],
        "action_brief": action_brief,
        "brief_metrics": result["brief_metrics"],
        "brief_status": result["brief_status"],
        "startup_brief": result.get("startup_brief", ""),
        "review_required": result["review_required"],
        "executed_nodes": new_executed,
    }

    result_blockers = result.get("blockers", [])
    if result_blockers:
        updates["blockers"] = result_blockers

    return updates


def _run_quality_gates(state: StartupRadarState) -> dict[str, Any]:
    unsupported_critical_claims_count = state.get("unsupported_critical_claims_count", 0)
    blockers = list(state.get("blockers", []))

    # ── Consume sub-statuses ────────────────────────────────────────────
    ranking_status: str | None = None
    has_nvidia_recommendation_metrics = "nvidia_recommendation_metrics" in state
    has_nvidia_recommendations = "nvidia_recommendations" in state
    legacy_recommendations: list[Any] = state.get("recommendations", [])
    brief_metrics_for_quality: dict[str, Any] = state.get("brief_metrics", {})
    using_legacy_recommendations = (
        not has_nvidia_recommendation_metrics and not has_nvidia_recommendations
    )
    ranking_metrics: dict[str, Any] = state.get("nvidia_recommendation_metrics", {})
    if ranking_metrics:
        ranking_status = ranking_metrics.get("ranking_status") or (
            state.get("nvidia_recommendation_summary") or {}
        ).get("ranking_status")
    if ranking_status is None:
        ranking_status = state.get("ranking_status")
    if ranking_status is None and using_legacy_recommendations:
        ranking_status = "passed"

    gap_diagnosis_status: str | None = state.get("gap_diagnosis_status")
    gap_diagnosis_metrics: dict[str, Any] | None = state.get("gap_diagnosis_metrics")
    rag_retrieval_status: str | None = state.get("rag_retrieval_status")
    evidence_validation: dict[str, Any] | None = state.get("evidence_validation")

    scoring_summary: dict[str, Any] | None = state.get("startup_scoring_summary")
    scoring_status: str | None = scoring_summary.get("scoring_status") if scoring_summary else None

    mapping_summary: dict[str, Any] = state.get("nvidia_mapping_summary") or {}
    mapping_status_raw = (
        mapping_summary.get("mapping_status") if isinstance(mapping_summary, dict) else ""
    )
    mapping_status = str(mapping_status_raw or "")

    # ── Recommendation data ─────────────────────────────────────────────
    nvidia_recommendations: list[dict[str, Any]] = state.get("nvidia_recommendations", [])
    recommendation_count = (
        int(brief_metrics_for_quality.get("recommendation_count", 0) or 0)
        if using_legacy_recommendations and not legacy_recommendations
        else len(legacy_recommendations)
        if using_legacy_recommendations
        else len(nvidia_recommendations)
    )
    recs_not_production_allowed = sum(
        1 for r in nvidia_recommendations if not r.get("production_allowed", False)
    )
    recs_production_allowed = (
        recommendation_count
        if using_legacy_recommendations
        else recommendation_count - recs_not_production_allowed
    )

    calibration_blocker_count = sum(
        1 for r in nvidia_recommendations
        if not r.get("production_allowed", False)
        and any(
            kw in str(b).lower()
            for kw in ("calibrat", "uncalibrat", "not found")
            for b in r.get("blockers", [])
        )
    )

    # ── Gap metrics ─────────────────────────────────────────────────────
    total_gap_count = 0
    production_allowed_gap_count = 0
    blocked_gap_count = 0
    needs_more_evidence_gap_count = 0
    average_gap_severity = 0.0
    average_gap_confidence = 0.0
    average_gap_evidence_coverage = 0.0
    missing_gap_calibration_count = 0
    calibrated_gap_decision_count = 0
    gap_uncertainty_mean = 0.0

    if gap_diagnosis_metrics is not None:
        total_gap_count = gap_diagnosis_metrics.get("total_gap_count", 0)
        production_allowed_gap_count = gap_diagnosis_metrics.get("production_allowed_gap_count", 0)
        blocked_gap_count = gap_diagnosis_metrics.get("blocked_gap_count", 0)
        average_gap_severity = gap_diagnosis_metrics.get("average_gap_severity", 0.0)
        average_gap_confidence = gap_diagnosis_metrics.get("average_gap_confidence", 0.0)
        missing_gap_calibration_count = gap_diagnosis_metrics.get("missing_calibration_count", 0)
        calibrated_gap_decision_count = gap_diagnosis_metrics.get("calibrated_decision_count", 0)
        gap_uncertainty_mean = gap_diagnosis_metrics.get("gap_uncertainty_mean", 0.0)
        needs_more_evidence_gap_count = gap_diagnosis_metrics.get(
            "evidence_coverage_gap_count", 0
        )

    # ── Recommendation metrics ──────────────────────────────────────────
    rec_metrics = dict(ranking_metrics)

    # ── Build top-level quality metrics ─────────────────────────────────
    metrics: dict[str, Any] = {
        "unsupported_critical_claims_count": unsupported_critical_claims_count,
        "blockers_count": len(blockers),
        "evidence_items_count": len(state.get("evidence_items", [])),
        "rag_contexts_count": len(state.get("rag_contexts", [])),
        "recommendation_count": recommendation_count,
        "production_allowed_recommendation_count": recs_production_allowed,
        "blocked_recommendation_count": calibration_blocker_count,
        "needs_review_recommendation_count": recommendation_count - recs_production_allowed - calibration_blocker_count,
        "average_recommendation_priority_score": rec_metrics.get("average_recommendation_priority_score", 0.0),
        "average_recommendation_confidence": rec_metrics.get("average_recommendation_confidence", 0.0),
        "rag_supported_recommendation_rate": rec_metrics.get("rag_supported_recommendation_rate", 0.0),
        "evidence_supported_recommendation_rate": rec_metrics.get("evidence_supported_recommendation_rate", 0.0),
        "missing_recommendation_calibration_count": rec_metrics.get("missing_recommendation_calibration_count", 0),
        "total_gap_count": total_gap_count,
        "production_allowed_gap_count": production_allowed_gap_count,
        "blocked_gap_count": blocked_gap_count,
        "needs_more_evidence_gap_count": needs_more_evidence_gap_count,
        "average_gap_severity": average_gap_severity,
        "average_gap_confidence": average_gap_confidence,
        "average_gap_evidence_coverage": average_gap_evidence_coverage,
        "missing_gap_calibration_count": missing_gap_calibration_count,
        "calibrated_gap_decision_count": calibrated_gap_decision_count,
        "gap_uncertainty_mean": gap_uncertainty_mean,
        "ranking_status": ranking_status or "",
        "mapping_status": mapping_status,
        "scoring_status": scoring_status or "",
    }

    failed_checks: list[str] = []
    warning_checks: list[str] = []

    # ── Critical claims ─────────────────────────────────────────────────
    if unsupported_critical_claims_count > 0:
        failed_checks.append("unsupported_critical_claims_count > 0")

    # ── Blockers ────────────────────────────────────────────────────────
    if blockers:
        failed_checks.append("blockers_count > 0")

    if metrics["evidence_items_count"] == 0:
        warning_checks.append("evidence_items_count == 0")
    if metrics["rag_contexts_count"] == 0:
        warning_checks.append("rag_contexts_count == 0")
    if metrics["recommendation_count"] == 0:
        warning_checks.append("recommendation_count == 0")

    # ── Ranking status ──────────────────────────────────────────────────
    if ranking_status == "blocked_no_nvidia_mappings":
        failed_checks.append("ranking_status is blocked_no_nvidia_mappings")
    elif ranking_status == "blocked_uncalibrated_mapping":
        failed_checks.append("ranking_status is blocked_uncalibrated_mapping")
    elif ranking_status == "blocked_uncalibrated_recommendation":
        failed_checks.append("ranking_status is blocked_uncalibrated_recommendation")
    elif ranking_status == "failed":
        failed_checks.append("ranking_status is failed")
    elif ranking_status == "needs_review":
        warning_checks.append("ranking_status is needs_review")
    elif ranking_status is None:
        failed_checks.append("ranking_status is missing")

    # ── Any recommendation production_allowed=false ─────────────────────
    if recs_not_production_allowed > 0 and ranking_status in ("passed", "needs_review"):
        rec_blockers_detail = []
        for r in nvidia_recommendations:
            if not r.get("production_allowed", False):
                for b in r.get("blockers", []):
                    if b not in rec_blockers_detail:
                        rec_blockers_detail.append(b)
        for b in rec_blockers_detail:
            if "calibrat" in b.lower() or "uncalibrat" in b.lower():
                failed_checks.append(f"recommendation blocked by calibration: {b}")
            else:
                warning_checks.append(f"recommendation blocked: {b}")

    # ── Recommendation calibration missing ──────────────────────────────
    missing_cal = rec_metrics.get("missing_recommendation_calibration_count", 0)
    if missing_cal > 0:
        failed_checks.append(
            f"missing_recommendation_calibration_count is {missing_cal}"
        )

    # ── Evidence validation ─────────────────────────────────────────────
    evidence_status = evidence_validation.get("status") if evidence_validation else None
    if evidence_status == "failed":
        failed_checks.append(f"evidence_validation.status is {evidence_status}")
    elif evidence_status in ("needs_review", "blocked_uncalibrated_scoring"):
        warning_checks.append(f"evidence_validation.status is {evidence_status}")

    # ── Gap diagnosis ───────────────────────────────────────────────────
    if gap_diagnosis_status == "blocked_uncalibrated_gap_diagnosis":
        failed_checks.append(
            "gap_diagnosis_status is blocked_uncalibrated_gap_diagnosis"
        )
    elif gap_diagnosis_status and gap_diagnosis_status not in ("passed", None):
        failed_checks.append(f"gap_diagnosis_status is {gap_diagnosis_status}")

    if total_gap_count > 0 and production_allowed_gap_count < total_gap_count:
        failed_checks.append(
            f"not all gaps allow production "
            f"({production_allowed_gap_count}/{total_gap_count})"
        )
    if missing_gap_calibration_count > 0:
        failed_checks.append(
            f"missing_gap_calibration_count is {missing_gap_calibration_count}"
        )

    # ── RAG retrieval ───────────────────────────────────────────────────
    if rag_retrieval_status in ("blocked_uncalibrated_rag", "blocked_no_calibrated_gaps", "failed"):
        failed_checks.append(f"rag_retrieval_status is {rag_retrieval_status}")
    elif rag_retrieval_status == "needs_review":
        warning_checks.append(f"rag_retrieval_status is {rag_retrieval_status}")

    # ── Scoring ─────────────────────────────────────────────────────────
    if scoring_status == "failed":
        failed_checks.append(f"scoring_status is {scoring_status}")
    elif scoring_status == "blocked_uncalibrated_scoring":
        failed_checks.append(f"scoring_status is {scoring_status}")

    # ── Mapping ─────────────────────────────────────────────────────────
    if mapping_status == "blocked_uncalibrated_mapping":
        failed_checks.append(f"mapping_status is {mapping_status}")
    elif mapping_status == "failed":
        failed_checks.append(f"mapping_status is {mapping_status}")

    # ── Determine quality_status ───────────────────────────────────────
    quality_status: str
    review_required: bool
    top_status: str

    if failed_checks:
        has_calibration_block = any(
            "blocked_uncalibrated" in c or "missing" in c
            for c in failed_checks
        )
        has_rec_calibration_block = any(
            "blocked_uncalibrated_recommendation" in c
            or "missing_recommendation_calibration" in c
            for c in failed_checks
        )
        if has_rec_calibration_block:
            quality_status = "blocked_uncalibrated_recommendation"
            review_required = True
            top_status = "quality_blocked_uncalibrated_recommendation"
        elif has_calibration_block:
            quality_status = "blocked_uncalibrated_gap_diagnosis"
            review_required = True
            top_status = "quality_blocked_uncalibrated"
        else:
            quality_status = "failed"
            review_required = False
            top_status = "quality_failed"
    elif warning_checks:
        quality_status = "needs_review"
        review_required = True
        top_status = "needs_human_review"
    else:
        quality_status = "passed"
        review_required = False
        top_status = "quality_passed"

    quality: dict[str, Any] = {
        "status": quality_status,
        "failed_checks": failed_checks,
        "warning_checks": warning_checks,
        "metrics": metrics,
        "thresholds": {
            "unsupported_critical_claims_count": 0,
            "blockers_count": 0,
            "evidence_items_count": 1,
            "rag_contexts_count": 1,
            "recommendation_count": 1,
        },
    }

    return {
        "status": top_status,
        "quality": quality,
        "review_required": review_required,
        "executed_nodes": _append_node(state, "run_quality_gates"),
    }


def _route_after_quality_gates(state: StartupRadarState) -> str:
    quality: dict[str, Any] = state.get("quality") or {}
    quality_status = quality.get("status")
    if state.get("review_required") or quality_status in ("needs_review", "blocked_uncalibrated_gap_diagnosis"):
        return "needs_review"
    if quality_status == "failed":
        return "finish"
    return "finish"


def _route_after_rag(state: StartupRadarState) -> str:
    retrieval_status: str = state.get("rag_retrieval_status") or "needs_review"
    if retrieval_status == "passed":
        return "build_technology_mappings"
    return "needs_review"


def _route_after_mappings(state: StartupRadarState) -> str:
    mapping_summary = state.get("nvidia_mapping_summary")
    if mapping_summary and isinstance(mapping_summary, dict):
        status = mapping_summary.get("mapping_status", "failed")
        if status in ("passed", "needs_review", "needs_more_evidence"):
            return "rank_recommendations"
    return "needs_review"


def _needs_review(state: StartupRadarState) -> dict[str, Any]:
    quality: dict[str, Any] = state.get("quality") or {}
    blockers: list[str] = state.get("blockers", [])
    run_id: str = state.get("run_id", "unknown")
    startup_id: str | None = state.get("startup_id")

    quality_issues: list[str] = quality.get("issues", [])
    quality_checks: dict[str, Any] = quality.get("checks", {})

    if quality.get("status") == "needs_review":
        reason_parts: list[str] = []
        if quality_issues:
            reason_parts.extend(quality_issues)
        if blockers:
            reason_parts.append(f"Blockers: {'; '.join(blockers)}")
        reason: str = "; ".join(reason_parts) if reason_parts else "quality_gate_requested_human_review"
    elif blockers:
        reason = f"Pipeline blocked: {'; '.join(blockers)}"
    else:
        reason = "quality_gate_requested_human_review"

    failed_checks: list[str] = [k for k, v in quality_checks.items() if v is False]
    if not failed_checks:
        failed_checks = quality_issues[:]

    if blockers:
        severity: str = "high"
    elif quality_issues:
        severity = "medium"
    else:
        severity = "low"

    review_payload: dict[str, Any] = {
        "run_id": run_id,
        "startup_id": startup_id,
        "reason": reason,
        "severity": severity,
        "failed_quality_checks": failed_checks,
        "blockers": blockers,
        "expected_human_actions": ["approve", "reject", "request_more_evidence"],
        "resumable": True,
        "interrupt_enabled": True,
    }

    resume_value: Any = None
    if _CHECKPOINTER_ENABLED:
        resume_value = interrupt(review_payload)

    review_decision: str | None = state.get("review_decision")
    if review_decision is None:
        if isinstance(resume_value, str):
            review_decision = resume_value
        elif isinstance(resume_value, dict):
            raw_decision = resume_value.get("review_decision") or resume_value.get("decision")
            if isinstance(raw_decision, str):
                review_decision = raw_decision

    if review_decision == "approve":
        return {
            "status": "human_review_approved",
            "review_required": False,
            "review_decision": review_decision,
            "review_notes": state.get("review_notes", ""),
            "reviewed_by": state.get("reviewed_by", ""),
            "review_payload": review_payload,
            "executed_nodes": _append_node(state, "needs_review"),
        }
    if review_decision == "reject":
        reject_blockers: list[str] = list(state.get("blockers", []))
        reject_msg: str = "Human rejected"
        if reject_msg not in reject_blockers:
            reject_blockers.append(reject_msg)
        return {
            "status": "human_review_rejected",
            "review_required": False,
            "review_decision": review_decision,
            "blockers": reject_blockers,
            "review_notes": state.get("review_notes", ""),
            "reviewed_by": state.get("reviewed_by", ""),
            "review_payload": review_payload,
            "executed_nodes": _append_node(state, "needs_review"),
        }
    if review_decision == "request_more_evidence":
        current_retry = state.get("evidence_retry_count", 0)
        max_retries = state.get("max_evidence_retries", 3)
        new_retry = current_retry + 1

        updates: dict[str, Any] = {
            "review_decision": review_decision,
            "review_notes": state.get("review_notes", ""),
            "reviewed_by": state.get("reviewed_by", ""),
            "evidence_retry_count": new_retry,
            "evidence_request_reason": state.get("review_notes", ""),
            "review_payload": review_payload,
            "executed_nodes": _append_node(state, "needs_review"),
        }

        if new_retry > max_retries:
            blockers = list(state.get("blockers", []))
            msg = "max_evidence_retries_reached"
            if msg not in blockers:
                blockers.append(msg)
            updates["status"] = "max_evidence_retries_reached"
            updates["blockers"] = blockers
            updates["review_required"] = False
        else:
            updates["status"] = "planning_more_evidence"
            updates["review_required"] = False

        return updates

    return {
        "status": "needs_human_review",
        "review_required": True,
        "review_payload": review_payload,
        "executed_nodes": _append_node(state, "needs_review"),
    }


def _route_after_review(state: StartupRadarState) -> str:
    review_decision: str | None = state.get("review_decision")
    if review_decision == "approve":
        executed: list[str] = state.get("executed_nodes", [])
        rag_status: str = state.get("rag_retrieval_status") or "needs_review"
        mapping_summary = state.get("nvidia_mapping_summary")
        has_mappings = bool(
            mapping_summary
            and isinstance(mapping_summary, dict)
            and mapping_summary.get("mapping_status")
        )
        if rag_status in ("needs_review", "failed") and "build_technology_mappings" not in executed:
            return "build_technology_mappings"
        if not has_mappings and "build_technology_mappings" not in executed:
            return "build_technology_mappings"
        if "rank_recommendations" not in executed:
            return "rank_recommendations"
        return "finish"
    if review_decision == "reject":
        return "finish"
    if review_decision == "request_more_evidence":
        retry_count = state.get("evidence_retry_count", 0)
        max_retries = state.get("max_evidence_retries", 3)
        if retry_count <= max_retries:
            return "plan_search"
        return "finish"
    return "finish"


def _finish(
    state: StartupRadarState,
    *,
    _analysis_repository: Any = None,
) -> dict[str, Any]:
    run_id = state.get("run_id", "unknown")
    analysis_run_id = state.get("analysis_run_id")
    startup_id = state.get("startup_id")
    current_status = state.get("status", "workflow_skeleton_completed")
    blockers = list(state.get("blockers", []))
    quality = state.get("quality")
    evidence_validation = state.get("evidence_validation")
    rag_metrics = state.get("rag_metrics")
    recommendation_metrics = state.get("recommendation_metrics")
    brief_metrics = state.get("brief_metrics")
    action_brief = state.get("action_brief")
    review_required = state.get("review_required", False)
    review_payload = state.get("review_payload")
    executed_nodes = list(state.get("executed_nodes", [])) + ["finish"]

    output_snapshot: dict[str, Any] = {
        "run_id": run_id,
        "startup_id": startup_id,
        "executed_nodes": executed_nodes,
        "status": current_status,
        "blockers": blockers,
        "quality": quality,
        "evidence_validation": evidence_validation,
        "rag_metrics": rag_metrics,
        "recommendation_metrics": recommendation_metrics,
        "brief_metrics": brief_metrics,
        "action_brief": action_brief,
        "review_required": review_required,
        "review_payload": review_payload,
    }

    errors: list[str] = []
    persist_failed = False

    if _analysis_repository is not None and analysis_run_id:
        try:
            _analysis_repository(
                analysis_run_id,
                status=current_status,
                output_snapshot=output_snapshot,
                error_message="; ".join(blockers) if blockers else None,
            )
        except Exception as exc:
            errors.append(f"Persistence failed: {type(exc).__name__}: {exc}")
            persist_failed = True

    updates_status = "persistence_failed" if persist_failed else current_status
    updates_blockers = list(blockers)
    for err in errors:
        if err not in updates_blockers:
            updates_blockers.append(err)

    updates: dict[str, Any] = {
        "status": updates_status,
        "executed_nodes": executed_nodes,
    }
    if updates_blockers:
        updates["blockers"] = updates_blockers
    return updates


def build_startup_radar_graph(
    *,
    checkpointer: Any = None,
    score_service: ScoreService | None = None,
    rag_service: RagService | None = None,
    diagnose_gaps_service: DiagnoseGapsService | None = None,
    rank_recommendations_service: RankRecommendationsService | None = None,
    generate_brief_service: GenerateBriefService | None = None,
    analysis_repository: PersistWorkflowResultService | None = None,
) -> Any | None:
    """Build and compile the full product workflow.

    Node sequence:
    preflight_configuration_check → plan_search → collect_sources →
    extract_profile → validate_evidence → score_startup → diagnose_gaps →
    retrieve_nvidia_context → rank_recommendations → generate_brief →
    run_quality_gates → finish.

    Parameters
    ----------
    checkpointer:
        A LangGraph checkpointer (e.g. ``MemorySaver()``) for interrupt/resume
        support.  When ``None`` (default) the graph runs without persistence
        and ``interrupt()`` is a no-op.
    score_service:
        Injectable callable for the scoring node.  When ``None`` (default)
        the real ``classifier_agent.score_startup`` is used.
    rag_service:
        Injectable callable for the RAG retrieval node.  When ``None``
        (default) the real ``nvidia_rag_agent.retrieve_nvidia_context``
        is used.
    diagnose_gaps_service:
        Injectable callable for the gap diagnosis node.  When ``None``
        (default) the real ``recommendation_agent.diagnose_gaps`` is used.
    rank_recommendations_service:
        Injectable callable for the recommendations node.  When ``None``
        (default) the real ``recommendation_agent.rank_recommendations``
        is used.
    generate_brief_service:
        Injectable callable for the briefing node.  When ``None`` (default)
        the real ``briefing_agent.generate_brief`` is used.
    analysis_repository:
        Injectable callable for persisting workflow results to AnalysisRun.
        Expected signature: ``(analysis_run_id, *, status, output_snapshot,
        error_message=None)``.  When ``None`` (default) the finish node
        does not persist.
    """
    global _CHECKPOINTER_ENABLED
    _CHECKPOINTER_ENABLED = checkpointer is not None
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(state_schema=StartupRadarState)

    for name in NODE_NAMES:
        fn: Any
        if name == "score_startup" and score_service is not None:
            fn = partial(_score_startup, _score_service=score_service)
        elif name == "retrieve_nvidia_context" and rag_service is not None:
            fn = partial(_retrieve_nvidia_context, _rag_service=rag_service)
        elif name == "diagnose_gaps" and diagnose_gaps_service is not None:
            fn = partial(_diagnose_gaps, _gaps_service=diagnose_gaps_service)
        elif name == "rank_recommendations" and rank_recommendations_service is not None:
            fn = partial(_rank_recommendations, _recommendations_service=rank_recommendations_service)
        elif name == "generate_brief" and generate_brief_service is not None:
            fn = partial(_generate_brief, _brief_service=generate_brief_service)
        elif name == "finish" and analysis_repository is not None:
            fn = partial(_finish, _analysis_repository=analysis_repository)
        else:
            fn = globals().get(f"_{name}")
            if fn is None:
                msg = f"Missing node function for {name}"
                raise ValueError(msg)
        graph.add_node(name, fn)

    graph.add_node("needs_review", _needs_review)

    graph.add_edge(START, "preflight_configuration_check")

    pre_rag_seq = [
        "plan_search",
        "collect_sources",
        "extract_profile",
        "validate_evidence",
        "score_startup",
        "diagnose_gaps",
    ]
    for i in range(len(pre_rag_seq) - 1):
        graph.add_edge(pre_rag_seq[i], pre_rag_seq[i + 1])
    graph.add_edge("diagnose_gaps", "retrieve_nvidia_context")

    graph.add_conditional_edges(
        "retrieve_nvidia_context",
        _route_after_rag,
        {"build_technology_mappings": "build_technology_mappings", "needs_review": "needs_review"},
    )

    graph.add_conditional_edges(
        "build_technology_mappings",
        _route_after_mappings,
        {"rank_recommendations": "rank_recommendations", "needs_review": "needs_review"},
    )

    post_rag_seq = [
        "rank_recommendations",
        "generate_brief",
        "run_quality_gates",
    ]
    for i in range(len(post_rag_seq) - 1):
        graph.add_edge(post_rag_seq[i], post_rag_seq[i + 1])

    graph.add_conditional_edges(
        "preflight_configuration_check",
        _route_after_preflight,
        {"finish": "finish", "plan_search": "plan_search"},
    )

    graph.add_conditional_edges(
        "run_quality_gates",
        _route_after_quality_gates,
        {"needs_review": "needs_review", "finish": "finish"},
    )

    graph.add_conditional_edges(
        "needs_review",
        _route_after_review,
        {
            "finish": "finish",
            "plan_search": "plan_search",
            "build_technology_mappings": "build_technology_mappings",
            "rank_recommendations": "rank_recommendations",
        },
    )
    graph.add_edge("finish", END)

    if checkpointer is not None:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


__all__ = ["build_startup_radar_graph", "NodeExecutionError"]
