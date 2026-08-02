"""Lexical retrieval over NVIDIA corpus chunks.

The lexical path is intentionally deterministic, but it still needs to model
query intent correctly. In particular:

* a gap + technology query is an intersection, not a union;
* an exact product match outranks a product merely mentioned in another page;
* broad gap/keyword queries should expose source diversity instead of allowing
  one long document to consume the whole top-k budget;
* source taxonomy is searchable, so terms such as ``inference`` and ``latency``
  still retrieve products whose clean page text uses a narrower vocabulary.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from src.rag.schemas import RagChunk, RetrievalQuery, RetrievedContext

_DEFAULT_TOP_K = 3
_TOKEN_RE = re.compile(r"[a-z0-9]+")


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
            tech_key = _normalize_text(chunk.product)
            if tech_key:
                self.by_tech.setdefault(tech_key, []).append(chunk)

    def _eligible(self, chunks: list[RagChunk], query: RetrievalQuery) -> list[RagChunk]:
        return [chunk for chunk in chunks if _is_retrievable(chunk, query)]

    def _technology_candidates(self, query: RetrievalQuery) -> list[RagChunk]:
        if not query.technology:
            return []

        tech_key = _normalize_text(query.technology)
        exact = self._eligible(self.by_tech.get(tech_key, []), query)
        if exact:
            return exact

        strong = [
            chunk
            for chunk in self.chunks
            if _is_retrievable(chunk, query)
            and _technology_match_strength(chunk, query.technology) >= 0.7
        ]
        if strong:
            return strong

        # Content-only mentions are a last-resort fallback for aliases or an
        # incomplete product registry. They must not compete with exact product
        # matches when those exist.
        return [
            chunk
            for chunk in self.chunks
            if _is_retrievable(chunk, query)
            and _technology_match_strength(chunk, query.technology) > 0.0
        ]

    def _candidates_from_query(self, query: RetrievalQuery) -> list[RagChunk]:
        gap_candidates = (
            self._eligible(self.by_gap.get(query.gap_type, []), query)
            if query.gap_type
            else []
        )
        technology_candidates = self._technology_candidates(query)

        if query.gap_type and query.technology:
            # The user requested a specific technology for a specific gap.
            # Prefer product/title-level matches within the gap and never let a
            # mention in another product page outrank the requested product.
            intersected = [
                chunk
                for chunk in gap_candidates
                if _technology_match_strength(chunk, query.technology) >= 0.7
            ]
            if intersected:
                return _deduplicate(intersected)

            technology_ids = {chunk.chunk_id for chunk in technology_candidates}
            fallback_intersection = [
                chunk for chunk in gap_candidates if chunk.chunk_id in technology_ids
            ]
            return _deduplicate(fallback_intersection)

        if query.gap_type:
            return _deduplicate(gap_candidates)

        if query.technology:
            return _deduplicate(technology_candidates)

        if query.keywords:
            return _deduplicate([
                chunk
                for chunk in self.chunks
                if _is_retrievable(chunk, query)
                and _keyword_match_strength(chunk, query.keywords) > 0.0
            ])

        return []

    def retrieve(
        self,
        query: RetrievalQuery,
        top_k: int = _DEFAULT_TOP_K,
    ) -> list[RetrievedContext]:
        if top_k <= 0:
            return []

        candidates = self._candidates_from_query(query)
        if not candidates:
            return []

        scored = [_score_chunk(chunk, query) for chunk in candidates]
        scored.sort(key=lambda item: (-item[1], item[0].source_id, item[0].chunk_id))
        selected = _select_source_diverse(scored, query, top_k)
        return [context for context, _ in selected]

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


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(_TOKEN_RE.findall(value.casefold()))


def _technology_match_strength(chunk: RagChunk, technology: str | None) -> float:
    query = _normalize_text(technology)
    if not query:
        return 0.0

    product = _normalize_text(chunk.product)
    registered_technology = _normalize_text(chunk.nvidia_technology)
    title = _normalize_text(chunk.title)
    content = _normalize_text(chunk.content)
    query_tokens = set(query.split())

    if query in {product, registered_technology}:
        return 1.0
    if product and (query in product or product in query):
        return 0.92
    if registered_technology and (
        query in registered_technology or registered_technology in query
    ):
        return 0.9
    if query_tokens and query_tokens.issubset(set(product.split())):
        return 0.86
    if title and (query == title or query in title):
        return 0.78
    if query in content:
        return 0.35
    if query_tokens and query_tokens.issubset(set(content.split())):
        return 0.25
    return 0.0


def _keyword_match_strength(chunk: RagChunk, keywords: list[str]) -> float:
    normalized_keywords = [_normalize_text(keyword) for keyword in keywords]
    normalized_keywords = [keyword for keyword in normalized_keywords if keyword]
    if not normalized_keywords:
        return 0.0

    product = _normalize_text(chunk.product)
    title = _normalize_text(chunk.title)
    content = _normalize_text(chunk.content)
    taxonomy = _normalize_text(" ".join(chunk.gap_types))
    taxonomy_tokens = set(taxonomy.split())
    strengths: list[float] = []

    for keyword in normalized_keywords:
        keyword_tokens = set(keyword.split())
        if keyword in product or keyword in title:
            strengths.append(1.0)
            continue
        if keyword in taxonomy or (
            keyword_tokens and keyword_tokens.issubset(taxonomy_tokens)
        ):
            strengths.append(0.95)
            continue
        occurrences = content.count(keyword)
        if occurrences:
            # Repeated terms are useful, but capped so boilerplate cannot win
            # purely by page length.
            strengths.append(min(0.55 + (0.08 * occurrences), 0.87))
        else:
            strengths.append(0.0)

    return sum(strengths) / len(strengths)


def _score_chunk(chunk: RagChunk, query: RetrievalQuery) -> tuple[RetrievedContext, float]:
    """Score a chunk's relevance to a query (0.0 to 1.0)."""
    score = 0.0

    if query.gap_type and query.gap_type in chunk.gap_types:
        score += 0.45

    if query.technology:
        score += 0.45 * _technology_match_strength(chunk, query.technology)

    if query.keywords:
        score += 0.45 * _keyword_match_strength(chunk, query.keywords)

    score = min(score, 1.0)
    context = RetrievedContext(
        chunk_id=chunk.chunk_id,
        source_id=chunk.source_id,
        title=chunk.title,
        content=chunk.content,
        product=chunk.product,
        gap_types=list(chunk.gap_types),
        url=chunk.url,
        relevance_score=round(score, 4),
        version=chunk.version,
        collected_at=chunk.collected_at,
        last_checked_at=chunk.last_checked_at,
        valid_from=chunk.valid_from,
        valid_until=chunk.valid_until,
        freshness_policy=chunk.freshness_policy,
        stale_after_days=chunk.stale_after_days,
        is_active=chunk.is_active,
        deprecated_at=chunk.deprecated_at,
        superseded_by=chunk.superseded_by,
    )
    return context, score


