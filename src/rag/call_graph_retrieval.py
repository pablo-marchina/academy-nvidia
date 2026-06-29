"""call graph retrieval

Hypothesis: Evaluate whether call graph retrieval improves final product output without paid dependency.
Category: 8.48 Software V and V
Expected runtime use: candidate_or_supporting_governance
"""

from __future__ import annotations

from typing import Any

from src.rag.schemas import RetrievedContext


class CallGraphRetrieval:
    """call graph retrieval"""

    def __init__(self, config: Any | None = None) -> None:
        self.config = config or {}

    def run(self, contexts: list[RetrievedContext], **kwargs: Any) -> list[RetrievedContext]:
        return self._apply(contexts, **kwargs)

    def _apply(self, contexts: list[RetrievedContext], **kwargs: Any) -> list[RetrievedContext]:
        if not getattr(self, "_call_graph", None):
            self._call_graph: dict[str, list[str]] = {}

        import re as _re

        for ctx in contexts:
            calls = _re.findall(r"\b(\w+)\(", ctx.content)

            self._call_graph[ctx.chunk_id] = calls

            call_count = len(calls)

            if call_count:
                ctx.relevance_score = min(1.0, ctx.relevance_score + min(call_count * 0.01, 0.15))

        return contexts
