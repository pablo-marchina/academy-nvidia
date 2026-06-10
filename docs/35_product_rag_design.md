# Product RAG / Playbook Retrieval — Design Doc

**Epic 11** | **Date**: 2026-06-09

## Objective

Build a minimal, testable RAG (Retrieval-Augmented Generation) layer that retrieves NVIDIA documentation snippets to enrich Startup Action Briefs and recommendations with grounded, provenance-tracked context.

RAG content is **non-authoritative context** — it enriches but never decides. The pipeline, scoring, diagnosis, recommendation, and briefing modules are unchanged.

## Architecture

```
data/nvidia_corpus/
├── sources.yaml          # Metadata per product (gap_types, urls)
├── nim.md                # NVIDIA NIM
├── tensorrt_llm.md       # TensorRT-LLM
├── triton.md             # Triton Inference Server
├── nemo_guardrails.md    # NeMo Guardrails
├── rapids.md             # RAPIDS
├── riva.md               # Riva
├── omniverse.md          # Omniverse
├── isaac.md              # Isaac
├── clara_monai.md        # Clara / MONAI
└── morpheus.md           # Morpheus

src/rag/
├── __init__.py           # Public API exports
├── schemas.py            # RagSource, RagDocument, RagChunk, RetrievalQuery, RetrievedContext, PlaybookRetrievalResult
├── ingestion.py          # load_sources(), load_markdown_document(), chunk_document(), load_and_chunk_corpus()
└── retrieval.py          # ChunkIndex (in-memory, lexical), retrieve(), retrieve_by_gap_type(), retrieve_by_technology(), build_default_index()
└── playbook_retriever.py # PlaybookRetriever: retrieve_for_gaps(), retrieve_for_brief()
```

## Chunking Strategy

- Deterministic: split by `##` headings
- Each section becomes one `RagChunk` preserving all source metadata
- No sliding windows, no overlap, no embeddings

## Retrieval Strategy

- **Lexical only**: no embeddings, no vector DB, no external calls
- **In-memory index**: indexed by `gap_type` and `product` (lowercased)
- **Scoring**: keyword match ratio + gap type match + product name match
- **Deduplication**: by `chunk_id`

## Key Design Decisions

| Decision | Rationale |
|---|---|
| No Qdrant/vector DB | MVP simplicity; embeddings add complexity without proven need |
| No LangGraph or new deps | Zero new dependencies; uses only json, pathlib, yaml (already present) |
| Deterministic chunking | Reproducible, testable, debuggable |
| Lexical retrieval | Sufficient for small corpus (10 docs); can be upgraded later |
| Provenance required | Every retrieved chunk carries source_id, url, product |
| RAG enriches, never decides | NVIDIA tech never recommended without explicit diagnosed gap |

## Corpus

10 manually curated Markdown files mapped to 15 `TechnicalGap` values from `_TECH_MATRIX` in `src/diagnosis/nvidia_mapping.py` and 14 experiment templates from `src/recommendation/recommendation_engine.py`.

## Integration

- `PlaybookRetriever.retrieve_for_gaps()`: called during Brief building to attach NVIDIA context per diagnosed gap
- `PlaybookRetriever.retrieve_for_brief()`: returns serializable dicts for template embedding
- Action Brief works normally without RAG context if corpus is unavailable

## Limitations

- No cross-chunk ranking or reranking
- No query expansion or synonyms
- Corpus is manually curated (no automated crawling/scraping)
- Relevance scoring is simple keyword-match-based
