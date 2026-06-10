# Development Workspace Quality System

## Purpose

Define the **development workflow, quality gates, and artifact rules** that the AI agent follows when working on the NVIDIA Startup AI Radar. This system ensures auditable, consistent, and scope-controlled development.

---

## Workflow: Plan → Artifact → Build → Review Diff → Validation → Closure → Commit

```
User Task
   │
   ▼
┌─────────────────────────────────────────────────────────────┐
│ PLAN MODE                                                   │
│ • Read AGENTS.md, relevant contracts, related plans         │
│ • Read ROADMAP, DECISIONS, EVALS for current state          │
│ • Write plan (or plan artifact if non-trivial)              │
│ • Present to user for approval                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ approved
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ BUILD MODE                                                  │
│ • Verify plan artifact exists (except hotfix)               │
│ • Read relevant contracts before touching modules           │
│ • Implement smallest useful increment                       │
│ • Follow scope from approved plan                           │
└─────────────────────────┬───────────────────────────────────┘
                          │ done
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ REVIEW DIFF                                                 │
│ • Run git diff (staged + unstaged)                          │
│ • Check scope adherence                                     │
│ • Check contract compliance                                 │
│ • Check doc updates                                         │
│ • Check validation results                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │ pass
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ VALIDATION                                                  │
│ • pytest                                                    │
│ • ruff check .                                              │
│ • black --check .                                           │
│ • mypy src                                                  │
└─────────────────────────┬───────────────────────────────────┘
                          │ pass
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ CLOSURE                                                    │
│ • Update README if capabilities/limitations changed         │
│ • Update ROADMAP                                            │
│ • Update DECISIONS or create ADR                            │
│ • Update EVALS                                              │
│ • Update ERROR_LOG if errors occurred                       │
│ • Update Known Limitations (Obsidian)                       │
│ • Backfill Obsidian (decision note + epic summary)          │
│ • Run end-of-epic closure checklist if applicable           │
└─────────────────────────┬───────────────────────────────────┘
                          │ ready
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ COMMIT                                                      │
│ • Review diff                                               │
│ • Create meaningful commit message                          │
│ • No --no-verify unless explicitly authorized               │
└─────────────────────────────────────────────────────────────┘
```

---

## Roles of Each Artifact

| Artifact | Role in Workflow |
|----------|------------------|
| `AGENTS.md` | Entry point: project context, rules, workflow, closure checklist |
| `docs/plans/` | Versioned plan artifacts; what was planned, scoped, approved |
| `prompts/` | Versioned system prompts; ensures consistent agent behavior |
| `docs/adr/` | Architectural Decision Records; structured, linkable decisions |
| `docs/contracts/` | Development contracts; what each module promises (not implementation) |
| `ERROR_LOG.md` | Error registry; what broke, why, how fixed, how prevented |
| `EVALS.md` | Test baseline + quality criteria |
| `obsidian-vault/` | Research lab; decisions, epic summaries, workspace control notes |

---

## Diff Quality Checklist

Before every commit, run `prompts/review_diff.md` and verify:

- [ ] **Scope:** No changes outside the approved plan scope
- [ ] **Product code:** No changes to `src/` when epic is workspace-only
- [ ] **Dependencies:** No new dependencies without justification
- [ ] **Contracts:** Schema/interface changes respect existing contracts in `docs/contracts/`
- [ ] **Documentation:** README, ROADMAP, DECISIONS, EVALS updated if applicable
- [ ] **Obsidian:** Decision note created, epic summary updated, Known Limitations reviewed
- [ ] **Tests:** New code has tests or explicit justification why not
- [ ] **Error log:** Relevant errors recorded in `ERROR_LOG.md`
- [ ] **Hallucination:** No invented sources, technologies, or features
- [ ] **Ghost features:** No documented feature that was not implemented

---

## End-of-Epic Closure Checklist

(Defined in `AGENTS.md` — repeated here for visibility.)

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

## Anti-Scope Rules

1. **No task starts without a scope boundary.** If the user's request is vague, clarify scope before building.
2. **Out-of-scope changes are rejected during Review Diff.** If found, revert and explain why.
3. **"While I'm here" is not a justification.** Prefer a new plan over scope creep.
4. **Product epic ≠ workspace epic.** Never mix `src/` changes with `docs/` or `prompts/` changes in the same epic.
5. **Contract updates are workspace.** Schema changes are product. Contract documents describe; schemas define.

## Anti-Hallucination Rules

1. **No invented sources.** Every claim about a startup or technology must trace to a real file or real evidence.
2. **No invented features.** If a feature is documented but not implemented, mark it as `[planned]` or `[stub]`.
3. **No false status.** Never mark an epic as "done" if any closure checklist item fails.
4. **No ghost contracts.** If you reference a contract in reasoning, that contract must exist in `docs/contracts/`.
5. **When uncertain, say so.** "I don't know" or "not verified" is preferred over a wrong answer.

---

*Document: docs/28_development_workspace_quality.md*  
*Part of: Epic 7.2 — Development Workspace Quality System*
