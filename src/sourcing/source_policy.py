from __future__ import annotations

from pydantic import BaseModel, Field

from src.sourcing.source_registry import SourceCategory


class SourcePolicy(BaseModel):
    category: SourceCategory
    robots_required: bool = True
    tos_required: bool = True
    public_only: bool = True
    allow_authenticated_scraping: bool = False
    rate_limit_per_minute: int = Field(default=6, ge=1)
    user_agent_required: bool = True
    blocked_means_failed: bool = True


def policy_for_category(category: SourceCategory) -> SourcePolicy:
    if category in {SourceCategory.NVIDIA_OFFICIAL, SourceCategory.NVIDIA_DOCS, SourceCategory.CASE_MATERIAL}:
        return SourcePolicy(category=category, rate_limit_per_minute=12)
    if category in {SourceCategory.LINKEDIN_PUBLIC, SourceCategory.GITHUB_PUBLIC}:
        return SourcePolicy(category=category, rate_limit_per_minute=3)
    return SourcePolicy(category=category)
