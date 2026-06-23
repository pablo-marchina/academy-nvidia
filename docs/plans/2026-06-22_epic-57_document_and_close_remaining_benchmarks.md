# Epic 57 - Document and Close Remaining Candidate Benchmarks

## Context

The benchmark evidence must answer whether each technology improves product output quality. The prior output-value layer correctly prevents adoption without quality lift, but many candidates still appear as needing a direct quality benchmark.

## Scope

- Add a benchmark documentation report that summarizes every candidate and decision.
- Run an adoption-readiness quality benchmark for all remaining candidates in the current product state.
- Mark candidates without integrated executable implementation as benchmarked for current adoption with zero quality lift and explicit implementation gap.
- Keep external SaaS/hardware/licensed candidates as future research until direct access is available.
- Keep adoption decisions conservative: add only when measured quality improves.
- Integrate the documentation artifact into final evidence generation and quick proof.

## Acceptance Criteria

- Every catalog candidate has a benchmark result and a documented decision.
- `final_case_evidence/all_candidate_benchmark_documentation.md` exists.
- `candidate_promotion_recommendations.json` answers what is added, kept, blocked, or rejected.
- Quick final proof passes.

## Validation

- Focused unit tests for documentation and remaining-candidate benchmark decisions.
- Focused ruff, black, mypy.
- `python scripts/prove_final_product.py --quick --skip-live`.
