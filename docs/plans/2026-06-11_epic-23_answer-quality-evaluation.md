> **ARCHIVED:** Historical plan artifact. Preserved for reference only. Current product direction is in Epics 28-31 and docs/54_final_product_backlog.md.

# Plan: Epic 23 - LLM/RAG Answer Quality Evaluation

## Objective

Add an offline deterministic evaluation harness for final RAG/Action Brief answer
quality. The harness checks whether generated briefs preserve evidence, uncertainty,
RAG provenance, required sections, gaps, technologies, and `recommended_motion`.

## Scope

- Create answer quality schemas and evaluator under `src/evaluation/`.
- Add versioned golden answer quality cases under `examples/answer_quality/`.
- Add golden eval tests under `tests/evals/`.
- Extend the regression dashboard to surface answer quality metrics when its JUnit
  report exists.
- Document the feature in docs, README, ROADMAP, EVALS, and Obsidian.

## Out of Scope

- No LLM judge calls.
- No OpenAI, Cohere, or NVIDIA judge integration.
- No scoring, diagnosis, recommendation, retrieval, Qdrant, or `recommended_motion`
  changes.
- No scraping.
- No new dependencies.

## Implementation

1. Add Pydantic schemas for eval cases, metrics, unsupported claims, coverage
   checks, required section checks, gate results, and eval results.
2. Implement pure deterministic evaluator functions that consume a
   `StartupActionBrief` and a golden `AnswerQualityEvalCase`.
3. Compute required deterministic metrics:
   required sections, missing evidence preservation, uncertainty preservation,
   motion consistency, required evidence/gap/technology presence, unsupported
   claim count, RAG citation coverage, startup evidence citation coverage,
   forbidden absolute language count, and PASS/WARN/FAIL status.
4. Add quality gates that fail on missing critical contract items and warn on low
   citation coverage or excessive absolute language.
5. Add golden cases for high-fit, weak evidence, non-AI, good RAG context, no RAG
   context, low confidence, conflicting/irrelevant RAG context, and required missing
   evidence.
6. Extend the dashboard to read `answer_quality_eval_junit.xml` when present and
   expose answer quality summary metrics.

## Tests

- `pytest tests/evals/test_answer_quality_golden.py -q`
- `pytest`
- `ruff check .`
- `black --check .`
- `mypy src`

## Definition of Done

- Answer quality eval runs offline.
- Golden cases are versioned.
- Quality gates are deterministic.
- CI does not require LLM judge.
- Dashboard incorporates answer quality metrics when available.
- Docs and Obsidian are updated.
- No central product logic is changed.

