# Known Limitations

- Output Validation Gate is structural and contract-focused. It catches missing
  fields, invalid enums, empty critical sections, placeholder text, and mapping
  inconsistencies, but it does not provide semantic entailment or replace human
  review.

## CI/CD & Quality Gates

- CI only tests on Ubuntu — no Windows/macOS matrix.
- Integration tests excluded from CI (require QDRANT_TEST_URL).
- Pre-commit hooks not auto-installed — developer must run `pre-commit install`.
- `check_scope.py` relies on `git diff HEAD` — may behave unexpectedly during rebase.
- `check_scope.py` does not validate file content, only file paths.
- Makefile requires `make` (available via `choco install make` or git-bash on Windows).
- No coverage threshold enforcement in CI yet.

## Capability & Configuration Registry (Epic 36.1)

- Capability status is environment-driven — config changes require a restart.
- New capabilities must be registered manually in `capability_registry.py` (no auto-discovery).
- `not_configured` for optional features may confuse users until they read the `status_reason`.
- No mechanism to auto-detect new env vars added at runtime.
- Readiness service does not verify that required services (e.g., Qdrant server) are actually reachable — only checks if their env vars are configured.
- No caching — every API call recomputes all capability statuses.
- 4 new API endpoints (capabilities, configuration, setup-checklist, readiness) are unchanging data — they do not need database querying, but are served via the API layer for consistent access.

## Product

- The pipeline uses deterministic heuristics, not an LLM, for all scoring and diagnosis steps.
- Scraping collects from a single public URL — no crawling in scale.
- RAG semantic/hybrid retrieval requires the optional `rag` extra for real embeddings: `pip install -e ".[rag]"` (mock provider used in tests).
- Qdrant ingestion with `sentence-transformers/all-MiniLM-L6-v2` requires `QDRANT_VECTOR_SIZE=384`.
- RAG evaluation multi-mode comparison uses `MockEmbeddingProvider` by default.
- Answer quality evaluation is deterministic and pattern-based; it is not a semantic LLM judge and does not prove entailment.
- Answer Quality JUnit reports expose pytest operational counters; they do not add new semantic quality metrics beyond the deterministic harness.
- Corpus is allowlist-backed in `data/nvidia_corpus/`; sync/promotion and ingestion remain explicit controlled steps.
- Vector store is in-memory by default, with optional QdrantStore for persistence.
- Context packing uses configurable limits (per-tech=2, per-gap=3, global=5).
- Recommendation Engine is deterministic (no LLM).
- No human-in-the-loop technically implemented.
- No integration tests exist — all tests are unit tests (9 integration tests skippable).
- Golden eval and answer quality harnesses exist under `tests/evals/`, but they use curated offline fixtures.
- Agents (`src/agents/`), database (`src/database/`), and interface (`src/interface/`) are stubs.
- Corpus maintenance has a safe scheduled workflow, but it does not promote sources or run real Qdrant ingestion automatically.
- Existing Qdrant collections need reingestion to receive Epic 20 lifecycle payload fields.
- Stale corpus content is reported by audit but not yet surfaced as an Action Brief warning.
- Regression dashboard consolidates existing reports only; missing required reports become `WARN`, optional answer quality reports are read when present, and JUnit eval reports expose pass/fail plus failed cases rather than full semantic metrics.
- Optional LLM judge reports are experimental and informational only. Epic 23.2
  implements a deterministic offline null provider, not a semantic model or real
  provider integration.
- CLI demo uses a fictional startup sample input — not a real startup.
- CLI demo answer quality eval uses a generic case, not golden cases.
- CLI demo requires a local corpus (`data/nvidia_corpus/`) for RAG to provide context.
- FastAPI API is local/dev only — no authentication, no rate limiting, no cloud deployment.
- API pipeline runs synchronously (may block for several seconds per request).
- POST /brief with RAG enabled and no corpus still succeeds but returns `warnings`.

# API (Epic 25)

- No authentication — local/dev only.
- Pipeline runs synchronously — may block for several seconds per request.
- Qdrant status checks connectivity but not data freshness.
- GET /demo/artifacts returns empty list when `data/demo_runs/` does not exist.

## Product UI (Epic 37)

- State-based routing — no URL-based navigation, deep linking, or browser back/forward support.
- No auth/roles — any user can access all views.
- No loading skeletons — uses simple "Loading..." text.
- No optimistic updates — mutations wait for server response.
- No error recovery UI — errors are shown via alert-style banner, not retry prompts.
- No pagination on startups table (returns all startups at once; future: server-side pagination).
- No pagination on evidence/claims within startup detail.
- No charts or visualizations — all data displayed as text/tables.
- Opportunities pagination is client-driven via offset/limit (server returns all opportunities, UI paginates).
- DossierView auto-generates dossier if GET returns 404 — may produce duplicate if creation fails silently.
- ReviewForm submits to server but does not refresh reviews list automatically after submit (manual nav reset).
- No E2E tests run in CI (requires browser + running backend server).

## Startup Discovery Engine (Epic 40)

- Signal detection is keyword-only — may miss AI-native startups that don't use common keywords.
- No broad crawling — discovery depends on user-provided seeds and curated source lists.
- URL list importer may fail on domains with strict rate limits or bot protection.
- Static HTML collection methods (distrito, ace, bossa, inovativa) are defined but not yet implemented as automatic collectors — only manual_seed and configured_url_list work.
- Dedup by normalized_name + domain only — no fuzzy matching for similar names with different domains.
- No LLM-based signal enrichment — all signals are deterministic keyword matches.
- Discovery does not automatically trigger AnalysisRun on promotion — user must run analysis manually.
- No scheduled/periodic discovery — all discovery runs are manually triggered via API.
