# CI/CD Quality Gates — Design & Operation

## Objective

Automate the manual quality process defined in `AGENTS.md` so that
linting, type-checking, testing, and documentation-consistency checks
run automatically on every push/PR and optionally on every commit.

## Components

```mermaid
flowchart LR
    A[Developer pushes code] --> B[GitHub Actions CI]
    B --> C[ruff check .]
    B --> D[black --check .]
    B --> E[mypy src]
    B --> F[pytest -m \"not integration\"]
    C --> G{All pass?}
    D --> G
    E --> G
    F --> G
    G -->|Yes| H[CI green]
    G -->|No| I[CI red - fix]
```

### 1. GitHub Actions CI (`.github/workflows/ci.yml`)

Trigger: push or pull_request to `main`.

Steps:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies (`pip install -e ".[dev]"`)
4. `ruff check .`
5. `black --check .`
6. `mypy src`
7. `pytest -m "not integration"` (unit tests only; integration tests require a running Qdrant server)

### 2. Pre-commit Hooks (`.pre-commit-config.yaml`)

Install with: `pre-commit install`

| Hook | Purpose |
|------|---------|
| `trailing-whitespace` | Remove trailing whitespace from all files |
| `end-of-file-fixer` | Ensure files end with a single newline |
| `check-yaml` | Validate YAML syntax |
| `check-toml` | Validate TOML syntax |
| `check-json` | Validate JSON syntax |
| `check-added-large-files` | Warn on files >500KB |
| `ruff` | Lint staged Python files |
| `black` | Format staged Python files |

### 3. Local Validation (`Makefile` and `scripts/validate.sh`)

| Target | Command |
|--------|---------|
| `make test` | `pytest -m "not integration"` |
| `make lint` | `ruff check .` |
| `make format-check` | `black --check .` |
| `make typecheck` | `mypy src` |
| `make validate` | All four above in sequence |
| `make rag-eval` | RAG evaluation tests |
| `make ci` | Alias for `validate` |

### 4. Scope Check (`scripts/check_scope.py`)

Detects changes in sensitive areas (`src/`, `tests/`, `docs/contracts/`,
`docs/plans/`, `pyproject.toml`, `AGENTS.md`, `README.md`, `EVALS.md`,
`ROADMAP.md`) and **requires** corresponding contract/doc updates.

Usage:
```bash
python scripts/check_scope.py
python scripts/check_scope.py --override docs/contracts/rag_contract.md
```

Exit code 0 = all checks pass; 1 = violations found.

### 5. Docs Closure Check (`scripts/check_docs_closure.py`)

Verifies that before closing an epic the following are updated:

- Plan file in `docs/plans/`
- `ROADMAP.md` (epic listed in Concluídos)
- `EVALS.md` (CI/CD Quality Gates section updated)
- Obsidian vault (decision + research notes)
- Known Limitations

Usage:
```bash
python scripts/check_docs_closure.py
python scripts/check_docs_closure.py --plan docs/plans/2026-06-10_epic-16_plan.md
```

## Test Coverage

| File | Tests | What it covers |
|------|-------|----------------|
| `tests/unit/test_check_scope.py` | 7 | Script exists, runnable, no changes, sensitive changes require docs, override flag, contract required for src/rag, contract override |
| `tests/unit/test_check_docs_closure.py` | 6 | Script exists, runnable, explicit plan OK, missing plan fails, missing ROADMAP fails, missing EVALS fails |

## Quality Gates

| Gate | Enforced by | Scope |
|------|------------|-------|
| Ruff passes | CI, pre-commit, Makefile | All Python files |
| Black passes | CI, pre-commit, Makefile | All Python files |
| Mypy passes | CI, Makefile | `src/` |
| Tests pass | CI, Makefile | All tests (except integration) |
| Contracts updated | `check_scope.py` (manual) | Changes to `src/` |
| Docs closure | `check_docs_closure.py` (manual) | Before epic close |

## Known Limitations

- Pre-commit hooks are not automatically installed — developer must run
  `pre-commit install` once per clone.
- CI only tests on Ubuntu — no Windows/macOS matrix.
- Integration tests are excluded from CI (require `QDRANT_TEST_URL`).
- `check_scope.py` requires `git` in PATH.
- `check_scope.py` checks git diff against HEAD — not robust for all
  workflows (e.g., rebase).
