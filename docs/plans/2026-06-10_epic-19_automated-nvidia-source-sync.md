# Plan: Epic 19 — Automated NVIDIA Corpus Source Sync

## Objective

Create a controlled source sync script that downloads allowed NVIDIA documentation
URLs to a staging area, validates metadata/provenance/hash, generates a sync report,
and promotes to the local corpus only with --promote. Does NOT ingest into Qdrant.

## Context Read

AGENTS.md, README.md, ROADMAP.md, DECISIONS.md, EVALS.md, Makefile, .env.example,
docs/contracts/rag_contract.md, docs/35_product_rag_design.md, docs/39_qdrant_persistent_vector_store.md,
docs/42_automated_qdrant_corpus_ingestion.md, src/rag/ingestion.py, scripts/ingest_nvidia_corpus.py,
data/nvidia_corpus/sources.yaml, data/nvidia_corpus/ (directory listing)

## Relevant Files

### Created
- scripts/sync_nvidia_sources.py
- data/nvidia_corpus/source_allowlist.yaml
- data/nvidia_corpus/staging/.gitkeep
- data/nvidia_corpus/archive/.gitkeep
- data/nvidia_corpus/sync_reports/.gitkeep
- tests/unit/test_sync_nvidia_sources.py
- docs/43_automated_nvidia_source_sync.md

### Updated
- README.md (Current Capabilities + Known Limitations)
- EVALS.md (test table + ingestion section)
- ROADMAP.md (Epic 19 as completed)
- docs/contracts/rag_contract.md (Source Sync section)
- Makefile (sync-corpus-dry-run, sync-corpus targets)
- docs/plans/2026-06-10_epic-19_automated-nvidia-source-sync.md
- obsidian-vault/ (decision + research + Known Limitations)

## Implementation Plan

1. Create source_allowlist.yaml with schema for all 10 NVIDIA sources + 1 blocked test source
2. Create staging/, archive/, sync_reports/ directories with .gitkeep
3. Create scripts/sync_nvidia_sources.py with full CLI and safety controls
4. Create 49 unit tests with mocked fetcher
5. Create design doc
6. Update README, EVALS, ROADMAP, Makefile, rag_contract.md
7. Backfill Obsidian vault
8. Run validation (pytest, ruff, black, mypy)

## Out of Scope

- Ingestao direta no Qdrant
- Crawler amplo
- Alteracao de src/rag/, src/pipeline/, src/scoring/, src/diagnosis/, src/recommendation/, src/briefing/
- Chamadas externas nos testes
- Novas dependencias
