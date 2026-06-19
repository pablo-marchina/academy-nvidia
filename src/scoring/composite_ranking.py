"""Composite Ranking — confidence-aware weighted ranking with recommended motion."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from src.classification.ai_native_classifier import ClassificationResult
from src.extraction.schemas import AINativeLevel, ConfidenceLevel
from src.quantitative.params import (
    CLASSIFICATION_TO_BASE_SCORE,
    CONFIDENCE_PENALTY_ON_MISSING,
    OPPORTUNITY_SCORE_WEIGHTS,
)
from src.scoring.defensibility_score import DefensibilityScoreResult
from src.scoring.inception_fit_score import InceptionFitScoreResult
from src.scoring.production_readiness import ProductionReadinessResult

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class CompositeResult(BaseModel):
    startup_id: str
    composite_score: float
    defensibility_score: float
    inception_fit_score: float
    production_readiness_score: float
    classification_score: float
    confidence: ConfidenceLevel
    confidence_penalty_applied: float
    missing_components: list[str] = Field(default_factory=list)
    reasoning: str


MotionHint = Literal[
    "immediate_outreach",
    "high_priority_outreach",
    "monitor_and_nurture",
    "lack_evidence_more_research",
    "not_recommended",
]


class RankedStartup(BaseModel):
    startup_id: str
    startup_name: str
    sector: str
    composite_score: float
    confidence: ConfidenceLevel
    motion: MotionHint
    reasoning: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_from_classification(result: ClassificationResult) -> float:
    return CLASSIFICATION_TO_BASE_SCORE.get(result.classification.value, 0)


def _compute_confidence_penalty(
    ds: DefensibilityScoreResult | None,
    isr: InceptionFitScoreResult | None,
    pr: ProductionReadinessResult | None,
    classification_result: ClassificationResult | None,
) -> tuple[float, list[str]]:
    """Compute the global confidence penalty (0.0 = no penalty)."""
    penalty = 0.0
    missing: list[str] = []

    if ds is None:
        missing.append("defensibility_score")
        penalty += CONFIDENCE_PENALTY_ON_MISSING
    elif ds.confidence == ConfidenceLevel.LOW:
        penalty += 0.05

    if isr is None:
        missing.append("inception_fit_score")
        penalty += CONFIDENCE_PENALTY_ON_MISSING
    elif isr.confidence == ConfidenceLevel.LOW:
        penalty += 0.05

    if pr is None:
        missing.append("production_readiness")
        penalty += CONFIDENCE_PENALTY_ON_MISSING
    elif pr.confidence == ConfidenceLevel.LOW:
        penalty += 0.05

    if classification_result is None:
        missing.append("classification")
        penalty += 0.10
    elif classification_result.classification in (
        AINativeLevel.NON_AI,
        AINativeLevel.AI_ASSISTED,
    ):
        penalty += 0.05

    return min(penalty, 1.0), missing


def _determine_motion(
    score: float,
    confidence: ConfidenceLevel,
    missing_components: list[str],
    classification: ClassificationResult | None,
) -> MotionHint:
    if classification is not None and classification.classification == AINativeLevel.NON_AI:
        return "not_recommended"

    if confidence == ConfidenceLevel.LOW and len(missing_components) >= 2:
        return "lack_evidence_more_research"

    if score >= 75:
        return "immediate_outreach"
    if score >= 55:
        return "high_priority_outreach"
    if score >= 35:
        return "monitor_and_nurture"
    return "lack_evidence_more_research"


# ---------------------------------------------------------------------------
# Main entry points
# ---------------------------------------------------------------------------


def compute_composite_score(
    startup_id: str,
    defensibility: DefensibilityScoreResult | None,
    inception_fit: InceptionFitScoreResult | None,
    production_readiness: ProductionReadinessResult | None,
    classification_result: ClassificationResult | None,
) -> CompositeResult:
    """Aggregate all 4 pillars into a composite score, applying confidence penalties.

    If a sub-score component is *None*, its weight is redistributed to the
    remaining non-None components proportionally.
    """
    components: list[tuple[str, float | None, float]] = [
        (
            "defensibility",
            defensibility.total_score if defensibility else None,
            OPPORTUNITY_SCORE_WEIGHTS["defensibility"],
        ),
        (
            "inception_fit",
            inception_fit.total_score if inception_fit else None,
            OPPORTUNITY_SCORE_WEIGHTS["inception_fit"],
        ),
        (
            "production_readiness",
            production_readiness.production_readiness_score if production_readiness else None,
            OPPORTUNITY_SCORE_WEIGHTS["production_readiness"],
        ),
        (
            "classification",
            _score_from_classification(classification_result) if classification_result else None,
            OPPORTUNITY_SCORE_WEIGHTS["classification"],
        ),
    ]

    present = [(name, val, w) for name, val, w in components if val is not None]
    total_weight = sum(w for _, _, w in present)

    if not present or total_weight == 0:
        return CompositeResult(
            startup_id=startup_id,
            composite_score=0.0,
            defensibility_score=0.0,
            inception_fit_score=0.0,
            production_readiness_score=0.0,
            classification_score=0.0,
            confidence=ConfidenceLevel.LOW,
            confidence_penalty_applied=1.0,
            missing_components=["all"],
            reasoning="No scoring components available — composite is 0.",
        )

    raw_score = sum(val * (w / total_weight) for name, val, w in present)

    confidence_penalty, missing = _compute_confidence_penalty(
        defensibility, inception_fit, production_readiness, classification_result
    )
    composite = round(raw_score * (1 - confidence_penalty), 1)

    # Determine overall confidence
    all_vals = [v for _, v, _ in present if v is not None]
    avg_val = sum(all_vals) / len(all_vals) if all_vals else 0

    if confidence_penalty >= 0.4 or avg_val < 25:
        overall_conf = ConfidenceLevel.LOW
    elif confidence_penalty >= 0.2 or avg_val < 50:
        overall_conf = ConfidenceLevel.MEDIUM
    else:
        overall_conf = ConfidenceLevel.HIGH

    def_score = defensibility.total_score if defensibility else "N/A"
    inc_score = inception_fit.total_score if inception_fit else "N/A"
    pr_score = production_readiness.production_readiness_score if production_readiness else "N/A"
    clf_score = (
        _score_from_classification(classification_result) if classification_result else "N/A"
    )
    lines: list[str] = [
        f"Composite score: {composite}/100 (confidence: {overall_conf.value})",
        f'  defensibility ({OPPORTUNITY_SCORE_WEIGHTS["defensibility"]}): {def_score}',
        f'  inception_fit ({OPPORTUNITY_SCORE_WEIGHTS["inception_fit"]}): {inc_score}',
        f'  production_readiness ({OPPORTUNITY_SCORE_WEIGHTS["production_readiness"]}): {pr_score}',
        f'  classification ({OPPORTUNITY_SCORE_WEIGHTS["classification"]}): {clf_score}',
        f"  confidence_penalty: {confidence_penalty:.2f}",
    ]
    if missing:
        lines.append(f"  missing components: {', '.join(missing)}")

    return CompositeResult(
        startup_id=startup_id,
        composite_score=composite,
        defensibility_score=defensibility.total_score if defensibility else 0.0,
        inception_fit_score=inception_fit.total_score if inception_fit else 0.0,
        production_readiness_score=(
            production_readiness.production_readiness_score if production_readiness else 0.0
        ),
        classification_score=(
            _score_from_classification(classification_result) if classification_result else 0.0
        ),
        confidence=overall_conf,
        confidence_penalty_applied=confidence_penalty,
        missing_components=missing,
        reasoning="\n".join(lines),
    )


def build_ranked_list(
    startup_scores: list[CompositeResult],
    names: dict[str, tuple[str, str]],  # startup_id -> (name, sector)
    classifications: dict[str, ClassificationResult],
) -> list[RankedStartup]:
    """Convert CompositeResults into a ranked list with motion hints.

    Parameters
    ----------
    startup_scores:
        CompositeResult per startup.
    names:
        Mapping of startup_id to (name, sector).
    classifications:
        Mapping of startup_id to classification result (for motion decision).

    Returns
    -------
    list[RankedStartup]
        Ranked by composite_score descending.
    """
    ranked: list[RankedStartup] = []
    for cs in startup_scores:
        name, sector = names.get(cs.startup_id, ("unknown", "unknown"))
        motion = _determine_motion(
            cs.composite_score,
            cs.confidence,
            cs.missing_components,
            classifications.get(cs.startup_id),
        )
        ranked.append(
            RankedStartup(
                startup_id=cs.startup_id,
                startup_name=name,
                sector=sector,
                composite_score=cs.composite_score,
                confidence=cs.confidence,
                motion=motion,
                reasoning=cs.reasoning,
            )
        )

    ranked.sort(key=lambda r: r.composite_score, reverse=True)
    return ranked
