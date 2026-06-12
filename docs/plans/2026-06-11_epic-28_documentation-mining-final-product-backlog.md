# Plan: Epic 28 - Documentation Mining & Final Product Backlog Consolidation

## Objective

Mine the project's accumulated documentation, examples, scripts, API, frontend,
pipeline, RAG, evaluation, scoring, recommendation, tests, and local data
artifacts to consolidate a final product backlog. The product direction is now
"usable final product", not demo-first delivery.

## Context Read

- Root docs: `README.md`, `ROADMAP.md`, `EVALS.md`, `AGENTS.md`,
  `DECISIONS.md`, `pyproject.toml`, `.env.example`, `Makefile`,
  `docker-compose.yml`
- Required docs: `docs/`, `docs/contracts/`, `docs/plans/`
- Knowledge base: `obsidian-vault/`
- Product/demo surfaces: `examples/`, `scripts/`, `frontend/`, `src/api/`,
  `src/pipeline/`, `src/briefing/`, `src/rag/`, `src/evaluation/`,
  `src/scoring/`, `src/recommendation/`, `tests/`, selected `data/`
- `IMPLEMENTATION_CONTRACT.md` was checked and does not exist.

## Scope

- Create `docs/54_final_product_backlog.md`.
- Update `ROADMAP.md` with Epic 28 and the recommended next technical epic.
- Update `README.md` only for factual contradictions and a pointer to the final
  backlog.
- Update `EVALS.md` only to document the Epic 28 documentary validation gate.
- Add short Obsidian research/decision notes following the existing project
  pattern.

## Out of Scope

- No functional code changes.
- No deletions.
- No database, endpoint, UI, pipeline, RAG, scoring, recommendation, Qdrant
  ingestion, dependency, workflow, auth, export, CRM, review-loop, or new eval
  implementation.

## Proposed Implementation

1. Extract implemented capabilities, limitations, backlog hints, demo-like
   flows, historical docs, contracts, tests, reports, examples, and generated
   data artifacts.
2. Cross-check documentation against implementation by reading representative
   code, especially `src/pipeline/run_pipeline.py`, `src/api/`, frontend entry
   points, scripts, contracts, and tests.
3. Classify product items into exactly one category:
   `IMPLEMENTED_KEEP`, `IMPLEMENTED_NEEDS_HARDENING`, `PRODUCT_BACKLOG`,
   `REPLACE`, `DELETE`, `ARCHIVE`, or `CONTRACT_OR_TEST`.
4. Classify documentation into:
   `KEEP_AS_LIVE_DOC`, `MERGE_INTO_LIVE_DOC`, `CONVERT_TO_BACKLOG`,
   `CONVERT_TO_TEST_OR_CONTRACT`, `ARCHIVE_HISTORY`, or
   `DELETE_AFTER_CONSOLIDATION`.
5. Record contradictions, especially the README/Obsidian stale statement that
   Gap Diagnosis is not integrated even though the pipeline now integrates Gap
   Diagnosis and Recommendation.
6. Recommend the next technical epic from the P0/P1 items.

## Files to Create/Change

### Create

- `docs/54_final_product_backlog.md`
- `obsidian-vault/03 Research/Epic 28 Documentation Mining & Final Product Backlog.md`
- `obsidian-vault/04 Decisions/Epic 28 Final Product Backlog Source of Truth.md`

### Change

- `README.md`
- `ROADMAP.md`
- `EVALS.md`

## Tests/Validations

- Manual documentary validation:
  - required headings present
  - no empty critical sections
  - no unresolved TODO/TBD/FIXME/placeholders in the new backlog doc
  - categories, decisions, priorities, and documentation decisions use only
    allowed values
  - each backlog item has a traceable origin
  - P0/P1 items and next technical epic are explicit
- Run `python scripts/check_scope.py`.
- Run `make validate` if available and report any failures that are outside this
  documentation-only scope.

## Risks

- The repository already has uncommitted changes in docs/frontend/test areas; do
  not revert or overwrite unrelated user work.
- Some historical documentation is obsolete; mark it as archive or consolidation
  source rather than treating it as current truth.
- Demo assets have validation value in tests; do not mark them for deletion when
  they are fixtures or golden datasets.

## Definition of Done

- Final backlog exists at `docs/54_final_product_backlog.md`.
- P0/P1 backlog items and next technical epic are clear.
- Demo-like areas, delete/archive candidates, contradictions, and documentation
  pruning decisions are recorded.
- README/ROADMAP/EVALS/Obsidian are updated only within the allowed documentary
  scope.
- No functional implementation was changed.
