from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class SourceCategory(str, Enum):
    OFFICIAL_SITE = "official_site"
    OFFICIAL_BLOG = "official_blog"
    CAREERS = "careers"
    PRODUCT_DOCS = "product_docs"
    LINKEDIN_PUBLIC = "linkedin_public"
    GITHUB_PUBLIC = "github_public"
    TRUSTED_NEWS = "trusted_news"
    ACCELERATOR = "accelerator"
    STARTUP_DIRECTORY = "startup_directory"
    INVESTOR_PORTFOLIO = "investor_portfolio"
    NVIDIA_OFFICIAL = "nvidia_official"
    NVIDIA_DOCS = "nvidia_docs"
    CASE_MATERIAL = "case_material"


class SourceRecord(BaseModel):
    source_id: str
    category: SourceCategory
    name: str
    url: HttpUrl | None = None
    authority_weight: float = Field(ge=0.0, le=1.0)
    expected_for_startup_analysis: bool = True
    requires_public_access_check: bool = True
    rate_limit_per_minute: int = Field(default=6, ge=1)


def default_source_registry() -> list[SourceRecord]:
    return [
        SourceRecord(source_id="official_site", category=SourceCategory.OFFICIAL_SITE, name="Startup official site", authority_weight=1.0),
        SourceRecord(source_id="official_blog", category=SourceCategory.OFFICIAL_BLOG, name="Startup official blog", authority_weight=0.9),
        SourceRecord(source_id="careers", category=SourceCategory.CAREERS, name="Startup careers page", authority_weight=0.75),
        SourceRecord(source_id="product_docs", category=SourceCategory.PRODUCT_DOCS, name="Product or technical docs", authority_weight=0.85),
        SourceRecord(source_id="linkedin_public", category=SourceCategory.LINKEDIN_PUBLIC, name="Allowed public LinkedIn page", authority_weight=0.7),
        SourceRecord(source_id="github_public", category=SourceCategory.GITHUB_PUBLIC, name="Allowed public GitHub profile", authority_weight=0.7),
        SourceRecord(source_id="trusted_news", category=SourceCategory.TRUSTED_NEWS, name="Trusted news", authority_weight=0.65),
        SourceRecord(source_id="accelerator", category=SourceCategory.ACCELERATOR, name="Accelerator profile", authority_weight=0.65),
        SourceRecord(source_id="startup_directory", category=SourceCategory.STARTUP_DIRECTORY, name="Startup directory", authority_weight=0.55),
        SourceRecord(source_id="investor_portfolio", category=SourceCategory.INVESTOR_PORTFOLIO, name="Investor or portfolio page", authority_weight=0.75),
        SourceRecord(source_id="nvidia_official", category=SourceCategory.NVIDIA_OFFICIAL, name="NVIDIA official product page", authority_weight=1.0),
        SourceRecord(source_id="nvidia_docs", category=SourceCategory.NVIDIA_DOCS, name="NVIDIA documentation", authority_weight=1.0),
        SourceRecord(source_id="case_material", category=SourceCategory.CASE_MATERIAL, name="Case material", authority_weight=0.8),
    ]
