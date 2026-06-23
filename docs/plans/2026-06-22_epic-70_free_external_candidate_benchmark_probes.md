# Epic 70: Free External Candidate Benchmark Probes

## Context

Epic 69 created a registry and review report for free external candidates. The ranked queue can now include eligible external tools, but the proof still needs an explicit benchmark/probe report that says whether each tool was actually available and whether product-output benchmarking can proceed.

## Goal

Generate honest evidence for free external candidates:

- `BLOCKED_BY_ENVIRONMENT` when the local free/open-source tool is not installed or network/API access is not verified;
- `READY_FOR_PRODUCT_BENCHMARK` when the tool is locally available but still needs an output-quality product spike;
- never `ADOPT` or `PROMOTED_TO_RUNTIME` from availability alone.

## Scope

- Add a probe runner for eligible free external candidates.
- Integrate its report into the evidence pack and quick proof.
- Document the report as benchmark evidence, not runtime promotion.
- Add unit tests for installed/missing tool classification.

## Non-goals

- Do not install external tools automatically.
- Do not call external networks or APIs.
- Do not promote any external candidate without output-quality lift evidence.

## Validation

- Focused pytest for the probe runner and ranking tests.
- Focused ruff and black.
- Quick final proof with live collection skipped.
