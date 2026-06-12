# Plan: Epic 31 — Product Simplification & Deletion Pass

**Date:** 2026-06-12
**Mode:** Planning only. No functional changes or deletions in this document.

---

## 1. Executive Summary

Epics 28–30 built the product persistence layer, API, migrations, and review/export endpoints. The product flow now works independently from demo artifacts (data/demo_runs, demo API routes, demo CLI, demo UI).

Epic 31 prunes, archives, and isolates the demo heritage *safely*: preserving only what tests, evals, or CI depend on, and never removing anything that would break the product flow.

**Principle:** reduce complexity; do not add features; separate fact from inference; every deletion must be protected by a test or explicit justification.

## 2. Why This Pass Is Needed Now

1. **Demo is not the main flow.** The product API exists. Demo endpoints (/brief, /brief/evaluate, /demo/artifacts) coexist in the same FastAPI app and share src/api/service.py with _DEMO_RUNS_DIR -- a latent coupling that can mislead new contributors and agents.

2. **docs/54_final_product_backlog.md** (FPB-033, FPB-031, FPB-030) explicitly calls for archiving demo docs and deleting generated outputs *after* product API/export docs exist -- which they now do (product API contract v2.0, ExportRecord).

3. **Historical plans and early docs** (docs/00_* through docs/09_*, docs/25-28_*) contain statements superseded by contracts, evals, and the final backlog. Keeping them as active guidance risks re-introducing outdated assumptions.

4. **Obsidian Known Limitations** has stale entries ("Sem Docker Compose", "Sem CI/CD") that contradict the current project state.

5. **Test/temp corpus files** (archive_test.md, nim_test.md, temp_test_source.md) pollute data/nvidia_corpus/ and risk being ingested into Qdrant.

6. **data/demo_runs/latest/ files are committed to git** (not in .gitignore) -- generated artifacts should not be versioned.

## 3. Demo/Dead Artifact Inventory

| # | Path | Type | Description | Decision |
|---|---|---|---|---|
| D-01 | data/demo_runs/latest/demo_run_report.json | data | Generated demo run report | DELETE_NOW |
| D-02 | data/demo_runs/latest/startup_action_brief.json | data | Generated brief JSON | DELETE_NOW |
| D-03 | data/demo_runs/latest/startup_action_brief.md | data | Generated brief Markdown | DELETE_NOW |
| D-04 | examples/demo/sample_startup_input.json | data | Fictional sample used by tests + CLI | KEEP_AS_FIXTURE_OR_GOLDEN |
| D-05 | examples/demo/README.md | doc | Documents sample format | ARCHIVE_HISTORY |
| D-06 | scripts/run_startup_radar_demo.py | script | CLI demo entry point | REPLACE_BEFORE_DELETE |
| D-07 | src/api/routes.py | code | Demo API routes | DELETE_AFTER_TEST_UPDATE |
| D-08 | src/api/schemas.py | code | Demo API schemas | DELETE_AFTER_TEST_UPDATE |
| D-09 | src/api/service.py | code | Demo service with _DEMO_RUNS_DIR ref | DELETE_AFTER_TEST_UPDATE |
| D-10 | frontend/ (full dir) | frontend | Demo UI (Vite + React) | REPLACE_BEFORE_DELETE |
| D-11 | Makefile demo targets | config | demo-cli, demo-acceptance, etc. | DELETE_AFTER_TEST_UPDATE |

## 4. Documentation Pruning Inventory

