"""Recommendation engine — deterministic gap-based NVIDIA technology recommendations."""

from src.recommendation.recommendation_engine import build_recommendations
from src.recommendation.schemas import (
    PerGapRecommendation,
    RecommendationResult,
    RecommendedNextAction,
    SuggestedTechnicalExperiment,
)

__all__ = [
    "build_recommendations",
    "PerGapRecommendation",
    "RecommendationResult",
    "RecommendedNextAction",
    "SuggestedTechnicalExperiment",
]
