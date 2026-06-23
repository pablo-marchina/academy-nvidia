# Epic 74: Value Family Completeness Audit

## Summary

Add an explicit audit for whether the project has discovered every value-generating family and every value-generating technique inside those families.

The report must distinguish:

- families with product-spike lift already implemented;
- families with diagnostic signal but no product implementation;
- roadmap categories that are cataloged but not deeply tested for output-quality lift;
- alternatives inside implemented families that still need direct comparison.

## Scope

- Add `scripts/check_value_family_completeness.py`.
- Generate JSON and Markdown evidence reports.
- Integrate the report into the evidence pack and quick proof.
- Add focused unit tests.

## Honest Policy

This audit must not claim exhaustive certainty unless every roadmap category and every technique inside each family has a direct baseline-vs-candidate output-quality benchmark. With the current evidence, the expected conclusion is partial coverage, not final closure.

## Public Interfaces

- `python scripts/check_value_family_completeness.py --evidence-dir final_case_evidence`
- `final_case_evidence/value_family_completeness_report.json`
- `final_case_evidence/value_family_completeness_report.md`

## Test Plan

- Unit test report construction with implemented families and an uncovered roadmap category.
- Unit test that global completeness is false when direct alternative gaps exist.
- Run the script against current evidence.
- Run focused pytest, black, ruff, mypy, and quick final proof.