| # | Path | Type | Description | Decision |
|---|---|---|---|---|
| DOC-01 | docs/08_demo_script.md | doc | 3-5 minute demo script | ARCHIVE_HISTORY |
| DOC-02 | docs/49_cli_demo_end_to_end.md | doc | Epic 24 design doc | ARCHIVE_HISTORY |
| DOC-03 | docs/50_minimal_fastapi_demo_api.md | doc | Epic 25 design doc | ARCHIVE_HISTORY |
| DOC-04 | docs/51_minimal_demo_ui.md | doc | Epic 26 design doc | ARCHIVE_HISTORY |
| DOC-05 | docs/52_demo_acceptance.md | doc | Epic 27 design doc | ARCHIVE_HISTORY |
| DOC-06 | docs/00_case_plan.md | doc | Original case/MVP plan | ARCHIVE_HISTORY |
| DOC-07 | docs/00_project_brief.md | doc | Early product framing | MERGE_INTO_LIVE_DOC |
| DOC-08 | docs/01_problem_definition.md | doc | Early problem definition | MERGE_INTO_LIVE_DOC |
| DOC-09 | docs/02_architecture.md | doc | Early architecture | MERGE_INTO_LIVE_DOC |
| DOC-10 | docs/03_data_contracts.md | doc | Early data contracts | MERGE_INTO_LIVE_DOC |
| DOC-11 | docs/04_agent_specs.md | doc | Planned agent specs | MERGE_INTO_LIVE_DOC |
| DOC-12 | docs/05_rag_design.md | doc | Early RAG design | ARCHIVE_HISTORY |
| DOC-13 | docs/06_recommendation_logic.md | doc | Recommendation rules | MERGE_INTO_LIVE_DOC |
| DOC-14 | docs/07_evaluation_plan.md | doc | Early eval plan | MERGE_INTO_LIVE_DOC |
| DOC-15 | docs/09_user_workflow.md | doc | Desired workflow | MERGE_INTO_LIVE_DOC |
| DOC-16 | docs/25_end_of_epic_closure.md | doc | Workspace governance | MERGE_INTO_LIVE_DOC |
| DOC-17 | docs/26_architecture_utilization_audit.md | doc | Audit history | ARCHIVE_HISTORY |
| DOC-18 | docs/27_developer_rag_design.md | doc | Dev RAG design | KEEP_AS_LIVE_DOC |
| DOC-19 | docs/28_development_workspace_quality.md | doc | Workspace quality | KEEP_AS_LIVE_DOC |
| DOC-20 | docs/52_workspace_clarification_gate.md | doc | Clarification gate | KEEP_AS_LIVE_DOC |
| DOC-21 | docs/53_workspace_output_validation_gate.md | doc | Output validation gate | KEEP_AS_LIVE_DOC |
| DOC-22 | docs/55_product_backend_foundation.md | doc | Epic 29 completion | KEEP_AS_LIVE_DOC |
| DOC-23 | docs/56_product_backend_completion.md | doc | Epic 30 completion | KEEP_AS_LIVE_DOC |

## 5. Data/Artifact Pruning Inventory

