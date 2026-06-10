"""Embedding provider abstraction for Product RAG.

Supports local (sentence-transformers) and mock/deterministic providers.
No API keys required for default usage.
"""

from __future__ import annotations

import hashlib
import math
from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):
    """Abstract embedding provider.

    Implementations must be deterministic for the same input text
    when running in the same mode.
    """

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a vector."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in a single batch call."""


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic pseudo-embedding provider for tests.

    Generates reproducible embeddings using MD5 hash as seed.
    Similar texts (by hash prefix) get related but non-identical vectors.
    No external dependencies, no model downloads.
    """

    def __init__(self, vector_size: int = 4) -> None:
        self.vector_size = vector_size

    def embed(self, text: str) -> list[float]:
        seed = _text_to_seed(text)
        return _pseudo_embedding(seed, self.vector_size)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class SentenceTransformerProvider(EmbeddingProvider):
    """Local embedding provider using sentence-transformers.

    Requires the ``sentence-transformers`` package.
    Default model is ``all-MiniLM-L6-v2`` (384 dimensions, ~80 MB).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            import sentence_transformers as st
        except ImportError as err:
            raise ImportError(
                "sentence-transformers is required for real RAG embeddings. "
                'Install the optional RAG dependencies with: pip install -e ".[rag]"'
            ) from err

        self.model = st.SentenceTransformer(model_name)
        self._dim = _embedding_dimension(self.model)

    @property
    def vector_size(self) -> int:
        return self._dim

    def embed(self, text: str) -> list[float]:
        result = self.model.encode(text)
        return result.tolist()  # type: ignore[no-any-return]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        result = self.model.encode(texts)
        return result.tolist()  # type: ignore[no-any-return]


def _text_to_seed(text: str) -> int:
    """Convert arbitrary text to a deterministic integer seed."""
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _embedding_dimension(model: Any) -> int:
    """Return embedding dimension across sentence-transformers versions."""
    get_dimension = getattr(model, "get_embedding_dimension", None)
    if callable(get_dimension):
        dimension = get_dimension()
        if dimension is not None:
            return int(dimension)

    get_legacy_dimension = getattr(model, "get_sentence_embedding_dimension", None)
    if callable(get_legacy_dimension):
        dimension = get_legacy_dimension()
        if dimension is not None:
            return int(dimension)

    return 384


def _pseudo_embedding(seed: int, size: int) -> list[float]:
    """Generate a deterministic pseudo-embedding from a seed.

    Uses sin/cos of the seed at different frequencies to produce
    a vector that preserves some notion of similarity: texts with
    close seeds (similar content) get closer vectors.
    """
    result: list[float] = []
    for i in range(size):
        val = math.sin(seed + i * 0.1) * math.cos(seed * 0.01 + i)
        result.append(round(val, 6))
    norm = math.sqrt(sum(x * x for x in result)) or 1.0
    return [round(x / norm, 6) for x in result]
