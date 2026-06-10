# Epic 17 — End-to-End Golden Eval Harness

**Status:** Done

**Summary:** Created regression detection harness with 7 golden pipeline cases (JSON) and 38 offline tests. Covers full pipeline output spectrum: high-fit, weak-evidence, non-AI, RAG edge cases. All tests run in CI via `pytest -m "not integration"` with MockEmbeddingProvider + InMemoryVectorStore.

**Test count:** 358 total (329 pre-existing + 38 golden evals)

**Key decisions:**
- Golden cases as JSON files (not inline dicts) — versioned, reviewable, loadable without Python
- Expected outputs use ranges/lists (motion_in, min_score, max_score) for tolerance
- RAG golden cases compare with-RAG vs without-RAG in a single test
- No new dependencies, no changes to `src/`

**See also:** Decision 025, `docs/41_end_to_end_eval_harness.md`, `EVALS.md`
