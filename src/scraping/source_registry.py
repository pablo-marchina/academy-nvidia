from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator

from src.quality.decision_calibration_registry import (
    DecisionCalibrationRecord,
    get_project_decision_inventory,
    validate_decision_for_production,
)
from src.scraping.rate_limit_policy import (
    get_available_capabilities,
    get_rate_limit_policy,
)


class SourceRecord(BaseModel):
    source_id: str
    source_name: str
    source_category: str
    base_url: str
    allowed_paths: list[str] = []
    disallowed_paths: list[str] = []
    requires_api_key: bool = False
    required_capability: str | None = None
    requires_login: bool = False
    paywall_risk: str = "none"
    robots_required: bool = True
    terms_review_required: bool = False
    rate_limit_policy_id: str = "default_polite"
    collector_type: str = "http"
    parser_type: str = "html"
    calibrated_priority_score: float | None = None
    priority_calibration_decision_id: str | None = None
    expected_evidence_types: list[str] = []
    expected_claim_types: list[str] = []
    source_quality_prior: float = 0.5
    production_enabled: bool = False
    production_blockers: list[str] = []
    notes: str = ""

    @field_validator("source_category")
    @classmethod
    def _validate_category(cls, v: str) -> str:
        allowed = {
            "official_website", "technical_docs", "funding_news", "jobs",
            "github_or_code", "ecosystem_directory", "media", "nvidia_or_partner_ecosystem",
        }
        if v not in allowed:
            msg = f"Invalid category '{v}'. Must be one of: {', '.join(sorted(allowed))}"
            raise ValueError(msg)
        return v

    @field_validator("paywall_risk")
    @classmethod
    def _validate_paywall_risk(cls, v: str) -> str:
        allowed = {"none", "low", "medium", "high", "mandatory"}
        if v not in allowed:
            msg = f"Invalid paywall_risk '{v}'"
            raise ValueError(msg)
        return v


