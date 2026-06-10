# Epic 18 — Automated Qdrant Corpus Ingestion

**Status:** Done

**Summary:** Created `scripts/ingest_nvidia_corpus.py` that reads `data/nvidia_corpus/` and `sources.yaml`, validates, chunks, generates embeddings, and upserts to Qdrant with full provenance. Backward-compatible schema extensions (version, document_type, content_hash, chunk_hash, ingestion_run_id). Payload indexes auto-created. 17 unit tests + 3 integration tests (skippable).

**Test count:** 375 total (358 pre-existing + 17 new)

**Key decisions:**
- Script is standalone — no changes to retrieval, scoring, diagnosis, or recommendation
- Payload indexes created in `_ensure_collection` → always present
- Idempotency via chunk_hash + --skip-existing
- No external calls, no scraping, no crawler

**See also:** `docs/42_automated_qdrant_corpus_ingestion.md`
