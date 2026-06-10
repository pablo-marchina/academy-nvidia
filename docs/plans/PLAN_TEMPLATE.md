# Plan: {Epic Title}

## Objective

{One paragraph: what this epic delivers and why.}

## Context Read

{List of files/directories read before planning.}

## Relevant Files

{Which files are in scope — existing and new. Include schemas, contracts, tests.}

## Scope

- {what is included, one per bullet}
- {be precise: module names, folders, file patterns}

## Out of Scope

- {what is explicitly excluded, one per bullet}
- {this prevents scope creep during Build Mode}

## Proposed Implementation

{Steps in order. Each step should be a small, testable increment.}

1. Step one — {file: what changes}
2. Step two — {file: what changes}
3. ...

## Files to Create/Change

### Create
- `path/to/file.ext` — reason

### Change
- `path/to/file.ext` — what changes

## Tests/Validations

- {list of test commands: pytest, ruff, black, mypy}
- {list of specific test functions or scenarios}
- {manual validation steps, if any}

## Risks

| Risk | Mitigation |
|------|-----------|
| {risk} | {mitigation} |

## Definition of Done

- [ ] {condition 1}
- [ ] {condition 2}
- [ ] ...

## End-of-Epic Closure Checklist

- [ ] `pytest` passa sem erros.
- [ ] `ruff check .` passa sem erros.
- [ ] `black --check .` passa sem erros.
- [ ] `mypy src` passa sem erros.
- [ ] `README.md` atualizado com Current Capabilities e Known Limitations.
- [ ] `ROADMAP.md` atualizado com status real do épico.
- [ ] `DECISIONS.md` atualizado com decisoes arquiteturais do épico.
- [ ] `EVALS.md` atualizado com baseline de testes e cobertura.
- [ ] `ERROR_LOG.md` revisado e atualizado se houve erros.
- [ ] `docs/` — documentacao relevante atualizada ou criada.
- [ ] `obsidian-vault/` — backfill realizado (decisao, resumo, limitações).
- [ ] Nenhuma dependencia nova foi adicionada sem justificativa.
- [ ] Nenhuma feature fantasma foi documentada.

---

*Gerado em: {date}*  
*Modo: Plan → Artifact → Build → Review → Commit*