def _build_source_registry() -> dict[str, SourceRecord]:
    records: dict[str, SourceRecord] = {}

    def add(rec: SourceRecord) -> None:
        records[rec.source_id] = rec

    # ── official_website ───────────────────────────────────────────────
    add(SourceRecord(
        source_id="startup_official_website",
        source_name="Startup Official Website",
        source_category="official_website",
        base_url="",
        allowed_paths=["/about", "/team", "/company", "/", "/blog"],
        disallowed_paths=["/login", "/admin", "/wp-admin"],
        robots_required=True,
        rate_limit_policy_id="default_polite",
        calibrated_priority_score=1.75,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["ai_native_signal", "team_info", "product_description"],
        expected_claim_types=["ai_adoption", "team_expertise", "product_capability"],
        source_quality_prior=0.9,
        notes="Per-startup official website. Base URL provided at runtime.",
    ))

    # ── github_or_code ─────────────────────────────────────────────────
    add(SourceRecord(
        source_id="github_api_search",
        source_name="GitHub API Repository Search",
        source_category="github_or_code",
        base_url="https://api.github.com",
        allowed_paths=["/search/repositories", "/repos/*"],
        disallowed_paths=["/user", "/users/*/repos"],
        requires_api_key=True,
        required_capability="github_token",
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="github_api",
        collector_type="api",
        parser_type="json",
        calibrated_priority_score=1.24,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["code_repository", "open_source_contributions"],
        expected_claim_types=["tech_stack", "open_source_usage"],
        source_quality_prior=0.8,
        notes="GitHub search API for startup repositories. Requires GITHUB_TOKEN.",
    ))

    # ── nvidia_or_partner_ecosystem ────────────────────────────────────
    add(SourceRecord(
        source_id="nvidia_inception_directory",
        source_name="NVIDIA Inception Program Directory",
        source_category="nvidia_or_partner_ecosystem",
        base_url="https://www.nvidia.com",
        allowed_paths=["/en-us/startups", "/en-us/inception", "/partners"],
        disallowed_paths=["/login", "/signup"],
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="nvidia_eco",
        calibrated_priority_score=1.07,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["nvidia_partnership", "inception_membership"],
        expected_claim_types=["nvidia_fit", "nvidia_technology_usage"],
        source_quality_prior=0.85,
        notes="NVIDIA public pages for startup and partner ecosystem.",
    ))
    add(SourceRecord(
        source_id="nvidia_developer_program",
        source_name="NVIDIA Developer Program",
        source_category="nvidia_or_partner_ecosystem",
        base_url="https://developer.nvidia.com",
        allowed_paths=["/*"],
        disallowed_paths=["/login"],
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="nvidia_eco",
        calibrated_priority_score=1.07,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["nvidia_tech_usage", "developer_program"],
        expected_claim_types=["nvidia_fit", "nvidia_technology_usage"],
        source_quality_prior=0.8,
        notes="NVIDIA developer pages for technology documentation and programs.",
    ))

    # ── jobs ────────────────────────────────────────────────────────────
    add(SourceRecord(
        source_id="startup_careers_page",
        source_name="Startup Careers / Jobs Page",
        source_category="jobs",
        base_url="",
        allowed_paths=["/careers", "/jobs", "/join-us", "/trabalhe-conosco"],
        disallowed_paths=["/login", "/apply/*"],
        robots_required=True,
        rate_limit_policy_id="default_polite",
        calibrated_priority_score=0.32,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["job_listings", "hiring_signals"],
        expected_claim_types=["talent_acquisition", "growth_signals"],
        source_quality_prior=0.5,
        notes="Per-startup careers/jobs page. Paths probed at runtime.",
    ))
    add(SourceRecord(
        source_id="linkedin_company_profiles",
        source_name="LinkedIn Company Profiles",
        source_category="jobs",
        base_url="https://www.linkedin.com",
        allowed_paths=["/company/*"],
        disallowed_paths=[],
        requires_login=True,
        paywall_risk="medium",
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="search_engine",
        collector_type="optional_playwright",
        parser_type="html",
        calibrated_priority_score=0.32,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["team_size", "employee_roles", "funding_announcements"],
        expected_claim_types=["team_expertise", "growth_signals"],
        source_quality_prior=0.6,
        notes="LinkedIn company pages. Blocked for production: requires login.",
    ))

    # ── funding_news ───────────────────────────────────────────────────
    add(SourceRecord(
        source_id="exame_news",
        source_name="Exame — Negócios & Startups",
        source_category="funding_news",
        base_url="https://exame.com",
        allowed_paths=["/negocios", "/startups"],
        disallowed_paths=["/login", "/newsletter", "/assine"],
        paywall_risk="medium",
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="news_site",
        calibrated_priority_score=-0.28,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["funding_round", "investment_news"],
        expected_claim_types=["funding", "valuation", "investor_relation"],
        source_quality_prior=0.6,
        notes="Major Brazilian business news outlet. May have soft paywall.",
    ))
    add(SourceRecord(
        source_id="neofeed_news",
        source_name="Neofeed — Negócios & Startups",
        source_category="funding_news",
        base_url="https://neofeed.com.br",
        allowed_paths=["/*"],
        disallowed_paths=["/login", "/cadastro"],
        paywall_risk="low",
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="news_site",
        calibrated_priority_score=-0.28,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["funding_round", "investment_news"],
        expected_claim_types=["funding", "valuation", "investor_relation"],
        source_quality_prior=0.55,
        notes="Brazilian business news covering startups and VC.",
    ))
    add(SourceRecord(
        source_id="startupi_news",
        source_name="Startupi — Ecossistema de Startups",
        source_category="funding_news",
        base_url="https://startupi.com.br",
        allowed_paths=["/*"],
        disallowed_paths=["/login", "/cadastro"],
        paywall_risk="low",
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="news_site",
        calibrated_priority_score=-0.28,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["funding_round", "startup_ecosystem"],
        expected_claim_types=["funding", "ecosystem_presence"],
        source_quality_prior=0.5,
        notes="Brazilian startup ecosystem news and coverage.",
    ))

    # ── technical_docs ─────────────────────────────────────────────────
    add(SourceRecord(
        source_id="startup_docs_site",
        source_name="Startup Technical Documentation",
        source_category="technical_docs",
        base_url="",
        allowed_paths=["/docs", "/documentation", "/developers", "/api"],
        disallowed_paths=["/login", "/admin"],
        robots_required=True,
        rate_limit_policy_id="default_polite",
        calibrated_priority_score=-0.52,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["api_docs", "technical_blog", "architecture"],
        expected_claim_types=["tech_stack", "product_capability", "ai_adoption"],
        source_quality_prior=0.7,
        notes="Per-startup documentation site. Probed at runtime.",
    ))

    # ── ecosystem_directory ────────────────────────────────────────────
    add(SourceRecord(
        source_id="distrito_startup_programs",
        source_name="Distrito — Startup Programs",
        source_category="ecosystem_directory",
        base_url="https://distrito.me",
        allowed_paths=["/programas"],
        disallowed_paths=["/login", "/cadastro"],
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="directory_listing",
        calibrated_priority_score=-0.86,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["startup_listing", "accelerator_program"],
        expected_claim_types=["ecosystem_presence", "acceleration"],
        source_quality_prior=0.6,
        notes="Distrito startup programs and participant listings.",
    ))
    add(SourceRecord(
        source_id="ace_startups_portfolio",
        source_name="Ace Startups — Portfolio",
        source_category="ecosystem_directory",
        base_url="https://acestartups.com.br",
        allowed_paths=["/portfolio"],
        disallowed_paths=["/login"],
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="directory_listing",
        calibrated_priority_score=-0.86,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["startup_listing", "accelerator_portfolio"],
        expected_claim_types=["acceleration", "ecosystem_presence"],
        source_quality_prior=0.6,
        notes="Ace Startups accelerator portfolio page.",
    ))
    add(SourceRecord(
        source_id="bossa_invest_portfolio",
        source_name="Bossa Invest — Portfolio",
        source_category="ecosystem_directory",
        base_url="https://bossainvest.com.br",
        allowed_paths=["/portfolio"],
        disallowed_paths=["/login"],
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="directory_listing",
        calibrated_priority_score=-0.86,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["startup_listing", "vc_portfolio"],
        expected_claim_types=["funding", "ecosystem_presence"],
        source_quality_prior=0.55,
        notes="Bossa Invest VC portfolio page.",
    ))
    add(SourceRecord(
        source_id="inovativa_startups",
        source_name="Inovativa — Startups",
        source_category="ecosystem_directory",
        base_url="https://inovativa.com.br",
        allowed_paths=["/startups"],
        disallowed_paths=["/login"],
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="directory_listing",
        calibrated_priority_score=-0.86,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["startup_listing", "accelerator_cohort"],
        expected_claim_types=["acceleration", "ecosystem_presence"],
        source_quality_prior=0.55,
        notes="Inovativa accelerator cohort listings.",
    ))

    # ── media ──────────────────────────────────────────────────────────
    add(SourceRecord(
        source_id="valor_economico",
        source_name="Valor Econômico — Empresas & Startups",
        source_category="media",
        base_url="https://valor.globo.com",
        allowed_paths=["/empresas", "/startups"],
        disallowed_paths=["/login", "/assine", "/newsletter"],
        paywall_risk="high",
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="news_site",
        calibrated_priority_score=-1.79,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["business_news", "market_analysis"],
        expected_claim_types=["funding", "valuation", "market_position"],
        source_quality_prior=0.65,
        notes="Major Brazilian financial newspaper. High paywall risk.",
    ))
    add(SourceRecord(
        source_id="startse_media",
        source_name="StartSe — Startup & Innovation Media",
        source_category="media",
        base_url="https://startse.com",
        allowed_paths=["/*"],
        disallowed_paths=["/login", "/cadastro"],
        paywall_risk="low",
        robots_required=True,
        terms_review_required=True,
        rate_limit_policy_id="news_site",
        calibrated_priority_score=-1.79,
        priority_calibration_decision_id="scraping.source_priority",
        expected_evidence_types=["startup_news", "innovation_coverage"],
        expected_claim_types=["ecosystem_presence", "media_attention"],
        source_quality_prior=0.5,
        notes="Brazilian startup and innovation media outlet.",
    ))

    return records


