# Plan: Epic 18 — Automated Qdrant Corpus Ingestion

**Data:** 2026-06-10
**Status:** Implementado e validado

## Escopo
1. `scripts/ingest_nvidia_corpus.py` — script de ingestão automatizada
2. `tests/unit/test_ingest_nvidia_corpus.py` — 17 testes
3. `tests/integration/test_qdrant_corpus_ingestion.py` — 3 testes skippable
4. `docs/42_automated_qdrant_corpus_ingestion.md`
5. Extensões de schema backward-compatible em `src/rag/schemas.py`, `vector_store.py`, `qdrant_store.py`
6. `data/nvidia_corpus/sources.yaml` — +version, document_type
7. Atualizar README, EVALS, ROADMAP, Makefile, rag_contract.md, Obsidian

## Fora de escopo
- Nenhum scraping, crawler, download externo
- Nenhuma alteração em retrieval, scoring, diagnosis, recommendation, Action Brief
- Nenhuma dependência nova

## Validação
- 375 testes passam (17 novos + 358 pre-existentes)
- 12 testes skippable (9 Qdrant + 3 ingest)
- ruff, black, mypy passam (pre-existing only)
