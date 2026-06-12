# RAG Design

> **ARCHIVED:** Early RAG design document. Superseded by `docs/35_product_rag_design.md`, `docs/contracts/rag_contract.md`, and Epics 11-15. This document is preserved for historical reference only.

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
