# Recommendation Logic

## Principle

No NVIDIA technology recommendation is valid unless there is an **explicit technical gap** with evidence or clearly marked inference. Recommendations are purely **deterministic** — no LLM, no RAG, no external calls.

## Inputs

- `GapDiagnosisResult` — diagnosed gaps with confidence and evidence tags
- `GapWithEvidence` — per-gap detection, confidence, evidence tag, evidence list
- `NvidiaTechnologyCandidate` — technology names mapped to gaps by the diagnosis module
- `CompositeResult` — motion hint (`immediate_outreach`, `monitor_and_nurture`, `lack_evidence_more_research`, `not_recommended`)
- `ClassificationResult`, `StartupProfile` — for business justification context

## Core Logic

### Action Matrix

| Detected | Gap Confidence | Recommended Motion           | Action                |
|----------|----------------|------------------------------|-----------------------|
| No       | any            | any                          | MONITOR               |
| Yes      | LOW            | any                          | VALIDATE_MANUALLY     |
| Yes      | MEDIUM/HIGH    | lack_evidence_more_research  | VALIDATE_MANUALLY     |
| Yes      | LOW/MEDIUM     | monitor_and_nurture          | MONITOR               |
| Yes      | HIGH           | immediate_outreach           | APPROACH_NOW          |
| Yes      | HIGH           | high_priority_outreach       | APPROACH_NOW          |
| any      | any            | not_recommended              | NOT_RECOMMENDED       |

### Priority Mapping

- **APPROACH_NOW** + HIGH confidence → HIGH priority
- **APPROACH_NOW** + MEDIUM confidence → MEDIUM priority
- **VALIDATE_MANUALLY** → MEDIUM or LOW
- **MONITOR** / **NOT_RECOMMENDED** → LOW

### SuggestedTechnicalExperiment

Generated **only** for `APPROACH_NOW` actions. 14 pre-built experiment templates covering all `TechnicalGap` values. Each template includes:

- Title, hypothesis, success metric, estimated duration, NVIDIA technology, next step

## Output

`RecommendationResult`:
- `startup_name`
- `overall_priority` — highest among detected gaps
- `overall_confidence` — aggregated from detected gaps
- `recommendations` — list of `PerGapRecommendation`
- `top_recommendation` — highest priority `APPROACH_NOW` recommendation
- `reasoning` — human-readable summary
- `evidence_used` — all evidence considered
- `missing_evidence` — gaps flagged as inferred or missing

## Implementation Complexity

| Complexity | Technologies                                      |
|------------|---------------------------------------------------|
| LOW        | NIM, cuDF, cuML                                   |
| MEDIUM     | TensorRT-LLM, Triton, RAPIDS, Riva, NeMo, MONAI   |
| HIGH       | Omniverse, Isaac, Clara, Morpheus, AI Enterprise  |

## Quality Checks

- Gap is explicit (enum value in `TechnicalGap`)
- Nvidia technology recommendation only generated when gap is diagnosed
- Weak/low-confidence evidence downgrades action to `VALIDATE_MANUALLY` or `MONITOR`
- `SuggestedTechnicalExperiment` only for `APPROACH_NOW`
- Evidence used and missing evidence are tracked per gap and aggregated
- No hallucinated technologies — all mapped from `_COMPLEXITY_MAP` or `_EXPERIMENT_TEMPLATES`
