"""Schemas for gap diagnosis and NVIDIA technology mapping."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from src.extraction.schemas import ConfidenceLevel, TechnicalGap
from src.validation.evidence_validator import ValidatedEvidence


class EvidenceTag(StrEnum):
    FACT = "fact"
    INFERRED = "inferred"
    HYPOTHESIS = "hypothesis"


class GapWithEvidence(BaseModel):
    gap: TechnicalGap
    detected: bool
    confidence: ConfidenceLevel
    evidence_tag: EvidenceTag
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)


class NvidiaTechnologyCandidate(BaseModel):
    technology_name: str
    addresses_gap: TechnicalGap
    justification: str


class GapDiagnosisResult(BaseModel):
    startup_name: str
    diagnosed_gaps: list[GapWithEvidence]
    nvidia_technology_candidates: list[NvidiaTechnologyCandidate] = Field(default_factory=list)
    confidence: ConfidenceLevel
    reasoning: str
    evidence_used: list[ValidatedEvidence] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
