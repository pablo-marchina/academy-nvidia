# Plan: Epic 50 Final Benchmark-First Roadmap

## Objective

Implement `final_final_benchmark_first_roadmap_all_changes.md` as the canonical final-product roadmap for NVIDIA Startup AI Radar. This epic introduces governance schemas, candidate cataloging, benchmark infrastructure, final evidence artifacts, release gates, live-collection controls, and a one-command proof target without pretending that every candidate has already been promoted to runtime.

## Context Read

- `.ai/project_context.md`
- `AGENTS.md`
- `final_final_benchmark_first_roadmap_all_changes.md`
- `docs/contracts/product_acceptance_contract.md`
- `docs/contracts/product_configuration_contract.md`
- `docs/contracts/rag_contract.md`
- `docs/contracts/scoring_contract.md`
- `docs/contracts/recommendation_contract.md`
- `docs/contracts/evidence_contract.md`
- `Makefile`
- `pyproject.toml`

## Relevant Files

- `src/governance/` for final roadmap schemas, evidence artifact helpers, and candidate parsing.
- `src/evaluation/benchmark_runner.py`, `dataset_registry.py`, `result_store.py` for the benchmark harness.
- `scripts/` for final gates and proof orchestration.
- `final_case_evidence/` for generated reports, ledgers, registries, manifests, and benchmark outputs.
- `docs/final_*.md` for canonical delivery documentation.
- `tests/unit/` for focused governance, benchmark, and gate coverage.

## Scope

- Treat the final roadmap markdown as the canonical source of candidate technologies and policies.
- Create typed Pydantic schemas for governance records, ledgers, evidence, risks, incidents, and status taxonomy.
- Generate initial final evidence artifacts from code and canonical inputs.
- Add benchmark harness primitives with cost, latency, risk, decision ledger, calibration registry, ablation, sensitivity, and regression budget support.
- Add gate scripts for numeric governance, candidate catalog, repository cleanliness, source compliance, lineage coverage, security/release checks, and final proof orchestration.
- Add Makefile targets: `setup`, `benchmark`, `evidence-pack`, `live-collect`, and `prove-final-product`.
- Reconcile final documentation around product-mode requirements and benchmark-first delivery.

## Out of Scope

- Promoting every listed candidate to runtime in one patch.
- Adding paid SaaS credentials, proprietary tools, or secrets to the repository.
- Faking benchmarks for unavailable candidates.
- Removing user-local ignored artifacts such as `.venv` or `reports/`.
- Replacing existing product API behavior outside the final readiness/gate path.

## Proposed Implementation

1. Add governance schemas and CSV/JSON artifact helpers.
2. Parse all section 8 candidate technologies from the canonical roadmap into `candidate_catalog.csv`.
3. Add a deterministic benchmark runner and result store that can benchmark local substitutes and record blocked/unavailable candidates explicitly.
4. Add scripts for evidence pack generation and final gates.
5. Add Makefile targets that call the new scripts.
6. Add canonical final docs and tests.
7. Run focused unit tests and final gate smoke checks.

## Files to Create/Change

### Create
- `src/governance/schemas.py` - final roadmap status taxonomy and Pydantic schemas.
- `src/governance/artifacts.py` - candidate parsing and evidence artifact generation.
- `src/evaluation/benchmark_runner.py` - benchmark orchestration primitives.
- `src/evaluation/dataset_registry.py` - benchmark dataset registry.
- `src/evaluation/result_store.py` - benchmark result persistence.
- `scripts/generate_final_evidence_pack.py` - generate final evidence files.
- `scripts/run_benchmark.py` - benchmark CLI.
- `scripts/live_collect.py` - live source compliance collection CLI.
- `scripts/prove_final_product.py` - one-command proof orchestrator.
- `scripts/check_numeric_governance.py` - numeric governance gate.
- `scripts/check_repository_clean.py` - repository cleanliness gate.
- `scripts/check_candidate_catalog.py` - candidate catalog completeness gate.
- `scripts/check_source_compliance.py` - source compliance gate.
- `scripts/check_lineage_coverage.py` - lineage coverage gate.
- `scripts/check_security_release.py` - security/release artifact gate.
- `docs/final_delivery_index.md` - evaluator entrypoint.
- `docs/final_runtime_contract.md` - product runtime contract.
- `docs/final_benchmark_first_policy.md` - adoption policy.
- `docs/final_candidate_technology_and_technique_catalog.md` - catalog documentation.
- `docs/final_eval_plan.md` - final evaluation plan.
- `docs/final_security_risk_plan.md` - security and risk plan.
- `tests/unit/test_governance_schemas.py` - schema coverage.
- `tests/unit/test_governance_artifacts.py` - artifact generation coverage.
- `tests/unit/test_benchmark_runner.py` - benchmark harness coverage.
- `tests/unit/test_final_gate_scripts.py` - final gate smoke tests.

### Change
- `Makefile` - add final roadmap targets.
- `README.md`, `ROADMAP.md`, `EVALS.md`, `DECISIONS.md` - record final benchmark-first capability and validation path.

## Tests/Validations

- `python -m pytest tests/unit/test_governance_schemas.py tests/unit/test_governance_artifacts.py tests/unit/test_benchmark_runner.py tests/unit/test_final_gate_scripts.py -q`
- `python scripts/generate_final_evidence_pack.py`
- `python scripts/check_candidate_catalog.py`
- `python scripts/check_numeric_governance.py`
- `python scripts/check_repository_clean.py`
- `python scripts/check_lineage_coverage.py`
- `python scripts/check_security_release.py`

## Risks

| Risk | Mitigation |
|------|------------|
| The roadmap lists hundreds of candidates that cannot all be benchmarked locally. | Catalog every candidate, benchmark local substitutes where needed, and block runtime promotion without direct evidence. |
| Live collection can fail due to network, robots, terms, or external instability. | Record explicit source status and fail only when mandatory calibrated sources are missing. |
| New gates could over-block local development. | Make strict product proof explicit under `make prove-final-product`; focused gates stay deterministic. |
| Documentation can drift from code. | Generate evidence artifacts from typed schemas and add docs/gate checks. |

## Definition of Done

- [ ] Plan is saved in `docs/plans/`.
- [ ] Governance schemas and final artifact generation are implemented.
- [ ] Candidate catalog is generated from the canonical roadmap.
- [ ] Benchmark harness and final gate scripts exist with tests.
- [ ] `make prove-final-product` exists and prints `FINAL_PRODUCT_STATUS=PASS_OR_FAIL`.
- [ ] Final docs point evaluators to the proof path and evidence pack.

## End-of-Epic Closure Checklist

- [ ] `pytest` passa sem erros.
- [ ] `ruff check .` passa sem erros.
- [ ] `black --check .` passa sem erros.
- [ ] `mypy src` passa sem erros.
- [ ] `README.md` atualizado com Current Capabilities e Known Limitations.
- [ ] `ROADMAP.md` atualizado com status real do epico.
- [ ] `DECISIONS.md` atualizado com decisoes arquiteturais do epico.
- [ ] `EVALS.md` atualizado com baseline de testes e cobertura.
- [ ] `ERROR_LOG.md` revisado e atualizado se houve erros.
- [ ] `docs/` - documentacao relevante atualizada ou criada.
- [ ] `obsidian-vault/` - backfill realizado.
- [ ] Nenhuma dependencia nova foi adicionada sem justificativa.
- [ ] Nenhuma feature fantasma foi documentada.

---

*Gerado em: 2026-06-21*  
*Modo: Plan -> Artifact -> Build -> Review -> Commit*
