# Epic 77 - Final Release Product Closure

## Context

`finalization_changes_to_reach_final_product.md` requires the project to stop treating a
workspace ZIP as the final delivery artifact. The release must be allowlisted, audited,
benchmark-type aware, and backed by final governance/security/compliance evidence.

## Scope

1. Add an official final release packaging command that builds
   `release/academy-nvidia-final-case.zip` from an allowlist.
2. Add a ZIP cleanliness gate that opens the generated archive and blocks forbidden
   artifacts such as `.env`, `.git`, `node_modules`, caches, local builds, logs, and local
   databases.
3. Generate the requested final release evidence reports in `final_case_evidence/`.
4. Add `benchmark_type` to candidate catalog, benchmark result summaries, and decision
   ledger outputs, with gates that block proxy/local-readiness-only runtime promotion.
5. Add final documentation/evidence artifacts for external reviewer mode, incident
   response, RCA, deprecation, data retention, quality regression, governance maturity,
   access-control-aware RAG, least-context/data minimization, context firewall, source
   coverage, and agent/tool observability.
6. Wire the new gates into `make prove-final-product` and add focused unit tests.

## Out of Scope

- Running live external scanners that require missing binaries or network access.
- Changing product API behavior unrelated to final release governance.
- Removing unrelated user/worktree changes already present.

## Validation

- `python -m pytest tests/unit/test_final_gate_scripts.py --tb=short`
- `python scripts/package_final_release.py`
- `python scripts/check_final_release_zip.py`
- `python scripts/prove_final_product.py --quick --skip-live`
