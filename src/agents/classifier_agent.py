"""Classify and score a startup profile using scoring services."""

from __future__ import annotations

from typing import Any


def score_startup(
    profile_dict: dict[str, Any] | None,
    validated_evidence_dicts: list[dict[str, Any]],
    run_id: str,
) -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any],
    dict[str, Any], dict[str, Any], list[str],
]:
    from src.classification.ai_native_classifier import classify_ai_native
    from src.extraction.schemas import StartupProfile
    from src.scoring.composite_ranking import compute_composite_score
    from src.scoring.defensibility_score import compute_defensibility_score
    from src.scoring.inception_fit_score import compute_inception_fit_score
    from src.scoring.production_readiness import compute_production_readiness
    from src.validation.evidence_validator import ValidatedEvidence

    errors: list[str] = []
    scores: dict[str, Any] = {}
    classification_result: dict[str, Any] = {}
    defensibility_result: dict[str, Any] = {}
    inception_fit_result: dict[str, Any] = {}
    production_readiness_result: dict[str, Any] = {}

    if not profile_dict:
        return (
            scores, classification_result,
            defensibility_result, inception_fit_result,
            production_readiness_result, errors,
        )

    try:
        profile = StartupProfile.model_validate(profile_dict)
    except Exception as exc:
        return (
            scores, classification_result,
            defensibility_result, inception_fit_result,
            production_readiness_result,
            [f"Failed to deserialize startup_profile: {exc}"],
        )

    validated_evidence_objs: list[ValidatedEvidence] = []
    for ev_dict in validated_evidence_dicts:
        try:
            validated_evidence_objs.append(ValidatedEvidence.model_validate(ev_dict))
        except Exception as exc:
            errors.append(f"Failed to deserialize validated_evidence: {exc}")

    classification = classify_ai_native(profile)

    defensibility = compute_defensibility_score(profile, classification, validated_evidence_objs)
    inception_fit = compute_inception_fit_score(
        profile, classification, defensibility.total_score, validated_evidence_objs
    )
    production_readiness = compute_production_readiness(
        profile, classification, validated_evidence_objs
    )
    composite = compute_composite_score(
        startup_id=run_id,
        defensibility=defensibility,
        inception_fit=inception_fit,
        production_readiness=production_readiness,
        classification_result=classification,
    )

    scores = {
        "defensibility": defensibility.total_score,
        "defensibility_confidence": defensibility.confidence.value,
        "inception_fit": inception_fit.total_score,
        "inception_fit_confidence": inception_fit.confidence.value,
        "production_readiness": production_readiness.production_readiness_score,
        "production_readiness_confidence": production_readiness.confidence.value,
        "composite": composite.composite_score,
        "composite_confidence": composite.confidence.value,
        "composite_reasoning": composite.reasoning,
        "classification": classification.classification.value,
        "classification_confidence": classification.confidence.value,
    }

    classification_result = classification.model_dump(mode="json")
    defensibility_result = defensibility.model_dump(mode="json")
    inception_fit_result = inception_fit.model_dump(mode="json")
    production_readiness_result = production_readiness.model_dump(mode="json")

    return (
        scores, classification_result,
        defensibility_result, inception_fit_result,
        production_readiness_result, errors,
    )
