from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeightedFeature:
    name: str
    value: float
    weight: float
    evidence_ids: tuple[str, ...] = ()


def score_features(features: list[WeightedFeature]) -> dict[str, object]:
    total_weight = sum(max(0.0, item.weight) for item in features)
    if total_weight == 0:
        return {"score": 0.0, "features": [], "confidence": 0.0, "uncertainty": 1.0}
    weighted = sum(max(0.0, min(1.0, item.value)) * max(0.0, item.weight) for item in features)
    evidence_count = sum(len(item.evidence_ids) for item in features)
    confidence = min(1.0, evidence_count / max(1, len(features) * 2))
    score = round(weighted / total_weight, 4)
    return {
        "score": score,
        "features": [item.__dict__ for item in features],
        "confidence": round(confidence, 4),
        "uncertainty": round(1.0 - confidence, 4),
    }
