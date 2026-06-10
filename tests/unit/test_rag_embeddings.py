"""Tests for src.rag.embeddings — EmbeddingProvider abstraction."""

import builtins
from typing import Any

import pytest

from src.rag.embeddings import (
    MockEmbeddingProvider,
    SentenceTransformerProvider,
    _pseudo_embedding,
    _text_to_seed,
)


def test_mock_provider_returns_expected_size() -> None:
    provider = MockEmbeddingProvider(vector_size=8)
    vec = provider.embed("hello")
    assert len(vec) == 8


def test_mock_provider_deterministic() -> None:
    provider = MockEmbeddingProvider()
    v1 = provider.embed("test text")
    v2 = provider.embed("test text")
    assert v1 == v2


def test_mock_provider_different_inputs_different_vectors() -> None:
    provider = MockEmbeddingProvider()
    v1 = provider.embed("NVIDIA NIM")
    v2 = provider.embed("TensorRT-LLM")
    assert v1 != v2


def test_mock_provider_embed_batch() -> None:
    provider = MockEmbeddingProvider()
    texts = ["a", "bb", "ccc"]
    results = provider.embed_batch(texts)
    assert len(results) == 3
    assert len(results[0]) == 4  # default size
    assert all(len(v) == 4 for v in results)


def test_mock_provider_batch_matches_single() -> None:
    provider = MockEmbeddingProvider()
    batch = provider.embed_batch(["hello"])
    single = provider.embed("hello")
    assert batch[0] == single


def test_mock_provider_vectors_normalized() -> None:
    provider = MockEmbeddingProvider()
    vec = provider.embed("some text")
    norm = sum(x * x for x in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-6


def test_text_to_seed_deterministic() -> None:
    assert _text_to_seed("hello") == _text_to_seed("hello")


def test_text_to_seed_different() -> None:
    assert _text_to_seed("hello") != _text_to_seed("world")


def test_pseudo_embedding_vector_size() -> None:
    vec = _pseudo_embedding(42, 10)
    assert len(vec) == 10


def test_pseudo_embedding_normalized() -> None:
    vec = _pseudo_embedding(42, 8)
    norm = sum(x * x for x in vec) ** 0.5
    assert abs(norm - 1.0) < 1e-6


def test_mock_provider_custom_size() -> None:
    provider = MockEmbeddingProvider(vector_size=16)
    vec = provider.embed("x")
    assert len(vec) == 16


def test_sentence_transformer_provider_missing_dependency_mentions_rag_extra(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "sentence_transformers":
            raise ImportError("missing sentence_transformers")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError, match=r'pip install -e "\.\[rag\]"'):
        SentenceTransformerProvider()


def test_sentence_transformer_provider_uses_new_dimension_method(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeModel:
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name

        def get_embedding_dimension(self) -> int:
            return 384

        def get_sentence_embedding_dimension(self) -> int:
            raise AssertionError("legacy dimension method should not be called")

    class FakeSentenceTransformers:
        SentenceTransformer = FakeModel

    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "sentence_transformers":
            return FakeSentenceTransformers
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    provider = SentenceTransformerProvider()

    assert provider.vector_size == 384


def test_sentence_transformer_provider_falls_back_to_legacy_dimension_method(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLegacyModel:
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name

        def get_sentence_embedding_dimension(self) -> int:
            return 384

    class FakeSentenceTransformers:
        SentenceTransformer = FakeLegacyModel

    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "sentence_transformers":
            return FakeSentenceTransformers
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    provider = SentenceTransformerProvider()

    assert provider.vector_size == 384


def test_sentence_transformer_provider_defaults_to_384_when_dimension_is_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeNoneDimensionModel:
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name

        def get_embedding_dimension(self) -> None:
            return None

        def get_sentence_embedding_dimension(self) -> None:
            return None

    class FakeSentenceTransformers:
        SentenceTransformer = FakeNoneDimensionModel

    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "sentence_transformers":
            return FakeSentenceTransformers
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    provider = SentenceTransformerProvider()

    assert provider.vector_size == 384
