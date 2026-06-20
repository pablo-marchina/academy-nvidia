"""AI-Native Defensibility Score — deterministic, evidence-aware scoring from 0 to 100."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.classification.ai_native_classifier import ClassificationResult
from src.extraction.schemas import AINativeLevel, ConfidenceLevel, StartupProfile
from src.quantitative.params import (
    CONFIDENCE_SCORE_FACTORS,
    DEFENSIBILITY_WEIGHTS,
    NO_EVIDENCE_FACTOR,
)
from src.validation.evidence_validator import ValidatedEvidence

# ---------------------------------------------------------------------------
# Evidence filtering keywords per dimension
# ---------------------------------------------------------------------------
_EVIDENCE_AI_CORE = ["AI signal", "Company desc"]
_EVIDENCE_PROPRIETARY = ["AI signal", "Service pattern"]
_EVIDENCE_WORKFLOW = ["Service pattern", "Customer"]
_EVIDENCE_REAL_USAGE = ["Customer", "Funding"]
_EVIDENCE_REPLICATION = ["Tech stack", "AI signal"]
_EVIDENCE_NVIDIA_FIT = ["Tech stack", "Company desc"]

# ---------------------------------------------------------------------------
# Keyword lists for heuristic scoring
# ---------------------------------------------------------------------------
_PROPRIETARY_KEYWORDS: list[str] = [
    "proprietary data",
    "exclusive data",
    "dados proprietarios",
    "dados exclusivos",
    "fine-tuned",
    "trained on",
    "custom model",
    "vertical solution",
    "industry-specific",
]
_WORKFLOW_KEYWORDS: list[str] = [
    "workflow integration",
    "enterprise integration",
    "process automation",
    "automacao de processos",
    "integracao de workflow",
]
_REAL_USAGE_KEYWORDS: list[str] = [
    "production",
    "deployed",
    "real-world",
    "feedback",
    "continuous learning",
    "ciclo de feedback",
]
_EXTERNAL_API_KEYWORDS: list[str] = ["gpt", "openai", "api dependency"]
_CUSTOM_MODEL_KEYWORDS: list[str] = [
    "fine-tuned",
    "trained on",
    "custom model",
    "professional services",
]
_NVIDIA_TECH_KEYWORDS: list[str] = [
    "pytorch",
    "tensorflow",
    "cuda",
    "tensorrt",
    "rapids",
    "triton",
]
_INFERENCE_KEYWORDS: list[str] = [
    "low latency",
    "real-time",
    "inference",
    "latency",
    "throughput",
]
_GOVERNANCE_KEYWORDS: list[str] = [
    "governance",
    "security",
    "compliance",
    "lgpd",
    "privacy",
    "guardrails",
]
_CV_KEYWORDS: list[str] = ["computer vision", "visao computacional", "image", "video"]
_LLM_KEYWORDS: list[str] = ["llm", "large language model", "gpt", "transformer"]
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


class DimensionScore(BaseModel):
    dimension_name: str
    weight: float
    raw_score: float
    adjusted_score: float
    confidence: ConfidenceLevel
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)


class DefensibilityScoreResult(BaseModel):
    total_score: float
    score_breakdown: dict[str, DimensionScore]
    confidence: ConfidenceLevel
    classification_boost: str
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


def _keyword_in_signals_or_text(
    text: str,
    signals: list[str],
    keywords: list[str],
) -> bool:
    combined = (text + " " + " ".join(signals)).lower()
    return any(kw in combined for kw in keywords)


def _count_keyword_matches(
    text: str,
    signals: list[str],
    keywords: list[str],
) -> int:
    combined = (text + " " + " ".join(signals)).lower()
    return sum(1 for kw in keywords if kw in combined)


# ---------------------------------------------------------------------------
# Dimension scoring functions
# ---------------------------------------------------------------------------


def _score_ai_core_dependency(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> DimensionScore:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_AI_CORE)
    factor, conf = _evidence_confidence_penalty(evidence)

    level = classification.classification
    base = {
        AINativeLevel.NON_AI: 0,
        AINativeLevel.AI_ASSISTED: 15,
        AINativeLevel.AI_ENABLED: 40,
        AINativeLevel.AI_NATIVE: 85,
        AINativeLevel.AI_NATIVE_SERVICE: 95,
    }.get(level, 0)

    bonus = min(len(profile.ai_signals) * 2, 10) + min(len(profile.tech_stack_signals), 5)
    raw = min(base + bonus, 100)
    adjusted = round(raw * factor, 1)

    reasoning = (
        f"Classification: {level.value} (base {base}). "
        f"AI signals: {len(profile.ai_signals)}, tech stack: {len(profile.tech_stack_signals)}. "
        f"Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."
    )

    return DimensionScore(
        dimension_name="ai_core_dependency",
        weight=DEFENSIBILITY_WEIGHTS["ai_core"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_proprietary_data(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> DimensionScore:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_PROPRIETARY)
    factor, conf = _evidence_confidence_penalty(evidence)

    combined = f"{profile.product_summary} {profile.description}"
    sig_text = " ".join(profile.ai_signals)

    base = 0
    reasons: list[str] = []
    if classification.classification == AINativeLevel.AI_NATIVE_SERVICE:
        base += 30
        reasons.append("AI-native service (+30)")

    kw_count = _count_keyword_matches(combined, profile.ai_signals, _PROPRIETARY_KEYWORDS)
    if kw_count >= 3:
        base += 50
        reasons.append(f"strong proprietary signals ({kw_count}, +50)")
    elif kw_count >= 1:
        base += 35
        reasons.append(f"proprietary signals found ({kw_count}, +35)")
    else:
        reasons.append("no proprietary signals found")

    if "exclusive" in combined.lower() or "exclusivo" in combined.lower():
        base += 15
        reasons.append("exclusive data mention (+15)")

    if "dados propriet" in sig_text.lower():
        base += 15
        reasons.append("dados proprietarios in signals (+15)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return DimensionScore(
        dimension_name="proprietary_data",
        weight=DEFENSIBILITY_WEIGHTS["proprietary_data"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_workflow_integration(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> DimensionScore:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_WORKFLOW)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 0
    reasons: list[str] = []

    if profile.customers:
        base += 25
        reasons.append(f"customers found ({len(profile.customers)}, +25)")

    kw = _WORKFLOW_KEYWORDS
    wk_count = _count_keyword_matches(combined, profile.ai_signals, kw)
    if wk_count >= 2:
        base += 35
        reasons.append(f"workflow signals ({wk_count}, +35)")
    elif wk_count >= 1:
        base += 20
        reasons.append(f"workflow signal found ({wk_count}, +20)")

    if "enterprise" in combined.lower() or "api" in combined.lower():
        base += 15
        reasons.append("enterprise/API mention (+15)")

    if "integration" in combined.lower() or "integracao" in combined.lower():
        base += 10
        reasons.append("integration mention (+10)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return DimensionScore(
        dimension_name="workflow_integration",
        weight=DEFENSIBILITY_WEIGHTS["workflow_integration"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_real_usage_learning(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> DimensionScore:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_REAL_USAGE)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 0
    reasons: list[str] = []

    if profile.customers:
        n = len(profile.customers)
        if n >= 3:
            base += 50
            reasons.append(f"customers ({n}, +50)")
        else:
            base += 30
            reasons.append(f"customer found ({n}, +30)")

    if profile.funding_signals:
        base += 20
        reasons.append(f"funding signals ({len(profile.funding_signals)}, +20)")

    kw_count = _count_keyword_matches(combined, profile.ai_signals, _REAL_USAGE_KEYWORDS)
    if kw_count >= 2:
        base += 20
        reasons.append(f"production/feedback signals ({kw_count}, +20)")
    elif kw_count >= 1:
        base += 10
        reasons.append(f"production/feedback signal ({kw_count}, +10)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return DimensionScore(
        dimension_name="real_usage_learning",
        weight=DEFENSIBILITY_WEIGHTS["real_usage"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_replication_complexity(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> DimensionScore:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_REPLICATION)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 10
    reasons: list[str] = ["base (10)"]

    if profile.sector not in ("Technology", "Not verified", "", "N/A"):
        base += 25
        reasons.append(f"verticalized sector '{profile.sector}' (+25)")

    pd_count = _count_keyword_matches(combined, profile.ai_signals, _PROPRIETARY_KEYWORDS)
    if pd_count >= 2:
        base += 25
        reasons.append(f"proprietary data ({pd_count}, +25)")
    elif pd_count >= 1:
        base += 15
        reasons.append(f"proprietary hint ({pd_count}, +15)")

    cm_count = _count_keyword_matches(combined, profile.ai_signals, _CUSTOM_MODEL_KEYWORDS)
    if cm_count >= 1:
        base += 15
        reasons.append(f"custom model signals ({cm_count}, +15)")

    if len(profile.tech_stack_signals) >= 3:
        base += 10
        reasons.append("diverse tech stack (+10)")

    if profile.funding_signals:
        base += 10
        reasons.append("funding (+10)")

    ext_count = _count_keyword_matches(combined, profile.ai_signals, _EXTERNAL_API_KEYWORDS)
    if ext_count >= 1:
        base -= 25
        reasons.append(f"external API dependency penalty ({ext_count}, -25)")

    raw = max(min(base, 100), 0)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return DimensionScore(
        dimension_name="replication_complexity",
        weight=DEFENSIBILITY_WEIGHTS["replication_barrier"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


def _score_nvidia_fit_potential(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> DimensionScore:
    evidence = _filter_evidence(validated_evidence, _EVIDENCE_NVIDIA_FIT)
    factor, conf = _evidence_confidence_penalty(evidence)
    combined = f"{profile.product_summary} {profile.description}"

    base = 0
    reasons: list[str] = []

    if profile.sector in _PRIORITY_SECTORS:
        base += 25
        reasons.append(f"priority sector '{profile.sector}' (+25)")

    gpu_count = _count_keyword_matches(combined, profile.tech_stack_signals, _NVIDIA_TECH_KEYWORDS)
    if gpu_count >= 2:
        base += 30
        reasons.append(f"NVIDIA-compatible tech ({gpu_count}, +30)")
    elif gpu_count >= 1:
        base += 20
        reasons.append(f"NVIDIA-compatible tech ({gpu_count}, +20)")

    inf_count = _count_keyword_matches(combined, profile.ai_signals, _INFERENCE_KEYWORDS)
    if inf_count >= 2:
        base += 15
        reasons.append(f"inference optimization signals ({inf_count}, +15)")
    elif inf_count >= 1:
        base += 10
        reasons.append(f"inference signal ({inf_count}, +10)")

    cv_count = _count_keyword_matches(combined, profile.ai_signals, _CV_KEYWORDS)
    if cv_count >= 1:
        base += 10
        reasons.append("computer vision signal (+10)")

    llm_count = _count_keyword_matches(combined, profile.ai_signals, _LLM_KEYWORDS)
    if llm_count >= 1:
        base += 10
        reasons.append("LLM signal (+10)")

    gov_count = _count_keyword_matches(combined, profile.ai_signals, _GOVERNANCE_KEYWORDS)
    if gov_count >= 1:
        base += 10
        reasons.append(f"governance/security signal ({gov_count}, +10)")

    raw = min(base, 100)
    adjusted = round(raw * factor, 1)

    reasoning = "; ".join(reasons) + f" Raw: {raw}, adjusted: {adjusted} (factor {factor:.2f})."

    return DimensionScore(
        dimension_name="nvidia_fit_potential",
        weight=DEFENSIBILITY_WEIGHTS["nvidia_fit"],
        raw_score=raw,
        adjusted_score=adjusted,
        confidence=conf,
        reasoning=reasoning,
        evidence_used=evidence,
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def compute_defensibility_score(
    profile: StartupProfile,
    classification: ClassificationResult,
    validated_evidence: list[ValidatedEvidence],
) -> DefensibilityScoreResult:
    """Compute the AI-Native Defensibility Score (0–100).

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
    DefensibilityScoreResult
        Total score, per-dimension breakdown, confidence, reasoning,
        evidence used, and list of missing evidence.
    """
    scores: dict[str, DimensionScore] = {}

    scores["ai_core_dependency"] = _score_ai_core_dependency(profile, classification, validated_evidence)
    scores["proprietary_data"] = _score_proprietary_data(profile, classification, validated_evidence)
    scores["workflow_integration"] = _score_workflow_integration(profile, classification, validated_evidence)
    scores["real_usage_learning"] = _score_real_usage_learning(profile, classification, validated_evidence)
    scores["replication_complexity"] = _score_replication_complexity(profile, classification, validated_evidence)
    scores["nvidia_fit_potential"] = _score_nvidia_fit_potential(profile, classification, validated_evidence)

    total = sum(s.adjusted_score * s.weight for s in scores.values())
    total = round(total, 1)

    all_evidence: list[ValidatedEvidence] = []
    missing: list[str] = []
    for name, ds in scores.items():
        all_evidence.extend(ds.evidence_used)
        if not ds.evidence_used:
            missing.append(f"No evidence for dimension: {name}")
        elif ds.confidence == ConfidenceLevel.LOW:
            missing.append(f"Weak evidence for dimension: {name} (confidence: {ds.confidence.value})")

    conf_factors = [CONFIDENCE_SCORE_FACTORS.get(s.confidence.value, 0.4) for s in scores.values()]
    avg_conf = sum(conf_factors) / len(conf_factors)

    if avg_conf >= 0.8:
        overall_conf = ConfidenceLevel.HIGH
    elif avg_conf >= 0.5:
        overall_conf = ConfidenceLevel.MEDIUM
    else:
        overall_conf = ConfidenceLevel.LOW

    classification_boost = {
        AINativeLevel.NON_AI: "Non-AI: no defensibility signal",
        AINativeLevel.AI_ASSISTED: "AI-assisted: low defensibility",
        AINativeLevel.AI_ENABLED: "AI-enabled: moderate defensibility potential",
        AINativeLevel.AI_NATIVE: "AI-native: strong defensibility base (+20)",
        AINativeLevel.AI_NATIVE_SERVICE: "AI-native service: strongest defensibility (+25)",
    }.get(classification.classification, "")

    lines = [
        f"Total Score: {total}/100 (confidence: {overall_conf.value})",
        classification_boost,
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

    return DefensibilityScoreResult(
        total_score=total,
        score_breakdown=scores,
        confidence=overall_conf,
        classification_boost=classification_boost,
        reasoning=reasoning,
        evidence_used=all_evidence,
        missing_evidence=missing,
    )
