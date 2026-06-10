from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from src.extraction.schemas import ConfidenceLevel
from src.rag.schemas import DroppedContext, PackedContext, SupportingNvidiaContext


class BriefVerdict(StrEnum):
    HIGH_PRIORITY = "high_priority"
    PROMISING = "promising"
    EARLY_STAGE = "early_stage"
    NEEDS_VALIDATION = "needs_validation"
    NOT_RECOMMENDED = "not_recommended"


class BriefUncertainty(BaseModel):
    description: str
    source: str
    impact: str


class BriefEvidenceItem(BaseModel):
    claim: str
    tag: str
    confidence: str
    source_url: str
    source_type: str


class BriefSection(BaseModel):
    title: str
    content: str
    items: list[BriefEvidenceItem] = Field(default_factory=list)


class StartupActionBrief(BaseModel):
    startup_name: str
    website: str
    sector: str
    one_line_summary: str
    verdict: BriefVerdict
    final_priority_score: float
    recommended_motion: str
    confidence: ConfidenceLevel
    sections: list[BriefSection]
    ai_native_classification: dict
    defensibility_score: dict
    inception_fit_score: dict
    production_readiness_score: dict
    composite_score: dict
    diagnosed_gaps: list[dict]
    nvidia_technology_candidates: list[dict]
    recommendations: list[dict]
    evidence_used: list[BriefEvidenceItem]
    missing_evidence: list[str]
    uncertainties: list[BriefUncertainty]
    next_action_for_nvidia_team: str
    reasoning: str
    # Epic 14 — optional RAG context
    packed_rag_contexts: list[PackedContext] = Field(default_factory=list)
    supporting_nvidia_context: list[SupportingNvidiaContext] = Field(default_factory=list)
    dropped_contexts_debug: list[DroppedContext] = Field(default_factory=list)
