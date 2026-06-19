"""NVIDIA Inception Fit Score — evidence-aware prioritization for Inception outreach."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.classification.ai_native_classifier import ClassificationResult
from src.extraction.schemas import AINativeLevel, ConfidenceLevel, StartupProfile, TechnicalGap
from src.quantitative.params import (
    CONFIDENCE_SCORE_FACTORS,
    INCEPTION_FIT_WEIGHTS,
    NO_EVIDENCE_FACTOR,
)
from src.validation.evidence_validator import ValidatedEvidence

# ---------------------------------------------------------------------------
# Evidence filtering keywords per dimension
# ---------------------------------------------------------------------------
_EVIDENCE_GAP = ["Tech stack", "AI signal", "Company desc"]
_EVIDENCE_VERTICAL = ["Company desc", "Funding"]
_EVIDENCE_MATURITY = ["Tech stack", "Company desc", "Funding"]
_EVIDENCE_REVENUE = ["Customer", "Funding", "AI signal", "Company desc"]

# ---------------------------------------------------------------------------
# Keyword lists for gap detection
# ---------------------------------------------------------------------------
_GAP_KEYWORDS: dict[TechnicalGap, list[str]] = {
    TechnicalGap.EXTERNAL_API_DEPENDENCY: ["gpt", "openai"],
    TechnicalGap.HIGH_LATENCY: ["latency", "real-time", "throughput"],
    TechnicalGap.AGENT_GOVERNANCE_GAP: ["agent", "autonomous"],
    TechnicalGap.PRIVACY_OR_CONTROLLED_DEPLOYMENT_GAP: [
        "privacy",
        "on-prem",
        "controlled deployment",
    ],
    TechnicalGap.SLOW_DATA_PIPELINE: ["data pipeline", "data processing"],
    TechnicalGap.HEAVY_TABULAR_PROCESSING: ["tabular", "structured data"],
    TechnicalGap.VOICE_NEED: ["voice", "speech", "audio"],
    TechnicalGap.SIMULATION_NEED: ["simulation", "digital twin"],
    TechnicalGap.COMPUTER_VISION_NEED: ["computer vision", "image", "video"],
    TechnicalGap.ROBOTICS_NEED: ["robot", "robotics"],
    TechnicalGap.HEALTHCARE_COMPLIANCE_NEED: ["healthcare", "compliance", "hipaa"],
    TechnicalGap.AI_CYBERSECURITY_NEED: ["cybersecurity", "threat detection"],
}

_PRIORITY_SECTORS: list[str] = [
    "HealthTech",
    "FinTech",
    "AgTech",
    "LegalTech",
    "EdTech",
]




# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class InceptionFitDimension(BaseModel):
    dimension_name: str
    weight: float
    raw_score: float
    adjusted_score: float
    confidence: ConfidenceLevel
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)


class InceptionFitScoreResult(BaseModel):
    total_score: float
    score_breakdown: dict[str, InceptionFitDimension]
    confidence: ConfidenceLevel
    detected_gaps: list[TechnicalGap] = Field(default_factory=list)
    recommended_motion_hint: str
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
        return NO_EVIDENCE_FACTOR, ConfidenceLevel.LOW
    factors = [CONFIDENCE_SCORE_FACTORS.get(ev.confidence.value, 0.4) for ev in evidence_list]
    avg = sum(factors) / len(factors)
    if avg >= 0.8:
        return avg, ConfidenceLevel.HIGH
    if avg >= 0.5:
        return avg, ConfidenceLevel.MEDIUM
    return avg, ConfidenceLevel.LOW


def _keyword_in_text(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _count_keyword_matches(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------


def _detect_gaps(profile: StartupProfile) -> list[TechnicalGap]:
    combined = (
        f"{profile.product_summary} {profile.description} "
        + " ".join(profile.ai_signals)
        + " "
        + " ".join(profile.tech_stack_signals)
    ).lower()

    detected: list[TechnicalGap] = []
    for gap, keywords in _GAP_KEYWORDS.items():
        if _keyword_in_text(combined, keywords):
            detected.append(gap)

    if profile.sector == "HealthTech" and TechnicalGap.HEALTHCARE_COMPLIANCE_NEED not in detected:
        detected.append(TechnicalGap.HEALTHCARE_COMPLIANCE_NEED)

    return detected


# ---------------------------------------------------------------------------
# Motion hint logic
# ---------------------------------------------------------------------------


def _compute_motion_hint(total_score: float, confidence: ConfidenceLevel) -> str:
    if total_score >= 70 and confidence == ConfidenceLevel.HIGH:
        return "approach_now"
    if total_score >= 50 and confidence in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM):
        return "validate_manually"
    if total_score >= 30:
        return "monitor"
    return "discard_for_now"


# ---------------------------------------------------------------------------
# Dimension scoring functions
# ---------------------------------------------------------------------------


def _score_gap_taxonomy(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> InceptionFitDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_GAP)
    factor, conf = _evidence_confidence_penalty(evidence)
    gaps = _detect_gaps(profile)
    n = len(gaps)

    base: int
    if profile.sector in _PRIORITY_SECTORS:
        base = 10
    else:
        base = 5

    if n >= 4:
        base = 100
    elif n == 3:
        base = 80
    elif n == 2:
        base = 60
    elif n == 1:
        base = 40
    else:
        base = base

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    gap_names = [g.value for g in gaps]
    reasoning = (
        f"Gaps detected: {n} ({', '.join(gap_names) if gap_names else 'none'}). "
        f"Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."
    )

    return InceptionFitDimension(
        dimension_name="explicit_gap_taxonomy",
        weight=INCEPTION_FIT_WEIGHTS["gap_taxonomy"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_vertical_alignment(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> InceptionFitDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_VERTICAL)
    factor, conf = _evidence_confidence_penalty(evidence)

    base = 0
    reasons: list[str] = []

    if profile.sector in _PRIORITY_SECTORS:
        base += 60
        reasons.append(f"priority sector '{profile.sector}' (+60)")
    else:
        reasons.append(f"non-priority sector '{profile.sector}'")

    if profile.funding_signals:
        base += 20
        reasons.append(f"funding signals ({len(profile.funding_signals)}, +20)")

    if profile.customers:
        base += 20
        reasons.append(f"customers ({len(profile.customers)}, +20)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return InceptionFitDimension(
        dimension_name="vertical_alignment",
        weight=INCEPTION_FIT_WEIGHTS["vertical_alignment"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_technical_maturity(
    profile: StartupProfile,
    classification: ClassificationResult,
    defensibility_total_score: float,
    validated_evidence: list[ValidatedEvidence],
) -> InceptionFitDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_MATURITY)
    factor, conf = _evidence_confidence_penalty(evidence)

    base: int
    if defensibility_total_score >= 70:
        base = 60
    elif defensibility_total_score >= 50:
        base = 45
    elif defensibility_total_score >= 30:
        base = 30
    else:
        base = 15

    reasons: list[str] = [f"defensibility base ({round(defensibility_total_score)} → {base})"]

    cl = classification.classification
    if cl in (AINativeLevel.AI_NATIVE, AINativeLevel.AI_NATIVE_SERVICE):
        base += 20
        reasons.append(f"{cl.value} classification (+20)")

    if profile.tech_stack_signals:
        base += 10
        reasons.append(f"tech stack signals ({len(profile.tech_stack_signals)}, +10)")

    if profile.funding_signals:
        base += 10
        reasons.append("funding (+10)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return InceptionFitDimension(
        dimension_name="technical_maturity",
        weight=INCEPTION_FIT_WEIGHTS["technical_maturity"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_revenue_potential(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> InceptionFitDimension:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_REVENUE)
    factor, conf = _evidence_confidence_penalty(evidence)

    base = 0
    reasons: list[str] = []

    if profile.funding_signals:
        base += 30
        reasons.append(f"funding ({len(profile.funding_signals)}, +30)")

    if profile.customers:
        n = len(profile.customers)
        if n >= 3:
            base += 30
            reasons.append(f"customers ({n}, +30)")
        else:
            base += 25
            reasons.append(f"customer ({n}, +25)")

    if profile.sector in _PRIORITY_SECTORS:
        base += 20
        reasons.append("priority sector (+20)")

    high_conf_evidence = [ev for ev in evidence if ev.confidence == ConfidenceLevel.HIGH]
    if len(high_conf_evidence) >= 2:
        base += 15
        reasons.append("multiple high-confidence sources (+15)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return InceptionFitDimension(
        dimension_name="revenue_potential",
        weight=INCEPTION_FIT_WEIGHTS["revenue_potential"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def compute_inception_fit_score(
    profile: StartupProfile,
    classification: ClassificationResult,
    defensibility_total_score: float,
    validated_evidence: list[ValidatedEvidence],
) -> InceptionFitScoreResult:
    """Compute the NVIDIA Inception Fit Score (0–100).

    Parameters
    ----------
    profile:
        Extracted startup profile with signals and evidence.
    classification:
        AI-native classification result.
    defensibility_total_score:
        Total score from the AI-Native Defensibility Score (0–100).
    validated_evidence:
        Evidence objects with kind and confidence already validated.

    Returns
    -------
    InceptionFitScoreResult
        Total score, per-dimension breakdown, confidence, detected gaps,
        recommended motion hint, reasoning, evidence used, and missing evidence.
    """
    gaps = _detect_gaps(profile)

    scores: dict[str, InceptionFitDimension] = {}

    scores["explicit_gap_taxonomy"] = _score_gap_taxonomy(
        profile, classification, validated_evidence
    )
    scores["vertical_alignment"] = _score_vertical_alignment(
        profile, classification, validated_evidence
    )
    scores["technical_maturity"] = _score_technical_maturity(
        profile, classification, defensibility_total_score, validated_evidence
    )
    scores["revenue_potential"] = _score_revenue_potential(
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
                f"Weak evidence for dimension: {name} (confidence: {ds.confidence.value})"
            )

    conf_factors = [CONFIDENCE_SCORE_FACTORS.get(s.confidence.value, 0.4) for s in scores.values()]
    avg_conf = sum(conf_factors) / len(conf_factors)

    if avg_conf >= 0.8:
        overall_conf = ConfidenceLevel.HIGH
    elif avg_conf >= 0.5:
        overall_conf = ConfidenceLevel.MEDIUM
    else:
        overall_conf = ConfidenceLevel.LOW

    motion = _compute_motion_hint(total, overall_conf)

    gap_names = [g.value for g in gaps]
    lines = [
        f"Total Score: {total}/100 (confidence: {overall_conf.value})",
        f"Recommended motion: {motion}",
        f"Detected gaps: {', '.join(gap_names) if gap_names else 'none'}",
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

    return InceptionFitScoreResult(
        total_score=total,
        score_breakdown=scores,
        confidence=overall_conf,
        detected_gaps=gaps,
        recommended_motion_hint=motion,
        reasoning=reasoning,
        evidence_used=all_evidence,
        missing_evidence=missing,
    )
