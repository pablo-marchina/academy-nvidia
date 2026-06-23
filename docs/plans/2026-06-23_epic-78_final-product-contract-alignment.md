# Epic 78 - Final Product Contract Alignment

## Context

`alteracoes_final_product_nvidia_startup_ai_radar.md` defines the final-product
contract expected by the reviewer. The repository already contains many final
proof, governance, benchmark, and release scripts, but some public command names,
evidence artifact names, dependency extras, and source-intelligence interfaces do
not yet match the requested contract.

## Scope

1. Add public Makefile aliases required by the final-product document:
   `doctor`, `package-release`, and `audit-release-package`.
2. Keep existing commands working while aligning `prove-final-product` with the
   requested `--full` invocation.
3. Generate compatibility evidence artifacts requested by the document:
   `release_cleanliness_report.{json,md}`, `release_package_manifest.json`,
   `full_proof_run.json`, `full_proof_junit.xml`, and `runtime_bom.{json,md}`.
4. Expand `pyproject.toml` optional dependency groups to the requested matrix:
   `rag`, `agents`, `postgres`, `eval`, `security`, and `full`, while preserving
   existing extra names for backward compatibility.
5. Add source-intelligence package interfaces for registry, policy, health,
   discovery, scoring, coverage, and compliance with deterministic unit tests.
6. Extend the local proof doctor to report Python, Node, import, package-manager,
   and Playwright readiness in addition to service health.

## Out of Scope

- Live external scraping or paid/free-tier API verification in this turn.
- Replacing existing product API contracts that intentionally allow degraded RAG
  in acceptance mode.
- Removing unrelated dirty worktree changes or local generated artifacts.

## Validation

- `python -m pytest tests/unit/test_final_gate_scripts.py tests/unit/test_local_proof_doctor.py tests/unit/test_source_intelligence.py --tb=short`
- `python scripts/package_final_release.py`
- `python scripts/check_final_release_zip.py`
- `python scripts/prove_final_product.py --quick --skip-live`
