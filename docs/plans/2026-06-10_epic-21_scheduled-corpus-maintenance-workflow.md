> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Plan: Epic 21 Scheduled Corpus Maintenance Workflow

## Objective

Create a controlled corpus maintenance workflow that runs source sync dry-run,
freshness audit, Qdrant ingest dry-run, optional real Qdrant ingestion, RAG evals,
golden evals, and report artifact generation without enabling automatic real
ingestion or source promotion by default.

## Context Read

- `AGENTS.md`
- `README.md`
- `ROADMAP.md`
- `EVALS.md`
- `.github/workflows/`
- `Makefile`
- `.env.example`
- `docker-compose.yml`
- `scripts/sync_nvidia_sources.py`
- `scripts/audit_nvidia_corpus_freshness.py`
- `scripts/ingest_nvidia_corpus.py`
- `docs/42_automated_qdrant_corpus_ingestion.md`
- `docs/43_automated_nvidia_source_sync.md`
- `docs/44_corpus_freshness_versioning_policy.md`
- `docs/contracts/rag_contract.md`
- `tests/evals/`
- `examples/rag_eval/`
- `examples/golden/`
- `obsidian-vault/`

## Relevant Files

- `.github/workflows/corpus-maintenance.yml`
- `scripts/run_corpus_maintenance.py`
- `docs/45_scheduled_corpus_maintenance.md`
- `Makefile`
- `README.md`
- `EVALS.md`
- `ROADMAP.md`
- `DECISIONS.md`
- `obsidian-vault/`

## Scope

- Add a manual GitHub Actions workflow with safe defaults.
- Add an optional schedule that runs only safe dry-run/audit/eval steps.
- Add a local script that executes the same maintenance sequence.
- Add Makefile targets for safe dry-run, evals, and explicit ingestion.
- Document operation, reports, safety controls, and limitations.

## Out of Scope

- No broad scraping or crawler.
- No retrieval, embeddings, scoring, diagnosis, recommendation, briefing, or
  `recommended_motion` changes.
- No auto-commit or external report publishing.
- No cloud Qdrant usage.

## Proposed Implementation

1. Create `scripts/run_corpus_maintenance.py` with typed argparse flags, safe
   defaults, sequential subprocess execution, report directory creation, per-step
   logs, JUnit eval output, and `maintenance_summary.json`.
2. Create `.github/workflows/corpus-maintenance.yml` with `workflow_dispatch`,
   optional schedule, dependency install, conditional local Qdrant startup, script
   execution, cleanup, and artifact upload.
3. Update `Makefile` with `corpus-maintenance-dry-run`,
   `corpus-maintenance-evals`, and `corpus-maintenance-ingest`.
4. Create `docs/45_scheduled_corpus_maintenance.md` and update README, EVALS,
   ROADMAP, DECISIONS, and Obsidian notes.

## Files to Create/Change

### Create
- `.github/workflows/corpus-maintenance.yml` - manual/scheduled workflow.
- `scripts/run_corpus_maintenance.py` - local and CI orchestrator.
- `docs/45_scheduled_corpus_maintenance.md` - operator documentation.
- Obsidian Epic 21 research and decision notes.

### Change
- `Makefile` - maintenance targets.
- `README.md` - capabilities, commands, limitations.
- `EVALS.md` - maintenance eval/reporting notes.
- `ROADMAP.md` - Epic 21 status.
- `DECISIONS.md` - workflow safety decision.
- Obsidian known limitations - updated scheduling limitation.

## Tests/Validations

- `git status`
- `git diff --stat`
- `pytest`
- `ruff check .`
- `black --check .`
- `mypy src`
- Local script validation in safe mode.

## Risks

| Risk | Mitigation |
|------|------------|
| Real ingestion mutates Qdrant unintentionally | Default `run_ingestion=false`; workflow only starts Qdrant for explicit real ingestion. |
| Scheduled run promotes sources | Schedule passes `promote_sources=false`; workflow never commits changes. |
| Expired corpus passes silently | Default `fail_on_expired=true`. |
| New script lacks direct unit tests | Scope excludes tests; script is validated by local safe execution and full quality gates. |

## Definition of Done

- [ ] Workflow manual exists with safe defaults.
- [ ] Schedule is safe by default.
- [ ] Real ingestion requires explicit input.
- [ ] Reports upload as artifacts.
- [ ] Local script exists.
- [ ] Makefile targets exist.
- [ ] Docs and Obsidian updated.
- [ ] Requested checks pass or failures are reported.

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
- [ ] `docs/` documentacao relevante atualizada ou criada.
- [ ] `obsidian-vault/` backfill realizado (decisao, resumo, limitacoes).
- [ ] Nenhuma dependencia nova foi adicionada sem justificativa.
- [ ] Nenhuma feature fantasma foi documentada.

---

*Gerado em: 2026-06-10*
*Modo: Plan -> Artifact -> Build -> Review -> Commit*

