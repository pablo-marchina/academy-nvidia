# Pipeline Output Contract

## Module
`src/pipeline/run_pipeline.py` — `run_full_pipeline()`

## What It Promises

- Accepts a `startup_name: str` and `raw_text: str` (or pre-built `StartupProfile`)
- Returns a `PipelineResult` with:
  - `startup_profile: StartupProfile`
  - `ai_native_classification: ClassificationResult`
  - `validated_evidence: list[ValidatedEvidence]`
  - `defensibility_score: DefensibilityScoreResult`
  - `inception_fit_score: InceptionFitScoreResult`
  - `production_readiness_score: ProductionReadinessResult`
  - `composite_score: CompositeResult`
  - `ranked: list[RankedStartup]`
  - `final_priority_score: float`
  - `recommended_motion: str` (one of: `immediate_outreach`, `high_priority_outreach`, `monitor_and_nurture`, `lack_evidence_more_research`, `not_recommended`)
  - `gap_diagnosis: GapDiagnosisResult | None` — diagnosed gaps with evidence tags and confidence
  - `recommendation: RecommendationResult | None` — per-gap recommendations with actions and experiments
  - `evidence_used: list[ValidatedEvidence]` — aggregated from all modules
  - `missing_evidence: list[str]` — aggregated from all modules

## Pipeline Steps (11)

1. Extraction
2. AI-native classification
3. Evidence validation
4. AI-Native Defensibility Score
5. NVIDIA Inception Fit Score
6. Production AI Readiness
7. Composite Score + Confidence-aware Ranking
8. Gap Diagnosis (15 deterministic detectors)
9. NVIDIA Technology Mapping (deterministic matrix)
10. Deterministic Recommendation Engine
11. Output consolidation

## What It Does NOT Promise

- Does **not** produce a final brief or report (deferred to Epic 9)
- Does **not** write to any database
- Does **not** call external APIs
- Does **not** execute Product RAG

## Validation Rules

- `final_priority_score` must be 0–100
- `recommended_motion` must be one of the 5 enumerated values
- `composite_score` must be present (not None)
- `gap_diagnosis` and `recommendation` are optional (None when pipeline errors, but never None in normal operation)
- No NVIDIA technology is recommended without a diagnosed gap

## Example

```python
result = run_full_pipeline("StartupX", raw_text)
assert result.gap_diagnosis is not None
assert result.recommendation is not None
assert len(result.recommendation.recommendations) >= 1
```

## Contract Version
2.0 — June 2026 (integration of diagnosis + recommendation)
