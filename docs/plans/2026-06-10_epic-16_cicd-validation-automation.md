> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Plan: Epic 16 — CI/CD, Validation Automation & Quality Gates

## Objective

Automate the manual quality process so that linting, type-checking, testing,
and documentation-consistency checks run automatically on every push/PR and
optionally on every commit.

## Context Read

- AGENTS.md, pyproject.toml, .gitignore, README.md, ROADMAP.md, DECISIONS.md, EVALS.md
- docs/contracts/end_of_epic_contract.md
- docs/plans/PLAN_TEMPLATE.md
- docker-compose.yml, .env.example
- prompts/review_diff.md

## Relevant Files

### Create
- .github/workflows/ci.yml
- .pre-commit-config.yaml
- Makefile
- scripts/validate.sh
- scripts/check_scope.py
- scripts/check_docs_closure.py
- tests/unit/test_check_scope.py
- tests/unit/test_check_docs_closure.py
- docs/40_ci_cd_quality_gates.md

### Change
- AGENTS.md — add validation rules (pre-commit, CI, scope check, docs closure)
- README.md — CI badge, commands, Known Limitations
- ROADMAP.md — mark Epic 16 done
- EVALS.md — add CI/CD Quality Gates, new test rows
- DECISIONS.md — Decision 024

## Scope

- .github/workflows/ci.yml
- .pre-commit-config.yaml
- Makefile
- scripts/validate.sh
- scripts/check_scope.py
- scripts/check_docs_closure.py
- tests/unit/test_check_scope.py
- tests/unit/test_check_docs_closure.py
- docs/40_ci_cd_quality_gates.md
- AGENTS.md, README.md, ROADMAP.md, EVALS.md, DECISIONS.md
- docs/plans/ — this plan
- obsidian-vault/ — backfill

## Out of Scope

- No scraping or crawler
- No scheduler
- No product logic changes (src/ untouched)
- No scoring, diagnosis, recommendation, RAG, or Qdrant changes
- No deploy or authentication
- No new dependencies without justification

## Proposed Implementation

1. Create .github/workflows/ci.yml — GitHub Actions CI
2. Create .pre-commit-config.yaml — pre-commit hooks
3. Create Makefile — convenience targets
4. Create scripts/validate.sh — local validation runner
5. Create scripts/check_scope.py — sensitive-area change detection
6. Create scripts/check_docs_closure.py — epic closure verification
7. Create tests/unit/test_check_scope.py — 7 tests
8. Create tests/unit/test_check_docs_closure.py — 6 tests
9. Create docs/40_ci_cd_quality_gates.md — design doc
10. Update AGENTS.md — validation rules, updated commands
11. Update README.md — CI badge, commands, Known Limitations
12. Update ROADMAP.md — mark completed
13. Update EVALS.md — CI/CD Quality Gates, new test files
14. Update DECISIONS.md — Decision 024
15. Obsidian backfill — decision note, research note, Known Limitations
16. Run validations: pytest, ruff, black, mypy

## Tests/Validations

- pytest — all 328 tests must pass
- ruff check .
- black --check .
- mypy src
- make validate (tests all targets)

## Risks

| Risk | Mitigation |
|------|-----------|
| CI fails because integration tests need Qdrant | CI uses `-m "not integration"` |
| Pre-commit hooks slow down commits | Only lint/format on staged files |
| Makefile doesn't work on Windows | PowerShell scripts also available; make via choco/git-bash |
| check_scope.py breaks during rebase | Documented limitation; only fails safe |

## Definition of Done

- [x] CI workflow created
- [x] Makefile created
- [x] validate.sh created
- [x] pre-commit config created
- [x] check_scope.py and check_docs_closure.py created
- [x] Tests for both scripts pass
- [x] docs/evals/roadmap/Obsidian updated
- [x] Local validation documented
- [x] `pytest` passes
- [x] `ruff check .` passes
- [x] `black --check .` passes
- [x] `mypy src` passes

---

*Gerado em: 2026-06-10*
*Modo: Plan → Artifact → Build → Review → Commit*

