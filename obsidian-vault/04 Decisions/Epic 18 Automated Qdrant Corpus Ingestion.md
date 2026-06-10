# Decision — Automated Qdrant Corpus Ingestion (Epic 18)

**Context:** Local corpus at `data/nvidia_corpus/` had no script to populate Qdrant. Ingestion was manual or non-existent.

**Decision:** Create `scripts/ingest_nvidia_corpus.py` with validation, hashing (MD5), embeddings (SentenceTransformerProvider or MockEmbeddingProvider), upsert to Qdrant, and ingestion report. Backward-compatible schema extensions on `RagSource`, `RagChunk`, `VectorEntry`.

**Key design choices:**
- No scraping, no crawler, no external calls — corpus is local and versioned
- Payload indexes created automatically on collection init
- Idempotency via deterministic chunk_id + chunk_hash + --skip-existing
- Dry-run mode validates without side effects
- Report saved as JSON via --report-path

**See also:** DECISIONS.md Decision (Epic 18), `docs/42_automated_qdrant_corpus_ingestion.md`
