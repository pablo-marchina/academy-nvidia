# Epic 20 Corpus Freshness Versioning

**Date:** 2026-06-10
**Status:** Implemented

## Summary

Epic 20 adds lifecycle governance for the NVIDIA corpus. The corpus manifest now carries freshness/versioning metadata, audit tooling detects stale/expired/deprecated/superseded content, and default RAG retrieval excludes inactive, deprecated, superseded, and expired chunks.

## Implemented

- `docs/44_corpus_freshness_versioning_policy.md`
- `scripts/audit_nvidia_corpus_freshness.py`
- `tests/unit/test_corpus_freshness_audit.py`
- Freshness/versioning metadata in `data/nvidia_corpus/sources.yaml`
- Freshness policy metadata in `data/nvidia_corpus/source_allowlist.yaml`
- Metadata propagation through ingestion, `VectorEntry`, Qdrant payload, lexical retrieval, semantic retrieval, hybrid retrieval, and context packing

## Invariants

- `sources.yaml` is the authoritative lifecycle manifest.
- One active version per `source_id` by default.
- Default retrieval excludes inactive, deprecated, superseded, and expired chunks.
- Stale content is audit-visible but not yet surfaced in Action Brief warnings.

## Validation

- 11 unit tests cover stale, expired, deprecated, superseded, missing metadata, duplicate active versions, fail flags, version promotion, retrieval filtering, and vector-store filtering.
