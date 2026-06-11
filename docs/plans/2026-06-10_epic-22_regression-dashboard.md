# Plan: Epic 22 - RAG / Action Brief Regression Dashboard

## Objective

Create a local Markdown/JSON regression dashboard that consolidates corpus maintenance
reports across ingestion, freshness, RAG evals, golden evals, and Action Brief checks.
The dashboard must also be rendered in the GitHub Actions Job Summary and uploaded as
an artifact.

## Context Read

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `EVALS.md`
- `.github/workflows/corpus-maintenance.yml`
- `scripts/run_corpus_maintenance.py`
- `scripts/ingest_nvidia_corpus.py`
- `scripts/audit_nvidia_corpus_freshness.py`
- `scripts/sync_nvidia_sources.py`
- `data/ingestion_reports/`
- `data/nvidia_corpus/sync_reports/`
- `examples/rag_eval/`
- `examples/golden/`
- `tests/evals/`
- `docs/45_scheduled_corpus_maintenance.md`
- `docs/contracts/rag_contract.md`
- `docs/contracts/briefing_contract.md`
- `obsidian-vault/`

## Relevant Files

- `scripts/build_regression_dashboard.py`
- `tests/unit/test_regression_dashboard.py`
- `data/regression_reports/`
- `docs/46_regression_dashboard.md`
- `.github/workflows/corpus-maintenance.yml`
- `Makefile`
- `README.md`
- `EVALS.md`
- `ROADMAP.md`
- `obsidian-vault/`

## Scope

- Read existing reports when available.
- Generate `data/regression_reports/latest_dashboard.md`.
- Generate `data/regression_reports/latest_dashboard.json`.
- Consolidate ingestion, freshness, RAG evals, golden evals, and Action Brief checks.
- Implement PASS/WARN/FAIL status rules.
- Add `make regression-dashboard`.
- Add GitHub Actions Job Summary and artifact integration.
- Add unit tests for clean, warning, failure, missing-report, Markdown, and JSON cases.

## Out of Scope

- No frontend or web app.
- No external publication.
- No changes to scoring, diagnosis, recommendation, retrieval, Qdrant ingestion, or
  Action Brief logic.
- No new dependencies.

## Proposed Implementation

1. Add `scripts/build_regression_dashboard.py` with a small dataclass-based report
   model, JSON/JUnit/Markdown readers, PASS/WARN/FAIL evaluator, and Markdown/JSON
   writers.
2. Add `tests/unit/test_regression_dashboard.py` using temporary report directories.
3. Add `data/regression_reports/.gitkeep` so the output directory exists.
4. Update `.github/workflows/corpus-maintenance.yml` to run the dashboard under
   `if: always()`, write Markdown to `$GITHUB_STEP_SUMMARY`, upload dashboard files,
   and fail only when dashboard status is `FAIL`.
5. Update `Makefile` with `regression-dashboard`.
6. Document usage and closure notes in README, EVALS, ROADMAP, docs, and Obsidian.

## Files to Create/Change

### Create

- `scripts/build_regression_dashboard.py` - dashboard builder.
- `tests/unit/test_regression_dashboard.py` - unit tests.
- `docs/46_regression_dashboard.md` - feature documentation.
- `data/regression_reports/.gitkeep` - output directory placeholder.

### Change

- `.github/workflows/corpus-maintenance.yml` - Job Summary/artifact/status integration.
- `Makefile` - local target.
- `README.md` - local/GitHub usage and limitations.
- `EVALS.md` - dashboard test baseline.
- `ROADMAP.md` - Epic 22 status.
- `obsidian-vault/` - research, decision, and limitations notes.

## Tests/Validations

- `pytest tests/unit/test_regression_dashboard.py -q`
- `pytest`
- `ruff check .`
- `black --check .`
- `mypy src`
- `make regression-dashboard`

## Risks

| Risk | Mitigation |
|------|------------|
| JUnit has limited RAG metrics | Use pass/fail and failed-case extraction only; do not invent quality metrics. |
| Action Brief checks are embedded in golden evals | Derive required-section pass/fail from golden eval status and test names when present. |
| Reports may be partial after failed runs | Treat missing/malformed reports as controlled warnings and still emit dashboard files. |
| WARN should not break GitHub Actions | Add a final explicit FAIL-only status gate. |

## Definition of Done

- [ ] Dashboard Markdown and JSON are generated locally.
- [ ] Dashboard consolidates ingestion, freshness, RAG evals, golden evals, and Action Brief checks.
- [ ] GitHub Actions writes dashboard Markdown to Job Summary.
- [ ] Dashboard files are uploaded as artifacts.
- [ ] FAIL fails the workflow and WARN does not.
- [ ] Unit tests pass.
- [ ] README, EVALS, ROADMAP, docs, and Obsidian are updated.
- [ ] No new dependencies are added.

## End-of-Epic Closure Checklist

- [ ] `pytest` passa sem erros.
- [ ] `ruff check .` passa sem erros.
- [ ] `black --check .` passa sem erros.
- [ ] `mypy src` passa sem erros.
- [ ] `README.md` atualizado com Current Capabilities e Known Limitations.
- [ ] `ROADMAP.md` atualizado com status real do epico.
- [ ] `DECISIONS.md` atualizado se houver decisao arquitetural nova.
- [ ] `EVALS.md` atualizado com baseline de testes e cobertura.
- [ ] `ERROR_LOG.md` revisado e atualizado se houve erros relevantes.
- [ ] `docs/` - documentacao relevante atualizada ou criada.
- [ ] `obsidian-vault/` - backfill realizado.
- [ ] Nenhuma dependencia nova foi adicionada.
- [ ] Nenhuma feature fantasma foi documentada.

---

*Gerado em: 2026-06-10*
*Modo: Plan -> Artifact -> Build -> Review -> Commit*
