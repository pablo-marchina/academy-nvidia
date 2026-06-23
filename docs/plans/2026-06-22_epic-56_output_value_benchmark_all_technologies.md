# Epic 56 - Output-Value Benchmark for All Technologies

## Context

The complete catalog benchmark currently proves that every roadmap candidate is represented and classified, but category proxies do not prove that a technology improves the product output. The benchmark must answer the product decision question: what should be added because it measurably improves recommendations, evidence coverage, RAG grounding, confidence, missing-evidence handling, latency, cost, or risk.

## Scope

- Reclassify category proxy benchmark results so they do not become `BENCHMARKED`.
- Keep direct executable checks as `BENCHMARKED` only when they run a concrete local task.
- Add an output-value decision report for every catalog technology.
- Emit explicit decisions: add/promote, keep active runtime, reject by evidence, future research, or needs direct output-value benchmark.
- Integrate the new report into the evidence pack and quick proof.
- Add tests for proxy status, promotion decisions, and complete-catalog output-value reporting.

## Non-Scope

- Do not promote paid SaaS, external APIs, hardware, or licensed products without direct benchmark evidence.
- Do not claim proxy category evidence proves runtime value.
- Do not change the core recommendation/RAG algorithm in this increment unless the benchmark identifies an already implemented local feature with measurable value.

## Acceptance Criteria

- `scripts/run_benchmark.py --suite complete-catalog` produces 408 results but only direct executable candidates are `BENCHMARKED`.
- Category proxies are recorded as configured coverage and blocked from runtime promotion.
- `final_case_evidence/output_value_benchmark_report.json` exists and includes all candidates.
- `final_case_evidence/candidate_promotion_recommendations.json` states what should be added or kept based on evidence.
- `python scripts/prove_final_product.py --quick --skip-live` passes.

## Validation

- Focused pytest for benchmark and gates.
- Focused ruff, black, and mypy on touched modules.
- Quick final proof.
