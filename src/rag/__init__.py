"""Product RAG module — NVIDIA playbook retrieval and context enrichment."""

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

__all__ = [
    "ChunkIndex",
    "PlaybookRetriever",
    "PlaybookRetrievalResult",
    "RagChunk",
    "RagDocument",
    "RagSource",
    "RetrievedContext",
    "RetrievalQuery",
    "build_default_index",
    "load_and_chunk_corpus",
    "load_sources",
]
