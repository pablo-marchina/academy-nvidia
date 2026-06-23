# Plan: Epic 80 Final Audit Remediation

## Objective

Address the actionable P0/P1/P2 findings from `adicoes_alteracoes_nvidia_startup_ai_radar.md` with honest evidence. This epic closes repository-level gaps that can be fixed locally, runs available validation gates, and records environment-dependent blockers without converting them into false product readiness.

## Context Read

- `AGENTS.md`
- `.ai/project_context.md`
- `C:/Users/Inteli/Downloads/adicoes_alteracoes_nvidia_startup_ai_radar.md`
- `docs/contracts/product_configuration_contract.md`
- `docs/contracts/product_acceptance_contract.md`
- `docs/contracts/rag_contract.md`
- `docs/contracts/recommendation_contract.md`
- recent plans under `docs/plans/`

## Relevant Files

- `.env.example`
- `.env.production.example`
- `src/services/product/health_executor.py`
- `src/services/product/config_registry.py`
- `src/services/product/capability_registry.py`
- `src/interface/app.py`
- `scripts/run_llm_security_suite.py`
- `scripts/prove_final_product.py`
- `scripts/local_proof_doctor.py`
- `scripts/package_final_release.py`
- `final_case_evidence/*`
- focused tests under `tests/unit/`, `tests/security/`, `tests/acceptance/`

## Scope

- Align LLM judge configuration variables across configuration registry, health checks, docs, and tests.
- Remove or reclassify active runtime-adjacent `demo`/`placeholder` language where it affects product capabilities.
- Add or harden production configuration example and validation expectations.
- Run feasible local product proof, frontend build, security suite, and focused tests.
- Preserve honest `BLOCKED_BY_ENVIRONMENT` status for Docker, PostgreSQL, Qdrant, live source review, scanners, and network-dependent tools when unavailable.
- Summarize remaining P0/P1/P2 blockers with exact commands and evidence files.

## Out of Scope

- No fabricated PASS for scanners, live sourcing, Docker, PostgreSQL, Qdrant, or external services not available in this environment.
- No broad rewrite of the product architecture.
- No activation of paid or credentialed providers without user-provided secrets.
- No deletion or restoration of pre-existing unrelated working-tree changes.
- No frontend redesign beyond build/readiness fixes required by the audit.

## Proposed Implementation

1. Inspect current implementation around LLM judge, product configuration, product capabilities, frontend build scripts, and security suite.
2. Patch narrow code/docs inconsistencies:
   - `health_executor.py`: use `ANSWER_QUALITY_LLM_JUDGE_PROVIDER` as canonical provider key, with explicit legacy compatibility if needed.
   - `capability_registry.py` and `src/interface/app.py`: remove active `demo`/`placeholder` wording from product-facing definitions.
   - `.env.example` / `.env.production.example`: make product mode requirements explicit and align LLM judge env names.
3. Add or update focused tests for configuration alignment and capability wording.
4. Run focused tests for modified modules plus existing no-demo/no-mock/security/product proof tests.
5. Attempt frontend build and available proof scripts; capture real failures or blockers.
6. Package or verify the final release artifact only if validation gates allow it.
7. Report completed fixes, generated evidence, and unresolved blockers honestly.

## Files to Create/Change

### Create

- `.env.production.example` - explicit production configuration template if missing.

### Change

- `src/services/product/health_executor.py` - LLM judge provider env alignment.
- `src/services/product/capability_registry.py` - product-facing frontend capability wording.
- `src/interface/app.py` - non-runtime interface wording.
- `.env.example` - product/readiness env alignment.
- focused tests as needed under `tests/unit/`.

## Tests/Validations

- `pytest tests/unit/test_health_executor.py tests/unit/test_product_configuration_registry.py`
- `pytest tests/acceptance/test_no_demo_dependency.py tests/acceptance/test_no_mock_in_production.py`
- `pytest tests/security`
- `python scripts/run_llm_security_suite.py`
- `python scripts/prove_final_product.py`
- `cd frontend && npm run build`
- `python scripts/package_final_release.py` if preceding gates are acceptable.

## Risks

| Risk | Mitigation |
|------|------------|
| Existing working tree has many user changes | Touch only files required by this epic and inspect before editing. |
| Environment lacks Docker/Postgres/Qdrant/scanners/network | Preserve `BLOCKED_BY_ENVIRONMENT` with remediation commands and do not mark as PASS. |
| LLM judge provider support is optional/experimental | Align health checks to canonical env names without requiring real provider by default. |
| Frontend build may fail due local permissions/dependencies | Attempt build, record exact failure, and only fix repository-caused issues. |

## Definition of Done

- [ ] Plan saved in `docs/plans/`.
- [ ] LLM judge env variable mismatch resolved or explicitly documented.
- [ ] Runtime-adjacent `demo`/`placeholder` wording removed or reclassified.
- [ ] Production env template exists and matches product readiness expectations.
- [ ] Focused tests pass or failures are documented with cause.
- [ ] Product proof/security/frontend commands are attempted with real outcomes.
- [ ] Remaining blockers are listed as environment, credential, or implementation blockers.

## End-of-Epic Closure Checklist

- [ ] `pytest` focused checks pass.
- [ ] `ruff check .` considered or run for touched Python files.
- [ ] `black --check .` considered or run for touched Python files.
- [ ] `mypy src` considered or run when type surface changes.
- [ ] README/ROADMAP/DECISIONS/EVALS updated only if scope requires durable product status changes.
- [ ] No dependency added without justification.
- [ ] No feature is documented as active runtime without evidence.

---

*Gerado em: 2026-06-23*
*Modo: Plan -> Artifact -> Build -> Review*
