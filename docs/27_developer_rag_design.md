# Developer RAG Design

## Objective

The Developer RAG provides the AI agent (opencode) with **retrievable context about the development workspace itself** — rules, plans, decisions, contracts, prompts, and known limitations. It is a **memory system for the developer**, not a feature for the end user.

## Difference: Developer RAG vs Product RAG

| Aspect | Developer RAG | Product RAG |
|--------|--------------|-------------|
| **Purpose** | Help the AI agent follow workspace rules and recall past context | Help the product recommend NVIDIA technologies to startups |
| **Audience** | AI agent (and human developer) | End user (NVIDIA team) |
| **Sources** | AGENTS.md, plans, ADRs, contracts, prompts, Obsidian | NVIDIA playbooks, documentation, technical specs |
| **Indexed data** | Development artifacts | NVIDIA technology knowledge |
| **Status** | Foundation designed, not yet implemented (no vector DB) | Future epic — not yet started |
| **Search method** | Future: embeddings + cosine similarity | Future: hybrid retrieval |

## Indexable Sources

When implemented, Developer RAG should index:

1. `AGENTS.md` — workspace rules, priorities, closure checklist
2. `README.md` — project overview, current capabilities, known limitations
3. `ROADMAP.md` — epic status
4. `DECISIONS.md` — architectural decisions
5. `EVALS.md` — test baseline and quality criteria
6. `ERROR_LOG.md` — error history
7. `docs/plans/*.md` — all plan artifacts
8. `docs/adr/*.md` — all ADRs
9. `docs/contracts/*.md` — development contracts
10. `prompts/*.md` — all versioned prompts
11. `obsidian-vault/02 Project Control/*.md` — workspace notes
12. `obsidian-vault/03 Research/*.md` — epic summaries
13. `obsidian-vault/04 Decisions/*.md` — decision notes

## Forbidden Sources

- Source code (`src/`) — agent reads code directly, no RAG needed
- Test files (`tests/`) — agent reads tests directly
- Generated artifacts (`.pyc`, `__pycache__`, `.venv`, `.pytest_cache`)
- Obsidian templates — only populated notes
- Archived prompts (`prompts/archived/`)

## Avoiding RAG Pollution

1. **No raw Obsidian inbox** — only promoted notes (02–04 folders)
2. **No duplicate content** — ADR in `docs/adr/` OR `DECISIONS.md`, not both
3. **Plans are immutable after approval** — append errata instead of editing
4. **Contracts versioned by directory** — old contracts archived to `docs/contracts/archive/`
5. **Prompts are curated** — only active prompts in `prompts/` (archived go to `prompts/archived/`)

## Handling Obsolete Documents

- Move to `docs/plans/archive/`, `docs/adr/archive/`, or `prompts/archived/`
- Add a note at the top: `> OBSOLETE: superseded by {new-document}`
- Update the index in Obsidian `Plan Artifacts` or `Prompt Library`

## Using `docs/plans/`

Plan artifacts are the **primary input** for Developer RAG context. When starting a new task:

1. Search `docs/plans/` for related plans (by epic number, module name, or date)
2. Read the most recent plan to understand current state
3. Check the Definition of Done to see what remains
4. Start a new plan only if no existing plan covers the task

## Using Obsidian

Obsidian vault is the **lab** — research, draft decisions, and ephemeral context live here.

- `02 Project Control/` — workspace operational notes (indexes, quality system)
- `03 Research/` — epic summaries (one per completed epic)
- `04 Decisions/` — decision notes (one per decision)
- `07 Evidence/` — raw evidence collected during research

The vault is **not indexed by default** — only `02 Project Control/`, `03 Research/`, and `04 Decisions/` should be in the RAG index.

## Future Retrieval Quality Evaluation

When a vector DB is implemented, evaluate with:

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Recall@5 | ≥90% | For each query, top 5 results contain the relevant doc |
| Precision@5 | ≥70% | At least 3 of 5 results are relevant |
| Faithfulness | No hallucinated doc references | Manual review of agent output |
| Retrieval latency | <500ms | Measured per query |

## Decision

**Do not implement a vector DB in this epic.** The Developer RAG is a **documental foundation only** — sources are identified, categorized, and structured. Implementation (chunking, embeddings, retrieval) is deferred until:
- The number of documents exceeds ~50 files, OR
- The agent consistently fails to find relevant workspace context, OR
- A future epic explicitly requires it.

---

*Document: docs/27_developer_rag_design.md*  
*Part of: Epic 7.2 — Development Workspace Quality System*
