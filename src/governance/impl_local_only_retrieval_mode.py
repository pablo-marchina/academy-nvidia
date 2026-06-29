"""_local-only retrieval mode_

Hypothesis: Evaluate whether local-only retrieval mode improves final product output.
Category: 8.25
Expected runtime use: candidate_or_supporting_governance
"""

from __future__ import annotations

from typing import Any


class LocalOnlyRetrievalMode:
    """_local-only retrieval mode_"""

    def __init__(self, config: Any | None = None) -> None:
        self.config = config or {}

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "method",
            "candidate_id": "maximal__8-25-privacy-pii-and-lgpd__local-only-retrieval-mode",
            "tool_name": "local-only retrieval mode",
            "available": True,
            "issues": [],
            "recommendation": "Local-only retrieval mode for air-gapped or offline operation. Restrict retrieval to local corpora, disable external API calls, and validate all source origins.",
            "evidence": "Method pattern described. Implementation requires application-level configuration.",
        }
