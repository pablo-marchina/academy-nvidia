# Epic 23.2 Optional LLM Judge Adapter

## Summary

Implemented an optional, experimental answer quality judge interface for semantic
review of RAG/Action Brief outputs.

## Delivered

- Pydantic schemas for judge input, scores, result, run report, and provider config.
- `BaseLLMJudgeProvider` and deterministic offline `NullLLMJudgeProvider`.
- Prompt rubrics for faithfulness, answer relevancy, groundedness, completeness,
  uncertainty honesty, and executive usefulness.
- Manual script that writes JSON and Markdown reports under `data/regression_reports/`.
- Regression dashboard informational section for Optional LLM Judge.

## Boundaries

- No real provider.
- No external API calls.
- No API key requirement.
- Not a CI gate.
- Does not change deterministic Answer Quality JUnit, scoring, diagnosis,
  recommendation, retrieval, or Action Brief logic.
