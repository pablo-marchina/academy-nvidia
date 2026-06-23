# Epic 72: Full External Free Verification and Benchmark Run

## Context

The roadmap includes external services, tools, APIs, protocols, and paid/SaaS candidates. The project policy allows free external APIs and services, but only when free/no-cost access is explicitly verified and benchmark evidence is generated.

## Goal

Verify every external `FUTURE_RESEARCH` candidate from the canonical candidate catalog, classify free/no-cost benchmark eligibility, and run the available benchmark/probe paths for all candidates.

## Scope

- Expand `docs/free_external_candidate_registry.json` to cover every external future-research candidate from the document.
- Add a gate/report that checks the registry covers all external candidates.
- Allow both local/open-source free tools and verified free development APIs to enter the benchmark queue.
- Run complete catalog benchmarks and external free probes.
- Preserve blocked/unverified statuses as evidence, not failures.

## Non-goals

- Do not claim paid or trial-only services are free.
- Do not use paid credentials or hidden manual steps.
- Do not promote candidates without measured output-quality lift.

## Validation

- Focused unit tests.
- `scripts/run_benchmark.py --suite complete-catalog`.
- `scripts/check_external_free_verification.py`.
- `scripts/review_free_external_candidates.py`.
- `scripts/run_free_external_candidate_benchmarks.py`.
- `scripts/prove_final_product.py --quick --skip-live`.
