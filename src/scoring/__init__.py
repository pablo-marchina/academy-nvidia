"""Deterministic scoring — defensibility, inception fit, production readiness, composite ranking, startup scoring."""

from src.scoring.composite_ranking import (
    CompositeResult,
    RankedStartup,
    build_ranked_list,
    compute_composite_score,
)
from src.scoring.defensibility_score import (
    DefensibilityScoreResult,
    DimensionScore,
    compute_defensibility_score,
)
from src.scoring.evidence_confidence import (
    EvidenceConfidenceFeatures,
    EvidenceConfidenceScoreResult,
    ScoreCalibrationStatus as ECS_CalibrationStatus,
    ScoreStatus as ECS_ScoreStatus,
    compute_evidence_confidence_score,
    extract_evidence_confidence_features,
)
from src.scoring.inception_fit_score import (
    InceptionFitDimension,
    InceptionFitScoreResult,
    compute_inception_fit_score,
)
from src.scoring.production_readiness import (
    ProductionReadinessResult,
    ReadinessDimension,
    compute_production_readiness,
)
from src.scoring.source_quality import (
    ScoreCalibrationStatus as SQS_CalibrationStatus,
    ScoreStatus as SQS_ScoreStatus,
    SourceQualityFeatures,
    SourceQualityScoreResult,
    compute_source_quality_score,
    extract_source_quality_features,
)
from src.scoring.startup_scoring import (
    NvidiaFitFeatures,
    ScoreComponent,
    ScoreStatus as SS_ScoreStatus,
    StartupScoreResult,
    StartupScoringFeatures,
    StartupScoringSummary,
    build_scoring_summary,
    compute_startup_scoring,
    extract_ai_native_features,
    extract_nvidia_fit_features,
)

__all__ = [
    "CompositeResult",
    "DefensibilityScoreResult",
    "DimensionScore",
    "ECS_CalibrationStatus",
    "ECS_ScoreStatus",
    "EvidenceConfidenceFeatures",
    "EvidenceConfidenceScoreResult",
    "InceptionFitDimension",
    "InceptionFitScoreResult",
    "NvidiaFitFeatures",
    "ProductionReadinessResult",
    "RankedStartup",
    "ReadinessDimension",
    "ScoreComponent",
    "SQS_CalibrationStatus",
    "SQS_ScoreStatus",
    "SS_ScoreStatus",
    "SourceQualityFeatures",
    "SourceQualityScoreResult",
    "StartupScoreResult",
    "StartupScoringFeatures",
    "StartupScoringSummary",
    "build_ranked_list",
    "build_scoring_summary",
    "compute_composite_score",
    "compute_defensibility_score",
    "compute_evidence_confidence_score",
    "compute_inception_fit_score",
    "compute_production_readiness",
    "compute_source_quality_score",
    "compute_startup_scoring",
    "extract_ai_native_features",
    "extract_evidence_confidence_features",
    "extract_nvidia_fit_features",
    "extract_source_quality_features",
]
