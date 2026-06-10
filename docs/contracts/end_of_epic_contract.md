# End-of-Epic Closure Contract

## Purpose

Define what "done" means for an epic. Before marking any epic as completed, ALL items below must be verified.

## Mandatory Checks

### Validation
- [ ] `pytest` passes with no errors
- [ ] `ruff check .` passes with no errors (pre-existing warnings allowed)
- [ ] `black --check .` passes
- [ ] `mypy src` passes (pre-existing errors allowed)

### Documentation
- [ ] `README.md` updated:
  - Current Capabilities reflect what the epic delivered
  - Known Limitations updated with any new limitations introduced
- [ ] `ROADMAP.md` updated:
  - Epic moved from "Em andamento" to "Concluídos"
  - Status reflects real delivery (not aspirational)
- [ ] `DECISIONS.md` updated:
  - New architectural decisions from this epic registered
- [ ] `EVALS.md` updated:
  - Test count reflects actual total
  - New test files added to table
- [ ] `ERROR_LOG.md` reviewed:
  - If errors occurred: documented with cause, fix, and prevention
  - If no errors: note "No errors in this epic"

### Workspace
- [ ] `docs/` — relevant documentation created or updated for the epic
- [ ] `obsidian-vault/` — backfill performed:
  - Decision note in `04 Decisions/` (one per new decision)
  - Epic summary note in `03 Research/`
  - `Known Limitations.md` reviewed and updated
- [ ] No new dependencies added without justification
- [ ] No phantom features documented (feature was implemented or not documented)

## Special Cases

- **Workspace-only epic** (no `src/` changes): skip `mypy src` if it only checks `src/`, but document that `src/` was not changed.
- **Pure documentation epic**: skip validation commands that test code. Document why.
- **Epic with code + docs**: ALL checks apply. No exceptions.

## If Any Check Fails

The epic is NOT done. Fix before proceeding.

---

*Contract: end_of_epic_contract.md*  
*Part of: Epic 7.2 — Development Workspace Quality System*
