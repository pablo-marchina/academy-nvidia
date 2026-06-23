# Epic 58 - Ranked Value Benchmark Funnel

## Context

The correct adoption workflow is not to mark every roadmap technology as benchmarked. Technologies should be ranked by expected output-quality value, then benchmarked in that order. Once a moving window of candidates produces no quality lift, the process can stop and preserve the evidence.

## Scope

- Add a ranked benchmark queue for candidate changes.
- Add a sequential runner with stop conditions.
- Benchmark only executable, product-relevant change variants against a baseline.
- Mark non-executable candidates as requiring implementation, not as quality-benchmarked.
- Write evidence reports for ranked order, executed benchmarks, stop reason, and adoption decisions.

## Candidate Ranking Heuristic

Prioritize candidates that can plausibly improve product output quality:

1. RAG/retrieval and GraphRAG techniques.
2. Evidence verification, abstention, contradiction, and source trust.
3. Recommendation ranking/scoring.
4. Security guardrails that prevent unsafe unsupported claims.
5. Sourcing techniques that improve evidence coverage.
6. Observability/release/runtime tools only after output-quality candidates are exhausted.

## Stop Rule

Stop after a configurable number of consecutive executable candidates fail to improve quality. Non-executable candidates do not count against the stop window; they are implementation backlog.

## Acceptance Criteria

- `scripts/rank_value_candidates.py` writes a ranked queue.
- `scripts/run_ranked_value_benchmarks.py` runs executable candidates in order.
- Reports are written under `final_case_evidence/`.
- The report distinguishes `ADOPT`, `REJECT_NO_LIFT`, and `IMPLEMENTATION_REQUIRED`.
- Focused tests and quick proof pass.