_SOURCE_REGISTRY: dict[str, SourceRecord] | None = None


def _check_priority_calibration(
    decision_id: str | None,
    inventory: list[DecisionCalibrationRecord],
) -> bool:
    if decision_id is None:
        return False
    for rec in inventory:
        if rec.decision_id == decision_id:
            result = validate_decision_for_production(rec)
            return result.passed
    return False


def _check_rate_limit_policy_exists(policy_id: str) -> bool:
    return get_rate_limit_policy(policy_id) is not None


def _apply_production_blockers(
    source: SourceRecord,
    inventory: list[DecisionCalibrationRecord],
    *,
    available_capabilities: set[str] | None = None,
) -> list[str]:
    blockers: list[str] = []

    # Policy 2: Priority not calibrated
    if source.calibrated_priority_score is None:
        blockers.append("source_priority_uncalibrated")
    elif not _check_priority_calibration(source.priority_calibration_decision_id, inventory):
        blockers.append("source_priority_uncalibrated")

    # Policy 3: Login required
    if source.requires_login:
        blockers.append("source_requires_login")

    # Policy 3: Paywall mandatory
    if source.paywall_risk == "mandatory":
        blockers.append("source_paywall_mandatory")

    # Policy 4: API key required — check capability readiness
    if source.requires_api_key:
        caps = available_capabilities if available_capabilities is not None else get_available_capabilities()
        if source.required_capability and source.required_capability.lower() in caps:
            pass
        else:
            blockers.append("source_requires_api_key")

    # Policy 5: robots_required not defined
    if not source.robots_required:
        blockers.append("source_robots_not_defined")

    # Policy 1: rate_limit_policy_id doesn't exist
    if not _check_rate_limit_policy_exists(source.rate_limit_policy_id):
        blockers.append("rate_limit_policy_not_found")

    return blockers


