"""Lexical retrieval over NVIDIA corpus chunks."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import UTC, datetime

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
        for chunk in self.chunks:
            for gap in chunk.gap_types:
                self.by_gap.setdefault(gap, []).append(chunk)
            tech_key = _normalize_technology(chunk.product)
            self.by_tech.setdefault(tech_key, []).append(chunk)

    def _candidates_from_query(self, query: RetrievalQuery) -> list[RagChunk]:
        """Return candidates using conjunctive structured filters.

        A query that specifies both a gap and a technology is an intersection,
        not a union. The previous union behavior introduced unrelated NIM,
        TensorRT-LLM, and Triton chunks into technology-specific results.
        """
        if not query.gap_type and not query.technology and not query.keywords:
            return []

        if query.gap_type:
            candidates = list(self.by_gap.get(query.gap_type, []))
        elif query.technology:
            candidates = list(self.by_tech.get(_normalize_technology(query.technology), []))
        else:
            candidates = list(self.chunks)

        if query.technology:
            candidates = [chunk for chunk in candidates if _technology_matches(chunk, query.technology)]

        if query.keywords:
            candidates = [chunk for chunk in candidates if _keywords_match(chunk, query.keywords)]

        seen: set[str] = set()
        return [
            chunk
            for chunk in candidates
            if chunk.chunk_id not in seen
            and not seen.add(chunk.chunk_id)
            and _is_retrievable(chunk, query)
        ]

    def retrieve(
        self,
        query: RetrievalQuery,
        top_k: int = _DEFAULT_TOP_K,
    ) -> list[RetrievedContext]:
        candidates = self._candidates_from_query(query)
        if not candidates or top_k <= 0:
            return []

        scored = [_score_chunk(chunk, query) for chunk in candidates]
        top = _source_diverse_top(scored, top_k)
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


def _normalize_technology(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _technology_matches(chunk: RagChunk, technology: str) -> bool:
    wanted = _normalize_technology(technology)
    if not wanted:
        return True
    product = _normalize_technology(chunk.product)
    nvidia_technology = _normalize_technology(chunk.nvidia_technology or "")
    return wanted in {product, nvidia_technology}


def _keywords_match(chunk: RagChunk, keywords: list[str]) -> bool:
    haystack = f"{chunk.product}\n{chunk.title}\n{chunk.content}".casefold()
    return any(keyword.casefold() in haystack for keyword in keywords if keyword.strip())


def _source_diverse_top(
    scored: list[tuple[RetrievedContext, float]],
    top_k: int,
) -> list[tuple[RetrievedContext, float]]:
    """Rank by relevance while guaranteeing source coverage before duplicates.

    Golden and production queries frequently request a gap addressed by several
    NVIDIA technologies. Taking the first ``k`` tied chunks allowed one verbose
    document to occupy every slot. We first select the best chunk per source,
    then fill remaining capacity with the next best chunks.
    """
    ranked = sorted(scored, key=lambda item: (-item[1], item[0].source_id, item[0].chunk_id))
    by_source: dict[str, list[tuple[RetrievedContext, float]]] = defaultdict(list)
    for item in ranked:
        by_source[item[0].source_id].append(item)

    source_heads = sorted(
        (items[0] for items in by_source.values()),
        key=lambda item: (-item[1], item[0].source_id, item[0].chunk_id),
    )
    selected = source_heads[:top_k]
    selected_ids = {item[0].chunk_id for item in selected}

    if len(selected) < top_k:
        for item in ranked:
            if item[0].chunk_id in selected_ids:
                continue
            selected.append(item)
            selected_ids.add(item[0].chunk_id)
            if len(selected) == top_k:
                break

    return selected


def _score_chunk(chunk: RagChunk, query: RetrievalQuery) -> tuple[RetrievedContext, float]:
    """Score a chunk's relevance to a query (0.0 to 1.0)."""
    score = 0.0
    content_lower = chunk.content.casefold()
    product_lower = chunk.product.casefold()

    if query.gap_type and query.gap_type in chunk.gap_types:
        score += 0.4

    if query.technology:
        q_tech = query.technology.casefold()
        if q_tech in product_lower or q_tech in content_lower:
            score += 0.3

    if query.keywords:
        haystack = f"{product_lower}\n{chunk.title.casefold()}\n{content_lower}"
        matched = sum(1 for keyword in query.keywords if keyword.casefold() in haystack)
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
        version=chunk.version,
        valid_from=chunk.valid_from,
        valid_until=chunk.valid_until,
        freshness_policy=chunk.freshness_policy,
        stale_after_days=chunk.stale_after_days,
        is_active=chunk.is_active,
        deprecated_at=chunk.deprecated_at,
        superseded_by=chunk.superseded_by,
    )
    return ctx, score


def _is_retrievable(chunk: RagChunk, query: RetrievalQuery) -> bool:
    if not query.include_deprecated:
        if chunk.is_active is not True:
            return False
        if chunk.deprecated_at or chunk.superseded_by:
            return False
    if not query.include_expired and _is_expired(chunk.valid_until):
        return False
    return True


def _is_expired(valid_until: str | None) -> bool:
    if not valid_until:
        return False
    try:
        parsed = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
    except ValueError:
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC) < datetime.now(UTC)


def build_default_index() -> ChunkIndex:
    """Build index from the default corpus directory."""
    from src.rag.ingestion import load_and_chunk_corpus

    chunks = load_and_chunk_corpus()
    return ChunkIndex(chunks)
