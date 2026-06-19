"""Product RAG module — NVIDIA playbook retrieval and context enrichment."""

from src.rag.context_packing import build_supporting_contexts, pack_contexts
from src.rag.embeddings import EmbeddingProvider, SentenceTransformerProvider
from src.rag.hybrid_retrieval import hybrid_retrieve
from src.rag.ingestion import load_and_chunk_corpus, load_sources
from src.rag.ingestion_pipeline import (
    CORPUS_VERSION,
    REQUIRED_PAYLOAD_FIELDS,
    CorpusReadinessResult,
    IngestionReport,
    check_corpus_readiness,
    run_ingestion_pipeline,
    validate_payload_schema,
)
from src.rag.playbook_retriever import PlaybookRetriever
from src.rag.qdrant_store import (
    QdrantConfig,
    QdrantConnectionError,
    QdrantStore,
    build_qdrant_store,
)
from src.rag.rag_pipeline import run_rag_pipeline
from src.rag.rag_service_factory import QdrantRagService, build_qdrant_rag_service
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
    "CORPUS_VERSION",
    "ChunkIndex",
    "CorpusReadinessResult",
    "DroppedContext",
    "EmbeddingProvider",
    "InMemoryVectorStore",
    "IngestionReport",
    "PackedContext",
    "PackingConfig",
    "PackingResult",
    "PlaybookRetriever",
    "PlaybookRetrievalResult",
    "QdrantConfig",
    "QdrantConnectionError",
    "QdrantRagService",
    "QdrantStore",
    "REQUIRED_PAYLOAD_FIELDS",
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
    "build_qdrant_rag_service",
    "build_qdrant_store",
    "build_supporting_contexts",
    "check_corpus_readiness",
    "hybrid_retrieve",
    "load_and_chunk_corpus",
    "load_sources",
    "pack_contexts",
    "rerank_contexts",
    "run_ingestion_pipeline",
    "run_rag_pipeline",
    "semantic_retrieve",
    "validate_payload_schema",
]
