# Decision 025 — Golden Eval Harness

**Context:** 329 tests but zero end-to-end golden evaluations. Pipeline regressions undetectable by manual review.

**Decision:** 7 JSON golden cases at `examples/golden/` + 38 tests at `tests/evals/` with 11 assert helpers. Offline, deterministic, no external dependencies.

**Key files:**
- `examples/golden/` — 7 versioned golden cases
- `tests/evals/helpers.py` — GoldenCase + helpers
- `tests/evals/test_pipeline_golden.py` — 38 tests

**See also:** DECISIONS.md Decision 025, `docs/41_end_to_end_eval_harness.md`
