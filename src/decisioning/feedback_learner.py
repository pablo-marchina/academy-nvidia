from __future__ import annotations


def apply_feedback_weight(base_weight: float, *, positive: int = 0, negative: int = 0) -> float:
    adjustment = positive * 0.03 - negative * 0.05
    return round(max(0.0, min(1.0, base_weight + adjustment)), 4)
