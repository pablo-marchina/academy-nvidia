"""Integration tests for the QdrantStore adapter with a real Qdrant server.

All tests are skippable — they only run when ``QDRANT_TEST_URL`` is set.
"""

from __future__ import annotations

import os

import pytest

from src.rag.qdrant_store import QdrantConfig, QdrantConnectionError, QdrantStore
from src.rag.vector_store import VectorEntry

_QDRANT_TEST_URL = os.environ.get("QDRANT_TEST_URL")
_REQUIRE_QDRANT = pytest.mark.skipif(
    not _QDRANT_TEST_URL,
    reason="set QDRANT_TEST_URL to run Qdrant integration tests",
)


@pytest.fixture
def store() -> QdrantStore:
    assert _QDRANT_TEST_URL is not None, "QDRANT_TEST_URL not set"
    cfg = QdrantConfig(
        url=_QDRANT_TEST_URL,
        collection_name="test_epic15_integration",
        vector_size=4,
        timeout=5,
    )
    s = QdrantStore(config=cfg)
    s.clear()  # start clean
    return s


@pytest.fixture
def sample_entries() -> list[VectorEntry]:
    return [
        VectorEntry(
            chunk_id="nim_000",
            source_id="nim",
            title="NIM",
            content="NVIDIA NIM optimizes inference cost.",
            product="nim",
            gap_types=["high_inference_cost"],
            url="https://docs.nvidia.com/nim",
            embedding=[0.1, 0.2, 0.3, 0.4],
        ),
        VectorEntry(
            chunk_id="triton_000",
            source_id="triton",
            title="Triton",
            content="Triton Inference Server reduces latency.",
            product="triton",
            gap_types=["high_latency"],
            url="https://docs.nvidia.com/triton",
            embedding=[0.5, 0.6, 0.7, 0.8],
        ),
    ]


@_REQUIRE_QDRANT
def test_upsert_and_search(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """Basic upsert + search round-trip."""
    store.add_entries(sample_entries)
    assert store.size == 2

    results = store.search([0.1, 0.2, 0.3, 0.4], top_k=3)
    assert len(results) >= 1
    assert results[0].chunk_id == "nim_000"


@_REQUIRE_QDRANT
def test_search_filter_product(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """Filter by product returns only matching entries."""
    store.add_entries(sample_entries)
    results = store.search([0.1, 0.2, 0.3, 0.4], product="triton")
    assert all(r.product == "triton" for r in results)


@_REQUIRE_QDRANT
def test_search_filter_gap_type(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """Filter by gap_type returns only matching entries."""
    store.add_entries(sample_entries)
    results = store.search([0.1, 0.2, 0.3, 0.4], gap_type="high_latency")
    assert all("high_latency" in r.gap_types for r in results)


@_REQUIRE_QDRANT
def test_search_filter_source_id(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """Filter by source_id returns only matching entries."""
    store.add_entries(sample_entries)
    results = store.search([0.1, 0.2, 0.3, 0.4], source_id="nim")
    assert all(r.source_id == "nim" for r in results)


@_REQUIRE_QDRANT
def test_remove_entry(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """Removing an entry decreases size."""
    store.add_entries(sample_entries)
    assert store.size == 2
    store.remove_entry("nim_000")
    assert store.size == 1
    assert store.get_entry("nim_000") is None


@_REQUIRE_QDRANT
def test_clear(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """Clear removes all entries."""
    store.add_entries(sample_entries)
    assert store.size == 2
    store.clear()
    assert store.size == 0


@_REQUIRE_QDRANT
def test_get_entry(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """get_entry retrieves a single entry by chunk_id."""
    store.add_entries(sample_entries)
    entry = store.get_entry("nim_000")
    assert entry is not None
    assert entry.chunk_id == "nim_000"
    assert entry.source_id == "nim"
    assert entry.url == "https://docs.nvidia.com/nim"


@_REQUIRE_QDRANT
def test_provenance_preserved(store: QdrantStore, sample_entries: list[VectorEntry]) -> None:
    """Provenance (url, source_id) is preserved after round-trip."""
    store.add_entries(sample_entries)
    entry = store.get_entry("nim_000")
    assert entry is not None
    assert entry.url == "https://docs.nvidia.com/nim"
    assert entry.source_id == "nim"
    assert entry.product == "nim"


@_REQUIRE_QDRANT
def test_connection_error_when_unavailable() -> None:
    """QdrantConnectionError is raised when server is unreachable."""
    cfg = QdrantConfig(url="http://localhost:19999", timeout=1)
    s = QdrantStore(config=cfg)
    with pytest.raises(QdrantConnectionError):
        _ = s.size
