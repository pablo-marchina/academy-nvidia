# Epic 71: Free External Candidate Operational Benchmark Recipes

## Context

The free external candidate probe now identifies six no-cost/open-source candidates, but all are blocked in this environment because their local CLIs or modules are not installed. A direct Phoenix install attempt also failed on Windows/Python due to native build requirements for a transitive dependency.

## Goal

Make the blocked state operationally useful by adding explicit benchmark recipes for every eligible free external candidate:

- value hypothesis;
- output-quality metrics;
- local activation/install command;
- benchmark command;
- adoption guardrail;
- environment blocker.

## Scope

- Extend `run_free_external_candidate_benchmarks.py`.
- Add `make benchmark-free-external`.
- Add tests for recipe fields and blocked/ready classification.
- Keep all external candidates blocked unless the actual tool is installed/importable.

## Non-goals

- Do not install tools automatically.
- Do not promote any candidate from a probe.
- Do not call external APIs or networks from quick proof.

## Validation

- Focused pytest.
- Focused ruff and black.
- Quick final proof with live collection skipped.
