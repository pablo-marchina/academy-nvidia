"""Pipeline orchestrator — coordinates extraction, classification, validation, scoring,
ranking, gap diagnosis, NVIDIA mapping, and recommendation into a single deterministic flow."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.classification.ai_native_classifier import (
    ClassificationResult,
    classify_ai_native,
)
from src.diagnosis import (
    GapDiagnosisResult,
    build_technology_candidates,
    diagnose_gaps,
)
from src.extraction.extractor import extract_profile
from src.extraction.schemas import Evidence, StartupProfile
from src.rag.embeddings import EmbeddingProvider
from src.rag.rag_pipeline import run_rag_pipeline
from src.rag.retrieval import ChunkIndex
from src.rag.schemas import PackingConfig, RagPipelineOutput, RerankingConfig
from src.rag.vector_store import InMemoryVectorStore
from src.recommendation import RecommendationResult, build_recommendations
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
    gap_diagnosis: GapDiagnosisResult | None = None
    recommendation: RecommendationResult | None = None
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    rag_output: RagPipelineOutput | None = None


def run_full_pipeline(
    startup_name: str,
    raw_text: str | None = None,
    url: str = "https://example.com",
    profile: StartupProfile | None = None,
    evidence_list: list[Evidence] | None = None,
    chunk_index: ChunkIndex | None = None,
    embedding_model: EmbeddingProvider | None = None,
    vector_store: InMemoryVectorStore | None = None,
    reranking_config: RerankingConfig | None = None,
    packing_config: PackingConfig | None = None,
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
      8. Gap Diagnosis
      9. NVIDIA Technology Mapping
     10. Deterministic Recommendation Engine
     11. Product RAG (optional — hybrid retrieval, reranking, context packing)

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
    chunk_index:
        Lexical index for RAG. If None, tries ``build_default_index()``.
    embedding_model:
        Embedding provider for semantic RAG. If None, lexical fallback.
    vector_store:
        Vector store for semantic RAG. If None or empty, lexical fallback.
    reranking_config:
        Reranking weights. If None, reranking is skipped.
    packing_config:
        Packing limits. If None, packing is skipped.

    Returns
    -------
    PipelineResult
        All intermediate and final outputs including gaps, recommendations,
        and (optionally) RAG output.
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

    # Step 8: Gap Diagnosis
    gap_diag = diagnose_gaps(
        startup_name=startup_name,
        profile=profile,
        classification=classification,
        validated_evidence=validated_evidence,
        production_readiness=production_readiness,
        defensibility=defensibility,
        inception_fit=inception_fit,
    )

    # Step 9: NVIDIA Technology Mapping
    candidates = build_technology_candidates(gap_diag.diagnosed_gaps)
    gap_diagnosis = gap_diag.model_copy(update={"nvidia_technology_candidates": candidates})

    # Step 10: Deterministic Recommendation Engine
    recommendation = build_recommendations(
        startup_name=startup_name,
        profile=profile,
        classification=classification,
        validated_evidence=validated_evidence,
        defensibility=defensibility,
        inception_fit=inception_fit,
        production_readiness=production_readiness,
        composite=composite,
        final_priority_score=final_priority_score,
        recommended_motion=recommended_motion,
        gap_diagnosis=gap_diagnosis,
    )

    # Step 11: Product RAG (optional)
    rag_output = None
    if gap_diagnosis is not None:
        rag_output = run_rag_pipeline(
            gap_diagnosis=gap_diagnosis,
            chunk_index=chunk_index,
            embedding_model=embedding_model,
            vector_store=vector_store,
            reranking_config=reranking_config,
            packing_config=packing_config,
        )

    # Aggregate evidence_used and missing_evidence
    all_missing: list[str] = list(defensibility.missing_evidence)
    all_missing.extend(inception_fit.missing_evidence)
    all_missing.extend(production_readiness.missing_evidence)
    all_missing.extend(gap_diagnosis.missing_evidence)
    all_missing.extend(recommendation.missing_evidence)

    all_evidence: list[ValidatedEvidence] = list(defensibility.evidence_used)
    all_evidence.extend(inception_fit.evidence_used)
    all_evidence.extend(production_readiness.evidence_used)
    all_evidence.extend(gap_diagnosis.evidence_used)
    all_evidence.extend(recommendation.evidence_used)

    def_total = defensibility.total_score
    def_conf = defensibility.confidence.value
    inc_total = inception_fit.total_score
    inc_conf = inception_fit.confidence.value
    pr_score = production_readiness.production_readiness_score
    pr_conf = production_readiness.confidence.value
    comp_score = composite.composite_score
    comp_conf = composite.confidence.value
    detected_gaps = len([g for g in gap_diagnosis.diagnosed_gaps if g.detected])
    rec_count = len(recommendation.recommendations)
    lines: list[str] = [
        f"Pipeline complete for {startup_name}",
        f"  Defensibility: {def_total}/100 ({def_conf})",
        f"  Inception Fit: {inc_total}/100 ({inc_conf})",
        f"  Production Readiness: {pr_score}/100 ({pr_conf})",
        f"  Composite: {comp_score}/100 ({comp_conf})",
        f"  Motion: {recommended_motion}",
        f"  Gaps detected: {detected_gaps}",
        f"  Recommendations: {rec_count}",
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
        gap_diagnosis=gap_diagnosis,
        recommendation=recommendation,
        reasoning="\n".join(lines),
        evidence_used=all_evidence,
        missing_evidence=all_missing,
        rag_output=rag_output,
    )
