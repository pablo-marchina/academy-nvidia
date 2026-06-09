# RAG Design

## Goal

Provide grounded NVIDIA recommendations by retrieving official product and program context before generation.

## Initial design choices

- Use a curated NVIDIA source manifest.
- Keep ingestion, chunking, retrieval, and reranking separated.
- Prefer official NVIDIA documentation.
- Preserve chunk-level citations for every recommendation path.

## Deferred decisions

- Embedding model selection
- Hybrid retrieval details
- Metadata schema for chunks
- Citation rendering format
