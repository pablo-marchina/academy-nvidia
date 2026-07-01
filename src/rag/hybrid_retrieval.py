"""Hybrid retrieval — BM25 + dense Qdrant + GraphRAG expansion via RRF."""

from __future__ import annotations

from typing import Any

from src.rag.embeddings import EmbeddingProvider
from src.rag.retrieval import ChunkIndex
from src.rag.schemas import RetrievalQuery, RetrievedContext
from src.rag.semantic_retrieval import semantic_retrieve
from src.rag.sparse_retrieval import SparseRetriever
from src.rag.graphrag_runtime import graphrag_expand
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
    include_deprecated: bool = False,
    include_expired: bool = False,
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

    bm25_retriever = SparseRetriever(chunk_index)
    lexical_results = bm25_retriever.retrieve(query, top_k=retrieve_top_k)

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
            include_deprecated=include_deprecated,
            include_expired=include_expired,
        )

    seed_results = semantic_results or lexical_results
    graph_results, _graph_metrics = graphrag_expand(
        seed_contexts=seed_results[:top_k],
        corpus_contexts=chunk_index.retrieve(query, top_k=max(retrieve_top_k * 3, 15)),
        query=query,
        top_k=retrieve_top_k,
    )

    fused = _rrf_fuse_many([lexical_results, semantic_results, graph_results], top_k)
    filtered = _apply_filters(fused, product, gap_type, source_id)
    return filtered[:top_k]


def _rrf_fuse(
    lexical: list[RetrievedContext],
    semantic: list[RetrievedContext],
    top_k: int,
) -> list[RetrievedContext]:
    """Backward-compatible two-list RRF fusion."""
    return _rrf_fuse_many([lexical, semantic], top_k)


def _rrf_fuse_many(
    ranked_lists: list[list[RetrievedContext]],
    top_k: int,
) -> list[RetrievedContext]:
    """Fuse BM25, dense Qdrant, and GraphRAG ranked lists using RRF."""
    rrf_scores: dict[str, float] = {}
    contexts: dict[str, RetrievedContext] = {}

    for ranked in ranked_lists:
        for rank, ctx in enumerate(ranked):
            rrf_scores[ctx.chunk_id] = rrf_scores.get(ctx.chunk_id, 0.0) + 1.0 / (_RRF_K + rank + 1)
            if ctx.chunk_id not in contexts:
                contexts[ctx.chunk_id] = ctx

    sorted_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)
    fused = [contexts[cid] for cid in sorted_ids[:top_k]]

    max_score = max(rrf_scores.values()) if rrf_scores else 1.0
    for ctx in fused:
        ctx.relevance_score = round(min(max(rrf_scores.get(ctx.chunk_id, 0.0) / max_score, 0.0), 1.0), 4)

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


class HybridRetrieval:
    def run(self, contexts: list[RetrievedContext], **kwargs: Any) -> list[RetrievedContext]:
        query = kwargs.get("query")
        chunk_index = kwargs.get("chunk_index")
        embedding_model = kwargs.get("embedding_model")
        vector_store = kwargs.get("vector_store")
        if (
            not isinstance(query, RetrievalQuery)
            or not isinstance(chunk_index, ChunkIndex)
            or not isinstance(embedding_model, EmbeddingProvider)
            or not isinstance(vector_store, VectorStore)
        ):
            return contexts
        return hybrid_retrieve(
            query=query,
            chunk_index=chunk_index,
            embedding_model=embedding_model,
            vector_store=vector_store,
            top_k=kwargs.get("top_k", 3),
            product=kwargs.get("product"),
            gap_type=kwargs.get("gap_type"),
            source_id=kwargs.get("source_id"),
            include_deprecated=kwargs.get("include_deprecated", False),
            include_expired=kwargs.get("include_expired", False),
        )
