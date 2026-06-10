"""Hybrid retrieval — fuse lexical (ChunkIndex) with semantic (vector store) via RRF."""

from __future__ import annotations

from src.rag.embeddings import EmbeddingProvider
from src.rag.retrieval import ChunkIndex
from src.rag.schemas import RetrievalQuery, RetrievedContext
from src.rag.semantic_retrieval import semantic_retrieve
from src.rag.vector_store import VectorStore

_RRF_K = 60


def hybrid_retrieve(
    query: RetrievalQuery,
    chunk_index: ChunkIndex,
    embedding_model: EmbeddingProvider,
    vector_store: VectorStore,
    top_k: int = 3,
    *,
    product: str | None = None,
    gap_type: str | None = None,
    source_id: str | None = None,
) -> list[RetrievedContext]:
    """Retrieve contexts using hybrid lexical + semantic fusion.

    Uses Reciprocal Rank Fusion (RRF) to combine results from
    the lexical ``ChunkIndex`` and the semantic vector store.

    If the vector store is empty, falls back to pure lexical retrieval.

    Parameters
    ----------
    query:
        The retrieval query.
    chunk_index:
        Lexical in-memory index (always available).
    embedding_model:
        Embedding provider for semantic search.
    vector_store:
        Vector store for semantic search.
    top_k:
        Maximum number of contexts to return.
    product, gap_type, source_id:
        Optional metadata filters.

    Returns
    -------
    list[RetrievedContext]
        Up to ``top_k`` fused and reranked contexts.
    """
    retrieve_top_k = max(top_k * 2, 5)

    lexical_results = chunk_index.retrieve(query, top_k=retrieve_top_k)

    semantic_results: list[RetrievedContext] = []
    if vector_store.size > 0:
        semantic_results = semantic_retrieve(
            query,
            embedding_model,
            vector_store,
            top_k=retrieve_top_k,
            product=product,
            gap_type=gap_type,
            source_id=source_id,
        )

    if not semantic_results:
        filtered = _apply_filters(lexical_results, product, gap_type, source_id)
        return filtered[:top_k]

    fused = _rrf_fuse(lexical_results, semantic_results, top_k)
    filtered = _apply_filters(fused, product, gap_type, source_id)
    return filtered[:top_k]


def _rrf_fuse(
    lexical: list[RetrievedContext],
    semantic: list[RetrievedContext],
    top_k: int,
) -> list[RetrievedContext]:
    """Fuse two ranked lists using Reciprocal Rank Fusion.

    Parameters
    ----------
    lexical:
        Ranked list from lexical retrieval.
    semantic:
        Ranked list from semantic retrieval.
    top_k:
        Maximum number of results in the fused list.

    Returns
    -------
    list[RetrievedContext]
        Fused list sorted by descending RRF score.
    """
    rrf_scores: dict[str, float] = {}
    contexts: dict[str, RetrievedContext] = {}

    for rank, ctx in enumerate(lexical):
        rrf_scores[ctx.chunk_id] = rrf_scores.get(ctx.chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
        if ctx.chunk_id not in contexts:
            contexts[ctx.chunk_id] = ctx

    for rank, ctx in enumerate(semantic):
        rrf_scores[ctx.chunk_id] = rrf_scores.get(ctx.chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
        if ctx.chunk_id not in contexts:
            contexts[ctx.chunk_id] = ctx

    sorted_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)
    fused = [contexts[cid] for cid in sorted_ids[:top_k]]

    for ctx in fused:
        ctx.relevance_score = round(
            min(max(rrf_scores.get(ctx.chunk_id, 0.0) / (_RRF_K + 1), 0.0), 1.0), 2
        )

    return fused


def _apply_filters(
    contexts: list[RetrievedContext],
    product: str | None = None,
    gap_type: str | None = None,
    source_id: str | None = None,
) -> list[RetrievedContext]:
    """Post-filter a list of contexts by metadata criteria."""
    result = contexts
    if product:
        p_lower = product.lower()
        result = [c for c in result if c.product.lower() == p_lower]
    if gap_type:
        result = [c for c in result if gap_type in c.gap_types]
    if source_id:
        result = [c for c in result if c.source_id == source_id]
    return result
