from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceCandidate:
    source_name: str
    source_url: str
    authority: float = 0.5
    freshness: float = 0.5
    independence: float = 0.5
    known_gap_coverage: float = 0.0


def expected_information_gain(candidate: SourceCandidate) -> float:
    novelty = 1.0 - max(0.0, min(1.0, candidate.known_gap_coverage))
    score = candidate.authority * 0.35 + candidate.freshness * 0.2 + candidate.independence * 0.2 + novelty * 0.25
    return round(max(0.0, min(1.0, score)), 4)


def select_next_sources(candidates: list[SourceCandidate], *, limit: int = 5) -> list[SourceCandidate]:
    return sorted(candidates, key=expected_information_gain, reverse=True)[:limit]


def should_stop_collection(*, confidence: float, sources_seen: int, max_sources: int = 12) -> bool:
    return confidence >= 0.85 or sources_seen >= max_sources
