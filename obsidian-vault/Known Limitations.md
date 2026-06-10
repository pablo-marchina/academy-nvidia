# Known Limitations

## CI/CD & Quality Gates

- CI only tests on Ubuntu — no Windows/macOS matrix.
- Integration tests excluded from CI (require QDRANT_TEST_URL).
- Pre-commit hooks not auto-installed — developer must run `pre-commit install`.
- `check_scope.py` relies on `git diff HEAD` — may behave unexpectedly during rebase.
- `check_scope.py` does not validate file content, only file paths.
- Makefile requires `make` (available via `choco install make` or git-bash on Windows).
- No coverage threshold enforcement in CI yet.

## Product

- The pipeline uses deterministic heuristics, not an LLM, for all scoring and diagnosis steps.
- Scraping collects from a single public URL — no crawling in scale.
- RAG semantic/hybrid retrieval requires the optional `rag` extra for real embeddings: `pip install -e ".[rag]"` (mock provider used in tests).
- Qdrant ingestion with `sentence-transformers/all-MiniLM-L6-v2` requires `QDRANT_VECTOR_SIZE=384`.
- RAG evaluation multi-mode comparison uses `MockEmbeddingProvider` by default.
- Corpus is manually curated in `data/nvidia_corpus/` (10 documents — no automated ingestion).
- Vector store is in-memory only (no persistence across sessions).
- Context packing uses configurable limits (per-tech=2, per-gap=3, global=5).
- No automated ingestion script for populating Qdrant from the corpus.
- Recommendation Engine is deterministic (no LLM).
- No human-in-the-loop technically implemented.
- No integration tests exist — all tests are unit tests (9 integration tests skippable).
- No eval harness exists — `tests/evals/` is empty.
- Agents (`src/agents/`), database (`src/database/`), and interface (`src/interface/`) are stubs.
- Corpus maintenance has a safe scheduled workflow, but it does not promote sources or run real Qdrant ingestion automatically.
- Existing Qdrant collections need reingestion to receive Epic 20 lifecycle payload fields.
- Stale corpus content is reported by audit but not yet surfaced as an Action Brief warning.
