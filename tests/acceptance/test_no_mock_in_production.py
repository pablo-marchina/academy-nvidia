"""Guard: Production API code must not depend on MockEmbeddingProvider.

This test verifies that the API service module does not import mock providers
and only uses real implementations (SentenceTransformerProvider) for embeddings.
"""

from src.api.service import build_rag_dependencies


def test_build_rag_dependencies_uses_real_provider() -> None:
    """Verify production path uses SentenceTransformerProvider, not MockEmbeddingProvider."""
    import inspect

    source = inspect.getsource(build_rag_dependencies)
    assert "SentenceTransformerProvider" in source
    assert "MockEmbeddingProvider" not in source


def test_build_rag_dependencies_local_raises_without_sentence_transformers() -> None:
    """When sentence-transformers is not installed, local backend raises ImportError."""
    import sys

    orig = sys.modules.get("sentence_transformers")
    sys.modules["sentence_transformers"] = None  # type: ignore[assignment]
    try:
        from src.rag.embeddings import SentenceTransformerProvider as STP

        try:
            STP()
            raise AssertionError("Expected ImportError")
        except ImportError:
            pass
    finally:
        if orig is not None:
            sys.modules["sentence_transformers"] = orig
        else:
            sys.modules.pop("sentence_transformers", None)


def test_build_rag_dependencies_raises_on_unknown_backend() -> None:
    """build_rag_dependencies raises ValueError for unknown backends."""
    try:
        build_rag_dependencies("nonexistent_backend")
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass
