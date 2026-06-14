# Plan: Epic 42 — Hybrid RAG + Reranking Hardening

## Objective

Add sparse (BM25) retrieval, deterministic query planning, RRF/weighted fusion,
cross-encoder reranking, citation packages, and Claim Ledger/Dossier/Product Quality
integration to the existing RAG pipeline — without replacing Qdrant or rewriting
the existing pipeline.

## Context Read

- AGENTS.md, DECISIONS.md, ROADMAP.md, EVALS.md, README.md
- `src/rag/` — all existing modules
- `src/services/product/` — claim_ledger, dossier_service, capability_registry, config_registry
- `src/quality/` — constants, evaluators (base, evidence_coverage, rag_quality)
- `src/evaluation/` — rag_eval_schemas, rag_eval
- `.env.example`, `docs/contracts/rag_contract.md`, `docs/69_hybrid_rag_reranking.md`

## Relevant Files

### Create
- `src/rag/schemas.py` — +RetrievalMode enum, RagEvidenceChunk, QueryPlan, RagEvidenceChunkList
- `src/rag/query_planner.py` — deterministic query planner from startup context
- `src/rag/sparse_retrieval.py` — BM25 local sparse retriever
- `src/rag/fusion.py` — RRF + weighted score fusion
- `src/rag/reranker.py` — Reranker ABC, NoOpReranker, OptionalCrossEncoderReranker, factory
- `src/rag/hybrid_retriever.py` — HybridRagRetriever service
- `src/rag/citation.py` — CitationPackage with citations/evidence_refs/source_coverage
- `src/rag/evidence_refs.py` — helpers for Claim Ledger + Dossier integration
- `src/quality/evaluators/rag_quality.py` — evaluate_rag_retrieval()
- `tests/unit/test_hybrid_rag.py` — 31 tests

### Change
- `src/quality/constants.py` — +6 RAG metric constants + thresholds
- `src/services/product/config_registry.py` — +9 hybrid RAG config items
- `src/services/product/capability_registry.py` — +5 RAG capabilities
- `.env.example` — +9 hybrid RAG env vars

## Scope

- Sparse retrieval: BM25 local (pure Python, no Qdrant sparse vectors)
- Query planner: deterministic string/keyword logic (no LLM)
- Fusion: RRF default, weighted score alternative
- Reranker: NoOpReranker default, OptionalCrossEncoderReranker (lazy-loaded)
- Citation package: structured citations, evidence_refs, source coverage
- Integration helpers: Claim Ledger (evidence_refs_from_chunks), Dossier (optional citation section)
- Product Quality: evaluate_rag_retrieval() metrics evaluator
- Config/capability registry updates for all new components
- Unit tests for all new modules

## Out of Scope

- No changes to existing RAG pipeline, Qdrant ingestion, LangGraph nodes
- No LLM query planner (noted for future)
- No Ragas integration (noted as optional future step)
- No changes to scoring, diagnosis, recommendation, Action Brief
- No frontend changes
- No schema changes to existing database models

## Proposed Implementation

1. Add RetrievalMode enum and RagEvidenceChunk/QueryPlan/RagEvidenceChunkList to schemas
2. Implement query_planner.py with deterministic build_query_plan()
3. Implement sparse_retrieval.py with BM25-local scoring
4. Implement fusion.py with RRF + weighted score fusion
5. Implement reranker.py with Reranker ABC, NoOpReranker, OptionalCrossEncoderReranker
6. Implement hybrid_retriever.py with HybridRagRetriever orchestrator
7. Implement citation.py with CitationPackage factory
8. Implement evidence_refs.py with Claim Ledger helpers
9. Update config_registry.py and capability_registry.py
10. Update .env.example with RAG env vars
11. Add RAG metrics to quality/constants.py and evaluators/rag_quality.py
12. Write 31 unit tests
13. Create plan document and contract

## Tests/Validations

- `pytest tests/unit/test_hybrid_rag.py -v` — 31 tests (query planner, sparse, fusion, reranker, citation, evidence refs)
- `ruff check src/rag/ tests/unit/test_hybrid_rag.py`
- `black --check src/rag/ tests/unit/test_hybrid_rag.py`
- `mypy src/rag/`

## Risks

| Risk | Mitigation |
|------|-----------|
| CrossEncoder model not available | OptionalCrossEncoderReranker gracefully falls back to NoOp |
| BM25 over pure lexical may not add value | Fusion defaults weight dense=0.5, sparse=0.5; configurable |
| New modules increase maintenance surface | All modules have pure functions, few deps, full test coverage |

## Definition of Done

- [ ] All new modules implemented and tested
- [ ] 31 tests passing
- [ ] ruff/black/mypy passing
- [ ] Config and capability registries updated
- [ ] .env.example updated
- [ ] Plan document saved
- [ ] Contract created at docs/contracts/hybrid_rag_contract.md
- [ ] EVALS.md, ROADMAP.md, DECISIONS.md, README.md updated

---

*Gerado em: 2026-06-13*
*Modo: Plan → Build*
