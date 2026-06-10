"""Product RAG module — NVIDIA playbook retrieval and context enrichment."""

from src.rag.embeddings import EmbeddingProvider, MockEmbeddingProvider, SentenceTransformerProvider
from src.rag.hybrid_retrieval import hybrid_retrieve
from src.rag.ingestion import load_and_chunk_corpus, load_sources
from src.rag.playbook_retriever import PlaybookRetriever
from src.rag.retrieval import ChunkIndex, build_default_index
from src.rag.schemas import (
    PlaybookRetrievalResult,
    RagChunk,
    RagDocument,
    RagSource,
    RetrievalQuery,
    RetrievedContext,
)
from src.rag.semantic_retrieval import semantic_retrieve
from src.rag.vector_store import InMemoryVectorStore, VectorEntry

__all__ = [
    "ChunkIndex",
    "EmbeddingProvider",
    "InMemoryVectorStore",
    "MockEmbeddingProvider",
    "PlaybookRetriever",
    "PlaybookRetrievalResult",
    "RagChunk",
    "RagDocument",
    "RagSource",
    "RetrievedContext",
    "RetrievalQuery",
    "SentenceTransformerProvider",
    "VectorEntry",
    "build_default_index",
    "hybrid_retrieve",
    "load_and_chunk_corpus",
    "load_sources",
    "semantic_retrieve",
]
