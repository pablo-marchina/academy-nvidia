from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UtilityCandidate:
    candidate_id: str
    expected_value: float
    confidence: float
    implementation_complexity: float
    risk: float = 0.0


def expected_utility(candidate: UtilityCandidate) -> float:
    value = candidate.expected_value * candidate.confidence
    cost = candidate.implementation_complexity * 0.25 + candidate.risk * 0.25
    return round(max(0.0, value - cost), 4)


def rank_by_expected_utility(candidates: list[UtilityCandidate]) -> list[UtilityCandidate]:
    return sorted(candidates, key=expected_utility, reverse=True)
