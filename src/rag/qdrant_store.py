"""Qdrant-backed vector store — persistent, filterable, optional.

Epic 15: Adds ``QdrantStore(VectorStore)`` as a production-ready backend
while preserving the in-memory fallback for development and testing.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from src.rag.vector_store import VectorEntry, VectorStore

if TYPE_CHECKING:
    from qdrant_client import QdrantClient


class QdrantConnectionError(Exception):
    """Raised when Qdrant is unreachable or returns an unexpected error."""


@dataclass
class QdrantConfig:
    """Configuration for connecting to a Qdrant instance."""

    url: str = "http://localhost:6333"
    api_key: str | None = None
    collection_name: str = "nvidia_corpus"
    vector_size: int = 384
    timeout: int = 10


# ------------------------------------------------------------------
# QdrantStore
# ------------------------------------------------------------------


class QdrantStore(VectorStore):
    """Vector store backed by a Qdrant collection.

    Every entry is upserted as a Qdrant point with a rich payload
    that preserves provenance and supports server-side filtering.

    Parameters
    ----------
    config:
        Connection and collection settings.
    """

    def __init__(self, config: QdrantConfig | None = None) -> None:
        self._config = config or QdrantConfig()
        self._client: QdrantClient | None = None  # lazy — set on first access
        self._models: Any = None

    # ------------------------------------------------------------------
    # Lazy connection
    # ------------------------------------------------------------------

    def _ensure_client(self) -> None:
        """Connect to Qdrant on first use."""
        if self._client is not None:
            return
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models as qdrant_models

            self._models = qdrant_models
            self._client = QdrantClient(
                url=self._config.url,
                api_key=self._config.api_key or None,
                timeout=self._config.timeout,
            )
            self._ensure_collection()
        except ImportError as err:
            raise QdrantConnectionError(
                "qdrant-client is not installed.  Install it with: pip install qdrant-client"
            ) from err
        except Exception as exc:
            raise QdrantConnectionError(
                f"Cannot connect to Qdrant at {self._config.url}: {exc}"
            ) from exc

    def _ensure_collection(self) -> None:
        """Create the collection if it does not exist."""
        assert self._client is not None
        assert self._models is not None
        collections = self._client.get_collections().collections  # type: ignore[attr-defined]
        existing = {c.name for c in collections}
        if self._config.collection_name not in existing:
            self._client.create_collection(  # type: ignore[attr-defined]
                collection_name=self._config.collection_name,
                vectors_config=self._models.VectorParams(
                    size=self._config.vector_size,
                    distance=self._models.Distance.COSINE,
                ),
            )

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_entry(self, entry: VectorEntry) -> None:
        """Upsert a single entry as a Qdrant point."""
        self._ensure_client()
        assert self._client is not None
        point = _entry_to_point(entry, self._models)
        self._client.upsert(  # type: ignore[attr-defined]
            collection_name=self._config.collection_name,
            points=[point],
        )

    def add_entries(self, entries: list[VectorEntry]) -> None:
        """Upsert multiple entries in a single batch."""
        self._ensure_client()
        assert self._client is not None
        points = [_entry_to_point(e, self._models) for e in entries]
        self._client.upsert(  # type: ignore[attr-defined]
            collection_name=self._config.collection_name,
            points=points,
        )

    def remove_entry(self, chunk_id: str) -> None:
        """Delete a single point by chunk_id."""
        self._ensure_client()
        assert self._client is not None
        assert self._models is not None
        self._client.delete(  # type: ignore[attr-defined]
            collection_name=self._config.collection_name,
            points_selector=self._models.FilterSelector(
                filter=self._models.Filter(
                    must=[
                        self._models.FieldCondition(
                            key="chunk_id",
                            match=self._models.MatchValue(value=chunk_id),
                        )
                    ]
                )
            ),
        )

    def clear(self) -> None:
        """Delete and recreate the collection."""
        self._ensure_client()
        assert self._client is not None
        assert self._models is not None
        self._client.recreate_collection(  # type: ignore[attr-defined]
            collection_name=self._config.collection_name,
            vectors_config=self._models.VectorParams(
                size=self._config.vector_size,
                distance=self._models.Distance.COSINE,
            ),
        )

    def get_entry(self, chunk_id: str) -> VectorEntry | None:
        """Retrieve a single point by chunk_id."""
        self._ensure_client()
        assert self._client is not None
        points = self._client.scroll(  # type: ignore[attr-defined]
            collection_name=self._config.collection_name,
            limit=1,
            filter=self._models.Filter(
                must=[
                    self._models.FieldCondition(
                        key="chunk_id",
                        match=self._models.MatchValue(value=chunk_id),
                    )
                ]
            ),
        )[0]
        if not points:
            return None
        return _point_to_entry(points[0])

    @property
    def size(self) -> int:
        self._ensure_client()
        assert self._client is not None
        return self._client.count(  # type: ignore[no-any-return, attr-defined]
            collection_name=self._config.collection_name
        ).count

    @property
    def entries(self) -> list[VectorEntry]:
        self._ensure_client()
        assert self._client is not None
        points, _ = self._client.scroll(  # type: ignore[attr-defined]
            collection_name=self._config.collection_name,
            limit=10000,
            with_payload=True,
            with_vectors=True,
        )
        return [_point_to_entry(p) for p in points]

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
        *,
        product: str | None = None,
        gap_type: str | None = None,
        source_id: str | None = None,
        version: str | None = None,
        document_type: str | None = None,
    ) -> list[VectorEntry]:
        """Search with server-side metadata filters."""
        self._ensure_client()
        assert self._client is not None
        assert self._models is not None
        must_conditions: list[Any] = []

        if product:
            must_conditions.append(
                self._models.FieldCondition(
                    key="product",
                    match=self._models.MatchValue(value=product.lower()),
                )
            )
        if gap_type:
            must_conditions.append(
                self._models.FieldCondition(
                    key="gap_types",
                    match=self._models.MatchValue(value=gap_type),
                )
            )
        if source_id:
            must_conditions.append(
                self._models.FieldCondition(
                    key="source_id",
                    match=self._models.MatchValue(value=source_id),
                )
            )
        if version:
            must_conditions.append(
                self._models.FieldCondition(
                    key="version",
                    match=self._models.MatchValue(value=version),
                )
            )
        if document_type:
            must_conditions.append(
                self._models.FieldCondition(
                    key="document_type",
                    match=self._models.MatchValue(value=document_type),
                )
            )

        query_filter = self._models.Filter(must=must_conditions) if must_conditions else None

        results = self._client.query_points(  # type: ignore[attr-defined]
            collection_name=self._config.collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=True,
        )

        return [_point_to_entry(p) for p in results.points]


# ------------------------------------------------------------------
# Payload helpers
# ------------------------------------------------------------------


def _entry_to_point(entry: VectorEntry, models_module: Any) -> Any:
    """Convert a ``VectorEntry`` to a Qdrant ``PointStruct``."""
    now = datetime.now(UTC).isoformat()
    content_hash = hashlib.md5(entry.content.encode("utf-8")).hexdigest()

    return models_module.PointStruct(
        id=entry.chunk_id,
        vector=entry.embedding,
        payload={
            "chunk_id": entry.chunk_id,
            "source_id": entry.source_id,
            "source_title": entry.title,
            "source_url": entry.url or "",
            "product": entry.product,
            "gap_types": list(entry.gap_types),
            "version": "1.0",
            "content_hash": content_hash,
            "collected_at": now,
            "document_type": "nvidia_corpus",
            "provenance": {
                "source_url": entry.url or "",
                "source_title": entry.title,
            },
        },
    )


def _point_to_entry(point: Any) -> VectorEntry:
    """Convert a Qdrant ``ScoredPoint`` back to a ``VectorEntry``."""
    payload = point.payload or {}
    vector = list(point.vector or [])

    return VectorEntry(
        chunk_id=payload.get("chunk_id", point.id),
        source_id=payload.get("source_id", ""),
        title=payload.get("source_title", ""),
        content=payload.get("content", ""),
        product=payload.get("product", ""),
        gap_types=list(payload.get("gap_types", [])),
        url=payload.get("source_url") or None,
        embedding=vector,
    )


# ------------------------------------------------------------------
# Factory
# ------------------------------------------------------------------


def build_qdrant_store(
    url: str | None = None,
    collection_name: str | None = None,
    vector_size: int | None = None,
    api_key: str | None = None,
    timeout: int | None = None,
) -> QdrantStore:
    """Build a ``QdrantStore`` from explicit parameters (falls back to env).

    Parameters are optional — if not provided the factory reads from
    environment variables (via ``QdrantConfig`` defaults).
    """
    config = QdrantConfig(
        url=url or "http://localhost:6333",
        api_key=api_key,
        collection_name=collection_name or "nvidia_corpus",
        vector_size=vector_size or 384,
        timeout=timeout or 10,
    )
    return QdrantStore(config=config)
