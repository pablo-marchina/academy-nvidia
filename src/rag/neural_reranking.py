from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from src.rag.nvidia_client import NvidiaClient
from src.rag.schemas import RetrievedContext


class NeuralRerankerConfig(BaseModel):
    enabled: bool = True
    top_k: int = 10
    rerank_model: str = "nvidia/rerank-qa-mistral-4b"


_NVIDIA_CLIENT: NvidiaClient | None = None


def _get_nvidia() -> NvidiaClient:
    global _NVIDIA_CLIENT
    if _NVIDIA_CLIENT is None:
        _NVIDIA_CLIENT = NvidiaClient()
    return _NVIDIA_CLIENT


class NeuralReranker:
    def __init__(self, config: Any | None = None) -> None:
        self.config = NeuralRerankerConfig.model_validate(config or {})

    def run(self, contexts: list[RetrievedContext], **kwargs: Any) -> list[RetrievedContext]:
        return self._apply(contexts, **kwargs)

    def _apply(self, contexts: list[RetrievedContext], **kwargs: Any) -> list[RetrievedContext]:
        query: str = kwargs.get("query", "")
        if not contexts or not query:
            return contexts

            candidates = sorted(contexts, key=lambda c: c.relevance_score, reverse=True)[: self.config.top_k]
            client = _get_nvidia()
            passages = [c.content[:1000] for c in candidates]
            rankings = client.rerank(query, passages, model=self.config.rerank_model)
            if rankings is not None:
                for idx, logit in rankings:
                    if idx < len(candidates):
                        candidates[idx].relevance_score = round(logit, 4)

                        result = sorted(candidates, key=lambda c: c.relevance_score, reverse=True)

                        other = [c for c in contexts if c.chunk_id not in {cc.chunk_id for cc in result}]

                        return result + other

                        content_lower = query.lower()
                        for ctx in candidates:
                            overlap = sum(1 for w in content_lower.split() if w in ctx.content.lower())

                            ctx.relevance_score = round(
                                min(ctx.relevance_score + (overlap / max(len(content_lower.split()), 1)) * 0.2, 1.0), 4
                            )

        return contexts
