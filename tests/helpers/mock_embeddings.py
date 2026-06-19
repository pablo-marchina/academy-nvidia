"""Mock embedding provider for tests.

Re-exports from src.rag.embeddings for backward compatibility.
"""

from src.rag.embeddings import MockEmbeddingProvider

__all__ = ["MockEmbeddingProvider"]
