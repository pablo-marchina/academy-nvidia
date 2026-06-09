"""Production AI Readiness — deterministic assessment of production maturity for AI startups."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.classification.ai_native_classifier import ClassificationResult
from src.extraction.schemas import AINativeLevel, ConfidenceLevel, StartupProfile
from src.validation.evidence_validator import ValidatedEvidence

# ---------------------------------------------------------------------------
# Dimension weights
# ---------------------------------------------------------------------------
_REAL_USERS_WEIGHT = 0.30
_SCALE_INFERENCE_WEIGHT = 0.30
_PRIVACY_GOV_WEIGHT = 0.20
_DATA_INFRA_WEIGHT = 0.20

# ---------------------------------------------------------------------------
# Evidence filtering keywords per dimension
# ---------------------------------------------------------------------------
_EVIDENCE_USERS = ["Customer", "Company desc", "Funding"]
_EVIDENCE_SCALE = ["Customer", "Funding", "Tech stack", "AI signal"]
_EVIDENCE_PRIVACY = ["Company desc", "AI signal"]
_EVIDENCE_DATA = ["Tech stack", "AI signal", "Company desc"]

# ---------------------------------------------------------------------------
# Keyword lists
# ---------------------------------------------------------------------------
_PRIORITY_SECTORS: list[str] = [
    "HealthTech",
    "FinTech",
    "AgTech",
    "LegalTech",
    "EdTech",
]
_REGULATED_SECTORS: list[str] = [
    "HealthTech",
    "FinTech",
    "LegalTech",
]

_PRODUCTION_KEYWORDS: list[str] = [
    "production",
    "deployed",
    "deployment",
    "real-world",
    "production-ready",
    "em producao",
    "implementado",
]
_INFERENCE_KEYWORDS: list[str] = [
    "low latency",
    "real-time",
    "inference",
    "latency",
    "throughput",
    "high throughput",
]
_COMPLIANCE_KEYWORDS: list[str] = [
    "compliance",
    "privacy",
    "lgpd",
    "governance",
    "hipaa",
    "security",
    "controlled deployment",
    "on-prem",
    "data protection",
]
_DATA_KEYWORDS: list[str] = [
    "data pipeline",
    "data processing",
    "etl",
    "data infrastructure",
    "data lake",
    "data warehouse",
    "streaming",
    "kafka",
    "spark",
]
_DATA_TECH_KEYWORDS: list[str] = [
    "kafka",
    "spark",
    "hadoop",
    "postgresql",
    "redis",
    "mongodb",
    "snowflake",
    "bigquery",
    "redshift",
]
_SCALE_TECH_KEYWORDS: list[str] = [
    "kubernetes",
    "docker",
    "aws",
    "gcp",
    "azure",
    "microservices",
    "serverless",
]

_CONFIDENCE_TO_FACTOR: dict[ConfidenceLevel, float] = {
    ConfidenceLevel.HIGH: 1.0,
    ConfidenceLevel.MEDIUM: 0.7,
    ConfidenceLevel.LOW: 0.4,
}
_NO_EVIDENCE_FACTOR = 0.3


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class ReadinessDimension(BaseModel):
    dimension_name: str
    weight: float
    raw_score: float
    adjusted_score: float
    confidence: ConfidenceLevel
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)


class ProductionReadinessResult(BaseModel):
    production_readiness_score: float
    score_breakdown: dict[str, ReadinessDimension]
    confidence: ConfidenceLevel
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _filter_evidence(
    evidence_list: list[ValidatedEvidence],
    keywords: list[str],
) -> list[ValidatedEvidence]:
    result: list[ValidatedEvidence] = []
    for ev in evidence_list:
        lower = ev.claim.lower()
        if any(kw.lower() in lower for kw in keywords):
            result.append(ev)
    return result


def _evidence_confidence_penalty(
    evidence_list: list[ValidatedEvidence],
) -> tuple[float, ConfidenceLevel]:
    if not evidence_list:
        return _NO_EVIDENCE_FACTOR, ConfidenceLevel.LOW
    factors = [_CONFIDENCE_TO_FACTOR.get(ev.confidence, 0.4) for ev in evidence_list]
    avg = sum(factors) / len(factors)
    if avg >= 0.8:
        return avg, ConfidenceLevel.HIGH
    if avg >= 0.5:
        return avg, ConfidenceLevel.MEDIUM
    return avg, ConfidenceLevel.LOW


def _count_keyword_matches(text: str, signals: list[str], keywords: list[str]) -> int:
    combined = (text + " " + " ".join(signals)).lower()
    return sum(1 for kw in keywords if kw in combined)


# ---------------------------------------------------------------------------
# Dimension scoring functions
# ---------------------------------------------------------------------------


def _score_real_users_and_deployment(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> ReadinessDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_USERS)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 0
    reasons: list[str] = []

    if profile.customers:
        n = len(profile.customers)
        if n >= 3:
            base += 30
            reasons.append(f"customers ({n}, +30)")
        else:
            base += 25
            reasons.append(f"customer ({n}, +25)")

    if profile.funding_signals:
        base += 20
        reasons.append(f"funding ({len(profile.funding_signals)}, +20)")

    cl = classification.classification
    if cl in (AINativeLevel.AI_NATIVE, AINativeLevel.AI_NATIVE_SERVICE):
        base += 25
        reasons.append(f"{cl.value} (+25)")
    elif cl == AINativeLevel.AI_ENABLED:
        base += 15
        reasons.append("ai_enabled (+15)")

    prod_count = _count_keyword_matches(combined, profile.ai_signals, _PRODUCTION_KEYWORDS)
    if prod_count >= 1:
        base += 15
        reasons.append(f"production keywords ({prod_count}, +15)")

    if len(profile.tech_stack_signals) >= 2:
        base += 10
        reasons.append("diverse tech stack (+10)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)
    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return ReadinessDimension(
        dimension_name="real_users_and_deployment",
        weight=_REAL_USERS_WEIGHT,
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_scale_and_inference(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> ReadinessDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_SCALE)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 0
    reasons: list[str] = []

    if profile.customers:
        n = len(profile.customers)
        if n >= 3:
            base += 30
            reasons.append(f"customers ({n}, +30)")
        elif n >= 1:
            base += 15
            reasons.append(f"customer ({n}, +15)")

    if profile.funding_signals:
        base += 20
        reasons.append(f"funding ({len(profile.funding_signals)}, +20)")

    inf_count = _count_keyword_matches(combined, profile.ai_signals, _INFERENCE_KEYWORDS)
    if inf_count >= 2:
        base += 25
        reasons.append(f"inference signals ({inf_count}, +25)")
    elif inf_count >= 1:
        base += 15
        reasons.append(f"inference signal ({inf_count}, +15)")

    nv_count = _count_keyword_matches(
        combined,
        profile.tech_stack_signals,
        [
            "pytorch",
            "tensorflow",
            "cuda",
            "tensorrt",
            "triton",
        ],
    )
    if nv_count >= 1:
        base += 15
        reasons.append(f"NVIDIA-compatible tech ({nv_count}, +15)")

    scale_count = _count_keyword_matches(combined, profile.tech_stack_signals, _SCALE_TECH_KEYWORDS)
    if scale_count >= 2:
        base += 15
        reasons.append(f"scale tech ({scale_count}, +15)")
    elif scale_count >= 1:
        base += 10
        reasons.append(f"scale tech ({scale_count}, +10)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)
    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return ReadinessDimension(
        dimension_name="scale_and_inference",
        weight=_SCALE_INFERENCE_WEIGHT,
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_privacy_and_governance(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> ReadinessDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_PRIVACY)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 0
    reasons: list[str] = []

    if profile.sector in _REGULATED_SECTORS:
        base += 35
        reasons.append(f"regulated sector '{profile.sector}' (+35)")
    elif profile.sector in _PRIORITY_SECTORS:
        base += 20
        reasons.append(f"priority sector '{profile.sector}' (+20)")

    comp_count = _count_keyword_matches(combined, profile.ai_signals, _COMPLIANCE_KEYWORDS)
    if comp_count >= 2:
        base += 30
        reasons.append(f"compliance signals ({comp_count}, +30)")
    elif comp_count >= 1:
        base += 20
        reasons.append(f"compliance signal ({comp_count}, +20)")

    has_gap = (
        "privacy" in combined.lower()
        or "controlled deployment" in combined.lower()
        or "on-prem" in combined.lower()
    )
    if has_gap:
        base += 20
        reasons.append("privacy/controlled deployment mention (+20)")

    if profile.tech_stack_signals:
        lower_stack = " ".join(profile.tech_stack_signals).lower()
        if "kubernetes" in lower_stack or "docker" in lower_stack:
            base += 15
            reasons.append("containerization tech (+15)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)
    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return ReadinessDimension(
        dimension_name="privacy_and_governance",
        weight=_PRIVACY_GOV_WEIGHT,
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_data_infrastructure(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> ReadinessDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_DATA)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 0
    reasons: list[str] = []

    data_kw_count = _count_keyword_matches(combined, profile.ai_signals, _DATA_KEYWORDS)
    if data_kw_count >= 2:
        base += 35
        reasons.append(f"data pipeline keywords ({data_kw_count}, +35)")
    elif data_kw_count >= 1:
        base += 25
        reasons.append(f"data pipeline keyword ({data_kw_count}, +25)")

    data_tech_count = _count_keyword_matches("", profile.tech_stack_signals, _DATA_TECH_KEYWORDS)
    if data_tech_count >= 2:
        base += 30
        reasons.append(f"data tech stack ({data_tech_count}, +30)")
    elif data_tech_count >= 1:
        base += 20
        reasons.append(f"data tech ({data_tech_count}, +20)")

    tabular_count = _count_keyword_matches(
        combined,
        profile.ai_signals,
        [
            "tabular",
            "structured data",
            "predictive model",
            "predictive analytics",
        ],
    )
    if tabular_count >= 1:
        base += 20
        reasons.append(f"tabular/predictive signals ({tabular_count}, +20)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)
    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return ReadinessDimension(
        dimension_name="data_infrastructure",
        weight=_DATA_INFRA_WEIGHT,
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def compute_production_readiness(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> ProductionReadinessResult:
    """Compute the Production AI Readiness score (0–100).

    Parameters
    ----------
    profile:
        Extracted startup profile with signals and evidence.
    classification:
        AI-native classification result.
    validated_evidence:
        Evidence objects with kind and confidence already validated.

    Returns
    -------
    ProductionReadinessResult
        Readiness score, per-dimension breakdown, confidence, reasoning,
        evidence used, and missing evidence.
    """
    scores: dict[str, ReadinessDimension] = {}

    scores["real_users_and_deployment"] = _score_real_users_and_deployment(
        profile, classification, validated_evidence
    )
    scores["scale_and_inference"] = _score_scale_and_inference(
        profile, classification, validated_evidence
    )
    scores["privacy_and_governance"] = _score_privacy_and_governance(
        profile, classification, validated_evidence
    )
    scores["data_infrastructure"] = _score_data_infrastructure(
        profile, classification, validated_evidence
    )

    total = sum(s.adjusted_score * s.weight for s in scores.values())
    total = round(total, 1)

    all_evidence: list[ValidatedEvidence] = []
    missing: list[str] = []
    for name, ds in scores.items():
        all_evidence.extend(ds.evidence_used)
        if not ds.evidence_used:
            missing.append(f"No evidence for dimension: {name}")
        elif ds.confidence == ConfidenceLevel.LOW:
            missing.append(
                f"Weak evidence for dimension: {name} " f"(confidence: {ds.confidence.value})"
            )

    conf_factors = [_CONFIDENCE_TO_FACTOR.get(s.confidence, 0.4) for s in scores.values()]
    avg_conf = sum(conf_factors) / len(conf_factors)

    if avg_conf >= 0.8:
        overall_conf = ConfidenceLevel.HIGH
    elif avg_conf >= 0.5:
        overall_conf = ConfidenceLevel.MEDIUM
    else:
        overall_conf = ConfidenceLevel.LOW

    lines = [
        f"Production AI Readiness: {total}/100 (confidence: {overall_conf.value})",
        "",
        "Breakdown:",
    ]
    for name, ds in scores.items():
        lines.append(
            f"  {name}: raw={ds.raw_score}, adjusted={ds.adjusted_score}, "
            f"weight={ds.weight}, conf={ds.confidence.value}"
        )
        lines.append(f"    reasoning: {ds.reasoning}")
    if missing:
        lines.append("")
        lines.append("Missing evidence:")
        for m in missing:
            lines.append(f"  - {m}")

    reasoning = "\n".join(lines)

    return ProductionReadinessResult(
        production_readiness_score=total,
        score_breakdown=scores,
        confidence=overall_conf,
        reasoning=reasoning,
        evidence_used=all_evidence,
        missing_evidence=missing,
    )
