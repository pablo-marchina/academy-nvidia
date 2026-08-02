from __future__ import annotations

from src.rag.hybrid_retrieval import _apply_filters, _gap_type_aliases
from src.rag.schemas import RetrievedContext


def _context(chunk_id: str, product: str, gap_types: list[str]) -> RetrievedContext:
    return RetrievedContext(
        chunk_id=chunk_id,
        source_id=f"source-{chunk_id}",
        title=product,
        content=f"Official NVIDIA context for {product}.",
        product=product,
        gap_types=gap_types,
        url=f"https://docs.nvidia.com/{chunk_id}",
        relevance_score=0.9,
    )


def test_diagnosis_gap_expands_to_technical_corpus_alias() -> None:
    aliases = _gap_type_aliases("computer_vision_gap")
    assert "computer_vision_gap" in aliases
    assert "computer_vision_need" in aliases


def test_alias_aware_filter_keeps_tensor_rt_context_and_rejects_voice() -> None:
    contexts = [
        _context("tensorrt", "TensorRT", ["computer_vision_need", "high_latency"]),
        _context("riva", "NVIDIA Riva", ["voice_need"]),
    ]

    filtered = _apply_filters(contexts, gap_type="computer_vision_gap")

    assert [context.product for context in filtered] == ["TensorRT"]
