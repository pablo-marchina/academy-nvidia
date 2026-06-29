"""_non-inferiority testing_

Hypothesis: Evaluate whether non-inferiority testing improves final product output.
Category: 8.28
Expected runtime use: candidate_or_supporting_governance
"""

from __future__ import annotations

from typing import Any


class NonInferiorityTesting:
    """_non-inferiority testing_"""

    def __init__(self, config: Any | None = None) -> None:
        self.config = config or {}

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "method",
            "candidate_id": "maximal__8-28-statistical-decision-science__non-inferiority-testing",
            "tool_name": "non-inferiority testing",
            "available": True,
            "issues": [],
            "recommendation": "Non-inferiority testing pattern to show a new variant is not worse than control by more than a pre-specified margin. Define margin delta and one-sided test.",
            "evidence": "Method pattern described. Implementation requires application-level configuration.",
        }
