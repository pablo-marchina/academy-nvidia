# Plan: Epic 11 — Product RAG / Playbook Retrieval

## Objective

Criar camada RAG minima e testavel para recuperar trechos de documentacao/playbooks NVIDIA locais, enriquecendo diagnosticos e recomendacoes sem substituir logica deterministica.

## Context Read

- AGENTS.md, README.md, ROADMAP.md, DECISIONS.md, EVALS.md
- docs/contracts/ (all 7)
- docs/13_nvidia_mapping_matrix.md
- docs/27_developer_rag_design.md
- src/rag/ (existing stubs)
- src/diagnosis/nvidia_mapping.py (_TECH_MATRIX)
- src/recommendation/recommendation_engine.py (_EXPERIMENT_TEMPLATES)
- src/briefing/ (schemas, action_brief)
- tests/

## Files to Create/Change

### Create
- `src/rag/schemas.py` — RagDocument, RagChunk, RetrievalQuery, RetrievedContext, PlaybookRetrievalResult
- `src/rag/ingestion.py` — load_markdown_corpus(), chunk_document()
- `src/rag/retrieval.py` — retrieve_by_gap_type(), retrieve_by_technology(), lexical_search()
- `src/rag/playbook_retriever.py` — PlaybookRetriever class
- `tests/unit/test_rag_ingestion.py` — 3 tests
- `tests/unit/test_rag_retrieval.py` — 3 tests
- `tests/unit/test_playbook_retriever.py` — 3 tests
- `data/nvidia_corpus/README.md`
- `data/nvidia_corpus/sources.yaml`
- `data/nvidia_corpus/nim.md` through `morpheus.md` (10 files)
- `docs/35_product_rag_design.md`
- `docs/contracts/rag_contract.md`
- Obsidian notes

### Change
- `src/rag/__init__.py` — export public API
- `EVALS.md`, `README.md`, `ROADMAP.md`, `DECISIONS.md`

## Implementation Steps

1. Save plan artifact
2. Create data/nvidia_corpus/ with 10 documents + sources.yaml + README
3. Create src/rag/schemas.py
4. Create src/rag/ingestion.py (replace stub)
5. Create src/rag/retrieval.py (replace stub)
6. Create src/rag/playbook_retriever.py (new)
7. Update src/rag/__init__.py
8. Create tests/ (3 files, 9+ tests)
9. Create docs/35 and docs/contracts/rag_contract.md
10. Update EVALS, README, ROADMAP, DECISIONS
11. Obsidian backfill
12. pytest, ruff, black, mypy

## Out of Scope

- No vector DB (Qdrant)
- No embeddings
- No scraping
- No external calls
- No LangGraph
- No changes to scoring/, diagnosis/, recommendation/, briefing/
- No new dependencies

## Tests/Validations

```bash
pytest
ruff check .
black --check .
mypy src
```

## Definition of Done

- [ ] 9+ RAG tests passing (total 162+)
- [ ] ruff, black, mypy sem erros novos
- [ ] 10 corpus files loadable
- [ ] retrieval returns provenance
- [ ] missing_context explicit
- [ ] docs/35 done, rag_contract done
- [ ] EVALS, README, ROADMAP, DECISIONS updated
- [ ] Obsidian updated

---

*Gerado em: 2026-06-09*