| # | Path | Type | Description | Decision |
|---|---|---|---|---|
| DA-01 | data/nvidia_corpus/archive_test.md | data | Test file in corpus dir | DELETE_NOW |
| DA-02 | data/nvidia_corpus/nim_test.md | data | Test file in corpus dir | DELETE_NOW |
| DA-03 | data/nvidia_corpus/temp_test_source.md | data | Temp file in corpus dir | DELETE_NOW |
| DA-04 | data/regression_reports/latest_dashboard.json | data | Generated report | DELETE_NOW |
| DA-05 | data/regression_reports/latest_dashboard.md | data | Generated report | DELETE_NOW |
| DA-06 | data/regression_reports/answer_quality_eval_junit.xml | data | Generated report | DELETE_NOW |
| DA-07 | data/regression_reports/answer_quality_llm_judge_report.json | data | Generated report | DELETE_NOW |
| DA-08 | data/regression_reports/answer_quality_llm_judge_report.md | data | Generated report | DELETE_NOW |
| DA-09 | data/ingestion_reports/*.json (7 files) | data | Generated ingestion reports | DELETE_NOW |
| DA-10 | data/ingestion_reports/*.md (2 files) | data | Generated ingestion reports | DELETE_NOW |
| DA-11 | data/product/product.db | data | Local SQLite DB (runtime) | DO_NOT_TOUCH |
| DA-12 | data/nvidia_corpus/sources.yaml | data | Source lifecycle manifest | KEEP_AS_LIVE_DOC |
| DA-13 | data/nvidia_corpus/source_allowlist.yaml | data | Source allowlist | KEEP_AS_LIVE_DOC |
| DA-14 | examples/golden/ (9 files) | data | Golden eval fixtures | KEEP_AS_FIXTURE_OR_GOLDEN |
| DA-15 | examples/rag_eval/ (2 files) | data | RAG eval fixtures | KEEP_AS_FIXTURE_OR_GOLDEN |
| DA-16 | examples/answer_quality/ (2 files) | data | Answer quality fixtures | KEEP_AS_FIXTURE_OR_GOLDEN |
| DA-17 | examples/validation/ (5 files) | data | Output validation fixtures | KEEP_AS_FIXTURE_OR_GOLDEN |

## 6. Script/API/Frontend Pruning Inventory

| # | Path | Type | Description | Decision |
|---|---|---|---|---|
| SA-01 | scripts/run_startup_radar_demo.py | script | CLI demo entry point | REPLACE_BEFORE_DELETE |
| SA-02 | src/api/routes.py | code | Demo routes | DELETE_AFTER_TEST_UPDATE |
| SA-03 | src/api/schemas.py | code | Demo schemas | DELETE_AFTER_TEST_UPDATE |
| SA-04 | src/api/service.py | code | Demo service | DELETE_AFTER_TEST_UPDATE |
| SA-05 | frontend/ (full dir) | frontend | Demo UI | REPLACE_BEFORE_DELETE |
| SA-06 | tests/integration/test_api_demo.py | test | 9 demo API tests | DELETE_AFTER_TEST_UPDATE |
| SA-07 | tests/integration/test_cli_demo.py | test | 6 CLI demo tests | DELETE_AFTER_TEST_UPDATE |
| SA-08 | tests/integration/test_demo_acceptance.py | test | 5 acceptance tests | DELETE_AFTER_TEST_UPDATE |
| SA-09 | tests/e2e/test_demo_ui.spec.ts | test | 2 Playwright smoke tests | DELETE_AFTER_TEST_UPDATE |
| SA-10 | .github/workflows/ci.yml | config | CI (no demo refs) | DO_NOT_TOUCH |
| SA-11 | frontend/playwright.config.ts | config | Playwright config for demo UI | REPLACE_BEFORE_DELETE |

## 7. Items Safe to Delete Now (DELETE_NOW)

1. data/demo_runs/latest/demo_run_report.json
2. data/demo_runs/latest/startup_action_brief.json
3. data/demo_runs/latest/startup_action_brief.md
4. data/nvidia_corpus/archive_test.md
5. data/nvidia_corpus/nim_test.md
6. data/nvidia_corpus/temp_test_source.md
7. data/regression_reports/latest_dashboard.json
8. data/regression_reports/latest_dashboard.md
9. data/regression_reports/answer_quality_eval_junit.xml
10. data/regression_reports/answer_quality_llm_judge_report.json
11. data/regression_reports/answer_quality_llm_judge_report.md
12. data/ingestion_reports/* (9 files)

**Total: 12+ items** -- zero code/test dependencies.

## 8. Items to Delete After Test/Doc Update (DELETE_AFTER_TEST_UPDATE)

**Prerequisite:** Confirm product routes have no demo dependency, write regression test, update README.

1. src/api/routes.py
2. src/api/schemas.py
3. src/api/service.py
4. tests/integration/test_api_demo.py
5. tests/integration/test_cli_demo.py
6. tests/integration/test_demo_acceptance.py
7. tests/e2e/test_demo_ui.spec.ts
8. Makefile targets: demo-cli, demo-cli-offline, demo-cli-rag, demo-acceptance, demo-full-check, demo-full, api-test

## 9. Items to Archive (ARCHIVE_HISTORY)

Add prominent "> **ARCHIVED:**" header to each file. Do not move or delete.

- docs/08_demo_script.md, docs/49-52 demo docs, docs/00_case_plan.md
- docs/05_rag_design.md, docs/26_architecture_utilization_audit.md
- examples/demo/README.md
- Historical plan files in docs/plans/ (all except PLAN_TEMPLATE.md and Epics 28-31)
- Obsidian 03 Research/ and 04 Decisions/ epic notes (add #archived tag)

## 10. Items to Keep as Fixture/Golden (KEEP_AS_FIXTURE_OR_GOLDEN)

- examples/demo/sample_startup_input.json (used by tests)
- examples/golden/ (7 cases + expected_outputs.json + README)
- examples/rag_eval/ (golden_queries.json, expected_contexts.json)
- examples/answer_quality/ (golden cases, llm_judge output)
- examples/validation/ (5 fixtures)

## 11. Items to Keep as Live Docs (KEEP_AS_LIVE_DOC)

- README.md, ROADMAP.md, EVALS.md, AGENTS.md, DECISIONS.md
- docs/10 through 17 (product rules)
- docs/27, 28, 35-48, 52, 53, 54, 55, 56
- docs/contracts/* (10 files)
- data/nvidia_corpus/sources.yaml, source_allowlist.yaml

## 12. Items That Need Replacement Before Deletion (REPLACE_BEFORE_DELETE)

1. scripts/run_startup_radar_demo.py -- no product CLI replacement yet
2. frontend/ -- no product UI yet (target of original Epic 31)
3. src/main.py -- check if any external tool depends on re-export path

## 13. Items Not to Touch (DO_NOT_TOUCH)

- All core src/ modules (pipeline, scoring, diagnosis, recommendation, briefing, rag, evaluation, config, database)
- data/product/product.db (runtime artifact)
- .github/workflows/ (no demo refs)
- migrations/ (Alembic)
- tests/unit/ and tests/evals/ (all active tests)
- pyproject.toml, docker-compose.yml, .pre-commit-config.yaml, .env.example

## 14. Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Deleting demo routes breaks CI | Low | High | All demo tests are integration-only (excluded from CI). Delete only after tests are removed. |
| Deleting sample_input breaks tests | High | High | DO NOT delete -- keep as fixture. |
| Archived docs re-enter agent context | Medium | Medium | Add prominent "ARCHIVED" headers. Update FPB-007. |
| Stale Obsidian limitations confuse agent | Medium | Medium | Correct Known Limitations.md. Archive epic notes. |
| Deleting demo service breaks product imports | Low | High | Verify no cross-import before deleting. |

## 15. Validation Plan

`ash
# After each DELETE_NOW step:
pytest -m "not integration" --tb=short
ruff check .
black --check .
mypy src

# After DELETE_AFTER_TEST_UPDATE steps:
pytest tests/integration/test_product_api.py -v  # product must work
python -c "from src.api.main import app; print('OK')"  # app must import
python scripts/check_scope.py
python scripts/check_docs_closure.py
alembic upgrade head

# Final validation:
make validate
`

## 16. Build Plan

1. **DELETE_NOW** -- remove generated artifacts, add to .gitignore, validate
2. **ARCHIVE_HISTORY** -- add archive headers to demo docs, historical plans, Obsidian notes
3. **UPDATE README** -- remove demo-first sections, consolidate product-first descriptions
4. **WRITE REGRESSION TEST** -- product routes never touch data/demo_runs
5. **DELETE_AFTER_TEST_UPDATE** -- remove demo routes, tests, Makefile targets
6. **MERGE_INTO_LIVE_DOC** -- consolidate early docs into live docs/contracts
7. **Obsidian sync** -- update Known Limitations, archive epic notes, create Epic 31 notes
8. **ROADMAP/EVALS update** -- reflect Epic 31 completion

## 17. Recommended Immediate Next Step

Start with **DELETE_NOW** items: remove committed generated artifacts (demo_runs/latest, regression_reports, ingestion_reports) and test corpus files (archive_test.md, nim_test.md, temp_test_source.md). Add them to .gitignore. This is the safest step with zero code/test impact.
