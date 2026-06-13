# Optional Answer Quality LLM Judge Report

This report is experimental, informational, and not a CI gate.

- Generated at: `2026-06-13T19:24:26.054416+00:00`
- Provider: `null`
- Model: `null-offline-deterministic`
- CI gate: `false`
- Total cases: `1`
- Completed cases: `1`
- Error cases: `0`

## Summary

| Metric | Value |
|---|---:|
| completed_cases | 1 |
| mean_faithfulness_score | 0.85 |
| mean_answer_relevancy_score | 0.82 |
| mean_groundedness_score | 0.84 |
| mean_completeness_score | 0.8 |
| mean_uncertainty_honesty_score | 0.88 |
| mean_executive_usefulness_score | 0.81 |
| mean_judge_confidence | 1.0 |
| mean_score | 0.8333 |
| status | INFO |

## Cases

### high_fit_supported_answer

- Status: `COMPLETED`
- Mean confidence: `1.0`
- Flags: `null_provider, offline, not_semantic`
- Rationale: NullLLMJudgeProvider produced deterministic offline scores for plumbing and report validation only; no semantic model was called.
