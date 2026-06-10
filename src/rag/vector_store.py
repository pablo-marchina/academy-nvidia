"""Local in-memory vector store with cosine similarity search.

No external dependencies. Supports filters by product, gap_type, and source_id.
Designed for development and testing — swap for Qdrant in production.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class VectorEntry:
    """A chunk stored in the vector store with its embedding."""

    chunk_id: str
    source_id: str
    title: str
    content: str
    product: str
    gap_types: list[str] = field(default_factory=list)
    url: str | None = None
    embedding: list[float] = field(default_factory=list)


class InMemoryVectorStore:
    """Dict-backed vector store with cosine similarity search."""

    def __init__(self) -> None:
        self._entries: dict[str, VectorEntry] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_entry(self, entry: VectorEntry) -> None:
        """Add or replace a single entry by chunk_id."""
        self._entries[entry.chunk_id] = entry

    def add_entries(self, entries: list[VectorEntry]) -> None:
        """Add multiple entries in one call."""
        for e in entries:
            self.add_entry(e)

    def remove_entry(self, chunk_id: str) -> None:
        """Remove a single entry by chunk_id."""
        self._entries.pop(chunk_id, None)

    def clear(self) -> None:
        """Remove all entries."""
        self._entries.clear()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_entry(self, chunk_id: str) -> VectorEntry | None:
        """Look up a single entry by chunk_id."""
        return self._entries.get(chunk_id)

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> list[VectorEntry]:
        return list(self._entries.values())

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        product: str | None = None,
        gap_type: str | None = None,
        source_id: str | None = None,
    ) -> list[VectorEntry]:
        """Cosine-similarity search with optional metadata filters.

        Parameters
        ----------
        query_embedding:
            The embedding vector to search for.
        top_k:
            Maximum number of results to return.
        product:
            If set, only return entries whose ``product`` matches (case-insensitive).
        gap_type:
            If set, only return entries whose ``gap_types`` contains this value.
        source_id:
            If set, only return entries whose ``source_id`` matches.

        Returns
        -------
        list[VectorEntry]
            Up to ``top_k`` entries sorted by descending similarity.
        """
        candidates = self._filter(product=product, gap_type=gap_type, source_id=source_id)
        if not candidates:
            return []

        scored: list[tuple[VectorEntry, float]] = []
        for entry in candidates:
            sim = _cosine_similarity(query_embedding, entry.embedding)
            scored.append((entry, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in scored[:top_k]]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _filter(
        self,
        product: str | None = None,
        gap_type: str | None = None,
        source_id: str | None = None,
    ) -> list[VectorEntry]:
        """Return all entries matching the given filters."""
        result = self.entries
        if product:
            p_lower = product.lower()
            result = [e for e in result if e.product.lower() == p_lower]
        if gap_type:
            result = [e for e in result if gap_type in e.gap_types]
        if source_id:
            result = [e for e in result if e.source_id == source_id]
        return result


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Returns a value in [-1, 1]. Returns 0.0 for zero vectors.
    """
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
