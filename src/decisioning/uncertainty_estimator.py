from __future__ import annotations


def estimate_uncertainty(*, evidence_count: int, contradiction_count: int = 0, source_diversity: int = 1) -> float:
    evidence_factor = min(1.0, evidence_count / 6)
    diversity_factor = min(1.0, source_diversity / 3)
    contradiction_penalty = min(0.5, contradiction_count * 0.15)
    uncertainty = 1.0 - (evidence_factor * 0.6 + diversity_factor * 0.4) + contradiction_penalty
    return round(max(0.0, min(1.0, uncertainty)), 4)
