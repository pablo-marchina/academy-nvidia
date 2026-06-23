# Epic 75: Direct Alternative Gap Benchmarks

## Summary

Run direct benchmarks for the cataloged alternatives inside the six implemented value families. The goal is to reduce the 63 direct alternative gaps without adding the separate `cost_latency_reliability_controls` family.

## Scope

- Add a direct alternative gap benchmark script.
- Compare each cataloged family alternative against the current implemented family score.
- Classify alternatives as:
  - `CURRENT_IMPLEMENTATION_COVERS_TECHNIQUE`
  - `DIRECT_BENCHMARK_NO_LIFT`
  - `DIRECT_BENCHMARK_LIFT`
  - `NEEDS_SEPARATE_IMPLEMENTATION`
- Generate JSON and Markdown evidence reports.
- Feed benchmark outcomes back into the implemented-family best-tool audit so resolved gaps are not counted forever.
- Integrate the script into quick final proof.
- Add focused unit tests.

## Non-Goals

- Do not add `cost_latency_reliability_controls`.
- Do not promote a new tool from conceptual similarity alone.
- Do not claim global best when a technique still needs separate implementation or external service access.

## Public Interfaces

- `python scripts/run_direct_alternative_gap_benchmarks.py --evidence-dir final_case_evidence`
- `final_case_evidence/direct_alternative_gap_benchmark_report.json`
- `final_case_evidence/direct_alternative_gap_benchmark_report.md`

## Test Plan

- Unit tests for covered/no-lift/lift/separate-implementation classifications.
- Unit tests that implemented-family best-tool audit consumes resolved gap evidence.
- Focused pytest, black, ruff, mypy.
- `python scripts/prove_final_product.py --quick --skip-live`.

