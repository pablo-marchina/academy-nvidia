"""Product RAG module — NVIDIA playbook retrieval and context enrichment."""

from src.rag.context_packing import build_supporting_contexts, pack_contexts
from src.rag.embeddings import EmbeddingProvider, MockEmbeddingProvider, SentenceTransformerProvider
from src.rag.hybrid_retrieval import hybrid_retrieve
from src.rag.ingestion import load_and_chunk_corpus, load_sources
from src.rag.playbook_retriever import PlaybookRetriever
from src.rag.qdrant_store import (
    QdrantConfig,
    QdrantConnectionError,
    QdrantStore,
    build_qdrant_store,
)
from src.rag.rag_pipeline import run_rag_pipeline
from src.rag.reranking import rerank_contexts
from src.rag.retrieval import ChunkIndex, build_default_index
from src.rag.schemas import (
    DroppedContext,
    PackedContext,
    PackingConfig,
    PackingResult,
    PlaybookRetrievalResult,
    RagChunk,
    RagDocument,
    RagPipelineOutput,
    RagSource,
    RerankingConfig,
    RetrievalQuery,
    RetrievedContext,
    SupportingNvidiaContext,
)
from src.rag.semantic_retrieval import semantic_retrieve
from src.rag.vector_store import InMemoryVectorStore, VectorEntry, VectorStore

__all__ = [
    "ChunkIndex",
    "DroppedContext",
    "EmbeddingProvider",
    "InMemoryVectorStore",
    "MockEmbeddingProvider",
    "PackedContext",
    "PackingConfig",
    "PackingResult",
    "PlaybookRetriever",
    "PlaybookRetrievalResult",
    "QdrantConfig",
    "QdrantConnectionError",
    "QdrantStore",
    "RagChunk",
    "RagDocument",
    "RagPipelineOutput",
    "RagSource",
    "RerankingConfig",
    "RetrievedContext",
    "RetrievalQuery",
    "SentenceTransformerProvider",
    "SupportingNvidiaContext",
    "VectorEntry",
    "VectorStore",
    "build_default_index",
    "build_qdrant_store",
    "build_supporting_contexts",
    "hybrid_retrieve",
    "load_and_chunk_corpus",
    "load_sources",
    "pack_contexts",
    "rerank_contexts",
    "run_rag_pipeline",
    "semantic_retrieve",
]
