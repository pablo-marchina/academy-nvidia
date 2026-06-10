---
type: research
epic: 16
date: 2026-06-10
status: completed
---

# Epic 16 — CI/CD, Validation Automation & Quality Gates

## What was delivered

- **GitHub Actions CI** — runs ruff, black, mypy, pytest on push/PR to main
- **Pre-commit hooks** — trailing-whitespace, end-of-file-fixer, YAML/TOML/JSON
  validation, check-added-large-files, ruff, black
- **Makefile** — test, lint, format-check, typecheck, validate, rag-eval, ci
- **scripts/validate.sh** — local validation runner
- **scripts/check_scope.py** — detects sensitive area changes, requires
  contract/doc updates (overridable)
- **scripts/check_docs_closure.py** — verifies plan, ROADMAP, EVALS, Obsidian,
  Known Limitations before epic close
- 13 new tests (7 check_scope, 6 check_docs_closure)
- Updated AGENTS.md, README.md, ROADMAP.md, EVALS.md, DECISIONS.md

## Test impact

- Total: 328 tests (319 unit + 9 skippable integration)
- 34 test files
- No product code (src/) was changed

## Key metrics

- `make validate` passes with 0 errors
- CI workflow passes on all validations
- All 315 pre-existing tests pass unchanged
- check_scope.py detects violations in 100% of test scenarios