def _select_source_diverse(
    scored: list[tuple[RetrievedContext, float]],
    query: RetrievalQuery,
    top_k: int,
) -> list[tuple[RetrievedContext, float]]:
    """Round-robin high-quality results across sources for broad queries.

    Specific technology queries intentionally stay concentrated on the selected
    product. Gap-only and keyword-only queries benefit from source diversity,
    because a long document can otherwise consume every result slot.
    """
    if query.technology or len(scored) <= 1:
        return scored[:top_k]

    buckets: dict[str, list[tuple[RetrievedContext, float]]] = {}
    source_order: list[str] = []
    for item in scored:
        source_id = item[0].source_id
        if source_id not in buckets:
            buckets[source_id] = []
            source_order.append(source_id)
        buckets[source_id].append(item)

    selected: list[tuple[RetrievedContext, float]] = []
    cursor = 0
    while len(selected) < top_k:
        added = False
        for source_id in source_order:
            bucket = buckets[source_id]
            if cursor < len(bucket):
                selected.append(bucket[cursor])
                added = True
                if len(selected) == top_k:
                    break
        if not added:
            break
        cursor += 1
    return selected


def _deduplicate(chunks: list[RagChunk]) -> list[RagChunk]:
    seen: set[str] = set()
    result: list[RagChunk] = []
    for chunk in chunks:
        if chunk.chunk_id in seen:
            continue
        seen.add(chunk.chunk_id)
        result.append(chunk)
    return result


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
