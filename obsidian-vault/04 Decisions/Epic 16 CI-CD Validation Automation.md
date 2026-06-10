---
type: decision
epic: 16
date: 2026-06-10
status: implemented
---

# Decision: CI/CD, Validation Automation & Quality Gates

**Context:** The project had a rigorous manual quality process documented in
AGENTS.md, contracts, and prompts, but zero automation of linting,
type-checking, testing, or documentation consistency.

**Decision:** Add GitHub Actions CI, pre-commit hooks, Makefile, validate.sh,
check_scope.py, and check_docs_closure.py.

**Rationale:** GitHub Actions is the natural CI platform for a GitHub-hosted
project. Pre-commit hooks catch issues before CI. Makefile/validate.sh provide
single-command local validation. check_scope.py enforces contract discipline.
check_docs_closure.py formalizes epic closure.

**Key files:**
- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`
- `Makefile`
- `scripts/validate.sh`
- `scripts/check_scope.py`
- `scripts/check_docs_closure.py`
- `docs/40_ci_cd_quality_gates.md`

**See also:** DECISIONS.md Decision 024