def load_source_registry(
    *,
    available_capabilities: set[str] | None = None,
) -> dict[str, SourceRecord]:
    global _SOURCE_REGISTRY
    if _SOURCE_REGISTRY is None:
        records = _build_source_registry()
        inventory = get_project_decision_inventory()
        caps = available_capabilities if available_capabilities is not None else get_available_capabilities()

        for src in records.values():
            blockers = _apply_production_blockers(src, inventory, available_capabilities=caps)
            src.production_blockers = blockers
            if len(blockers) == 0:
                src.production_enabled = True
            else:
                src.production_enabled = False

        _SOURCE_REGISTRY = records
    return _SOURCE_REGISTRY


def list_sources() -> list[SourceRecord]:
    return list(load_source_registry().values())


def list_sources_by_category(category: str) -> list[SourceRecord]:
    return [s for s in list_sources() if s.source_category == category]


def list_production_enabled_sources() -> list[SourceRecord]:
    return [s for s in list_sources() if s.production_enabled]


def validate_source_for_production(
    source: SourceRecord,
    *,
    available_capabilities: set[str] | None = None,
) -> dict[str, Any]:
    inventory = get_project_decision_inventory()
    caps = available_capabilities if available_capabilities is not None else get_available_capabilities()
    blockers = _apply_production_blockers(source, inventory, available_capabilities=caps)

    if len(blockers) == 0:
        return {
            "source_id": source.source_id,
            "passed": True,
            "blockers": [],
            "production_enabled": True,
        }

    return {
        "source_id": source.source_id,
        "passed": False,
        "blockers": blockers,
        "production_enabled": False,
    }


def reset_source_registry_cache() -> None:
    global _SOURCE_REGISTRY
    _SOURCE_REGISTRY = None


def summarize_source_coverage() -> dict[str, Any]:
    sources = list_sources()
    total = len(sources)
    categories = sorted({s.source_category for s in sources})

    by_category: dict[str, int] = {}
    enabled_by_category: dict[str, int] = {}
    for cat in categories:
        by_category[cat] = sum(1 for s in sources if s.source_category == cat)
        enabled_by_category[cat] = sum(1 for s in sources if s.source_category == cat and s.production_enabled)

    return {
        "total_sources": total,
        "total_categories": len(categories),
        "production_enabled_count": sum(1 for s in sources if s.production_enabled),
        "blocked_count": sum(1 for s in sources if not s.production_enabled),
        "sources_by_category": by_category,
        "enabled_by_category": enabled_by_category,
    }


def summarize_production_blockers() -> dict[str, int]:
    sources = list_sources()
    blocker_counts: dict[str, int] = {}
    for s in sources:
        for b in s.production_blockers:
            blocker_counts[b] = blocker_counts.get(b, 0) + 1
    return dict(sorted(blocker_counts.items()))
