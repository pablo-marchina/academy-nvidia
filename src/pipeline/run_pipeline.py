"""Pipeline orchestrator — coordinates extraction, classification, validation, scoring,
and ranking into a single deterministic flow."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.classification.ai_native_classifier import (
    ClassificationResult,
    classify_ai_native,
)
from src.extraction.extractor import extract_profile
from src.extraction.schemas import Evidence, StartupProfile
from src.scoring.composite_ranking import (
    CompositeResult,
    RankedStartup,
    build_ranked_list,
    compute_composite_score,
)
from src.scoring.defensibility_score import (
    DefensibilityScoreResult,
    compute_defensibility_score,
)
from src.scoring.inception_fit_score import (
    InceptionFitScoreResult,
    compute_inception_fit_score,
)
from src.scoring.production_readiness import (
    ProductionReadinessResult,
    compute_production_readiness,
)
from src.validation.evidence_validator import (
    ValidatedEvidence,
    validate_evidence_batch,
)


class PipelineResult(BaseModel):
    startup_name: str
    startup_profile: StartupProfile
    ai_native_classification: ClassificationResult
    validated_evidence: list[ValidatedEvidence]
    defensibility_score: DefensibilityScoreResult
    inception_fit_score: InceptionFitScoreResult
    production_readiness_score: ProductionReadinessResult
    composite_score: CompositeResult
    ranked: list[RankedStartup]
    final_priority_score: float
    recommended_motion: str
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)


def run_full_pipeline(
    startup_name: str,
    raw_text: str | None = None,
    url: str = "https://example.com",
    profile: StartupProfile | None = None,
    evidence_list: list[Evidence] | None = None,
) -> PipelineResult:
    """Execute the full Startup AI Radar pipeline.

    Pipeline order:
      1. Extraction (if raw_text is provided)
      2. AI-native classification
      3. Evidence validation
      4. AI-Native Defensibility Score
      5. NVIDIA Inception Fit Score
      6. Production AI Readiness
      7. Composite Score + Confidence-aware Ranking

    Parameters
    ----------
    startup_name:
        Name of the startup (used as a hint for extraction and as ID).
    raw_text:
        Raw scraped text to extract a profile from. If None, *profile* must
        be provided.
    url:
        Source URL for extraction metadata.
    profile:
        Pre-extracted StartupProfile. If None, *raw_text* must be provided.
    evidence_list:
        Raw Evidence objects to validate. If None, extracted from
        *profile* sources.

    Returns
    -------
    PipelineResult
        All intermediate and final outputs.
    """
    # Step 1: Extraction
    if profile is None:
        if raw_text is None:
            raise ValueError("Either raw_text or profile must be provided.")
        profile = extract_profile(
            clean_text=raw_text,
            url=url,
            startup_name_hint=startup_name,
        )

    # Step 2: AI-native classification
    classification = classify_ai_native(profile)

    # Step 3: Evidence validation
    raw_evidence = evidence_list if evidence_list is not None else profile.sources
    validated_evidence = validate_evidence_batch(raw_evidence)

    # Step 4: AI-Native Defensibility Score
    defensibility = compute_defensibility_score(profile, classification, validated_evidence)

    # Step 5: NVIDIA Inception Fit Score
    inception_fit = compute_inception_fit_score(
        profile,
        classification,
        defensibility.total_score,
        validated_evidence,
    )

    # Step 6: Production AI Readiness
    production_readiness = compute_production_readiness(
        profile,
        classification,
        validated_evidence,
    )

    # Step 7: Composite Score + Ranking
    composite = compute_composite_score(
        startup_id=startup_name,
        defensibility=defensibility,
        inception_fit=inception_fit,
        production_readiness=production_readiness,
        classification_result=classification,
    )

    names = {startup_name: (profile.startup_name, profile.sector)}
    classifications = {startup_name: classification}
    ranked = build_ranked_list([composite], names, classifications)

    top = ranked[0] if ranked else None
    final_priority_score = top.composite_score if top else 0.0
    recommended_motion = top.motion if top else "lack_evidence_more_research"

    all_missing: list[str] = list(defensibility.missing_evidence)
    all_missing.extend(inception_fit.missing_evidence)
    all_missing.extend(production_readiness.missing_evidence)

    all_evidence: list[ValidatedEvidence] = list(defensibility.evidence_used)
    all_evidence.extend(inception_fit.evidence_used)
    all_evidence.extend(production_readiness.evidence_used)

    def_total = defensibility.total_score
    def_conf = defensibility.confidence.value
    inc_total = inception_fit.total_score
    inc_conf = inception_fit.confidence.value
    pr_score = production_readiness.production_readiness_score
    pr_conf = production_readiness.confidence.value
    comp_score = composite.composite_score
    comp_conf = composite.confidence.value
    lines: list[str] = [
        f"Pipeline complete for {startup_name}",
        f"  Defensibility: {def_total}/100 ({def_conf})",
        f"  Inception Fit: {inc_total}/100 ({inc_conf})",
        f"  Production Readiness: {pr_score}/100 ({pr_conf})",
        f"  Composite: {comp_score}/100 ({comp_conf})",
        f"  Motion: {recommended_motion}",
        f"  Gaps: {len(inception_fit.detected_gaps)}",
    ]
    if all_missing:
        lines.append(f"  Missing evidence items: {len(all_missing)}")

    return PipelineResult(
        startup_name=startup_name,
        startup_profile=profile,
        ai_native_classification=classification,
        validated_evidence=validated_evidence,
        defensibility_score=defensibility,
        inception_fit_score=inception_fit,
        production_readiness_score=production_readiness,
        composite_score=composite,
        ranked=ranked,
        final_priority_score=final_priority_score,
        recommended_motion=recommended_motion,
        reasoning="\n".join(lines),
        evidence_used=all_evidence,
        missing_evidence=all_missing,
    )
