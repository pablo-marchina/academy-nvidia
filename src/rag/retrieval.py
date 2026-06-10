"""Lexical retrieval over NVIDIA corpus chunks."""

from __future__ import annotations

from src.rag.ingestion import load_and_chunk_corpus
from src.rag.schemas import RagChunk, RetrievalQuery, RetrievedContext

_DEFAULT_TOP_K = 3


class ChunkIndex:
    """In-memory index over corpus chunks for deterministic lexical retrieval."""

    def __init__(self, chunks: list[RagChunk] | None = None) -> None:
        self.chunks: list[RagChunk] = chunks or []
        self.by_gap: dict[str, list[RagChunk]] = {}
        self.by_tech: dict[str, list[RagChunk]] = {}
        self._rebuild()

    def _rebuild(self) -> None:
        self.by_gap.clear()
        self.by_tech.clear()
        for c in self.chunks:
            for gap in c.gap_types:
                self.by_gap.setdefault(gap, []).append(c)
            tech_key = c.product.lower()
            self.by_tech.setdefault(tech_key, []).append(c)

    def _candidates_from_query(self, query: RetrievalQuery) -> list[RagChunk]:
        seen: set[str] = set()
        result: list[RagChunk] = []

        if query.gap_type:
            for c in self.by_gap.get(query.gap_type, []):
                if c.chunk_id not in seen:
                    seen.add(c.chunk_id)
                    result.append(c)

        if query.technology:
            tech_key = query.technology.lower()
            for c in self.by_tech.get(tech_key, []):
                if c.chunk_id not in seen:
                    seen.add(c.chunk_id)
                    result.append(c)

        if not result and query.keywords:
            for c in self.chunks:
                content_lower = c.content.lower()
                product_lower = c.product.lower()
                kw_lower = query.keywords
                if any(k.lower() in content_lower or k.lower() in product_lower for k in kw_lower):
                    if c.chunk_id not in seen:
                        seen.add(c.chunk_id)
                        result.append(c)

        return result

    def retrieve(
        self,
        query: RetrievalQuery,
        top_k: int = _DEFAULT_TOP_K,
    ) -> list[RetrievedContext]:
        candidates = self._candidates_from_query(query)

        if not candidates:
            return []

        scored = [_score_chunk(c, query) for c in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_k]
        return [ctx for ctx, _ in top]

    def retrieve_by_gap_type(
        self,
        gap_type: str,
        top_k: int = _DEFAULT_TOP_K,
    ) -> list[RetrievedContext]:
        return self.retrieve(RetrievalQuery(gap_type=gap_type), top_k=top_k)

    def retrieve_by_technology(
        self,
        technology: str,
        top_k: int = _DEFAULT_TOP_K,
    ) -> list[RetrievedContext]:
        return self.retrieve(RetrievalQuery(technology=technology), top_k=top_k)


def _score_chunk(chunk: RagChunk, query: RetrievalQuery) -> tuple[RetrievedContext, float]:
    """Score a chunk's relevance to a query (0.0 to 1.0)."""
    score = 0.0
    content_lower = chunk.content.lower()
    product_lower = chunk.product.lower()

    if query.gap_type and query.gap_type in chunk.gap_types:
        score += 0.4

    if query.technology:
        q_tech = query.technology.lower()
        if q_tech in product_lower or q_tech in content_lower:
            score += 0.3

    if query.keywords:
        matched = sum(1 for kw in query.keywords if kw.lower() in content_lower)
        if matched > 0:
            score += 0.3 * min(matched / len(query.keywords), 1.0)

    ctx = RetrievedContext(
        chunk_id=chunk.chunk_id,
        source_id=chunk.source_id,
        title=chunk.title,
        content=chunk.content,
        product=chunk.product,
        gap_types=list(chunk.gap_types),
        url=chunk.url,
        relevance_score=round(min(score, 1.0), 2),
    )
    return ctx, score


def build_default_index() -> ChunkIndex:
    """Build index from the default corpus directory."""
    chunks = load_and_chunk_corpus()
    return ChunkIndex(chunks)
