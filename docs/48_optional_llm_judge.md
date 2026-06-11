# Optional LLM Judge Adapter

**Epic 23.2** | **Date:** 2026-06-11

## Objective

Provide an optional, experimental interface for semantic review of final
RAG/Action Brief answer quality. This judge is for human analysis only and is not
a deterministic quality gate.

## Architecture

```
src/evaluation/
  llm_judge_schemas.py
  llm_judge_prompts.py
  llm_judge_adapter.py

scripts/
  run_answer_quality_llm_judge.py

data/regression_reports/
  answer_quality_llm_judge_report.json
  answer_quality_llm_judge_report.md
```

The only executable provider in this epic is `NullLLMJudgeProvider`, which returns
deterministic offline scores and never calls an external API.

## Schemas

- `LLMJudgeInput`
- `LLMJudgeScore`
- `LLMJudgeResult`
- `LLMJudgeRunReport`
- `LLMJudgeProviderConfig`

## Optional Metrics

- `faithfulness_score`
- `answer_relevancy_score`
- `groundedness_score`
- `completeness_score`
- `uncertainty_honesty_score`
- `executive_usefulness_score`
- `judge_confidence`
- `judge_rationale`
- `judge_flags`

All scores are informational and use a `0.0` to `1.0` scale.

## Running

```bash
make answer-quality-llm-judge
```

Or:

```bash
python scripts/run_answer_quality_llm_judge.py --max-cases 1
```

Outputs:

- `data/regression_reports/answer_quality_llm_judge_report.json`
- `data/regression_reports/answer_quality_llm_judge_report.md`

## Dashboard Behavior

`scripts/build_regression_dashboard.py` reads
`answer_quality_llm_judge_report.json` when present and renders an
`Optional LLM Judge` section. Missing reports are `INFO`, not `WARN` or `FAIL`.
The judge never changes dashboard `PASS/WARN/FAIL` status.

## CI Behavior

The judge is disabled by default:

```env
ANSWER_QUALITY_LLM_JUDGE_ENABLED=false
ANSWER_QUALITY_LLM_JUDGE_PROVIDER=null
```

CI continues to depend on deterministic checks and JUnit XML only. No GitHub
Actions workflow runs the optional judge.

## Limitations

- No real provider is implemented in Epic 23.2.
- Null scores are deterministic plumbing checks, not semantic judgments.
- No external API key is required or read.
- The report is not a source of truth for startup claims or NVIDIA recommendations.
