"""Gap Diagnosis + NVIDIA Mapping package.

Deterministic detection of production AI gaps and mapping to NVIDIA technologies.
"""

from src.diagnosis.gap_diagnosis import diagnose_gaps
from src.diagnosis.nvidia_mapping import build_technology_candidates, map_gap_to_technologies
from src.diagnosis.schemas import (
    EvidenceTag,
    GapDiagnosisResult,
    GapWithEvidence,
    NvidiaTechnologyCandidate,
)

__all__ = [
    "EvidenceTag",
    "GapDiagnosisResult",
    "GapWithEvidence",
    "NvidiaTechnologyCandidate",
    "build_technology_candidates",
    "diagnose_gaps",
    "map_gap_to_technologies",
]
