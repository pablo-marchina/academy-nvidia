# Recommendation Contract

## Module
`src/recommendation/recommendation_engine.py` — `build_recommendations()`
`src/recommendation/schemas.py` — `PerGapRecommendation`, `RecommendationResult`, `RecommendedNextAction`, `SuggestedTechnicalExperiment`

## What It Promises

- Accepts: startup name, `StartupProfile`, `ClassificationResult`, validated evidence, all 3 score results, `CompositeResult`, priority score, motion, and `GapDiagnosisResult`
- Returns a `RecommendationResult` with:
  - `recommendations: list[PerGapRecommendation]` — one per diagnosed gap
  - `overall_priority` — highest priority among detected gaps
  - `overall_confidence` — aggregate confidence
  - `top_recommendation` — highest-priority APPROACH_NOW (or None)
  - `reasoning` — human-readable summary
  - `evidence_used` and `missing_evidence`

## Per-Gap Recommendation

Each contains:
- `action`: `approach_now`, `validate_manually`, `monitor`, `not_recommended`
- `priority`: `high`, `medium`, `low`
- `implementation_complexity`: `low`, `medium`, `high`
- `suggested_experiment`: only present when action is `approach_now`
- `evidence_used` and `missing_evidence`

## Action Logic

| Gap Detected | Gap Confidence | Motion | Action |
|---|---|---|---|
| No | any | any | MONITOR |
| Yes | LOW | any | VALIDATE_MANUALLY |
| Yes | any | lack_evidence | VALIDATE_MANUALLY |
| Yes | MEDIUM | monitor_and_nurture | MONITOR |
| Yes | HIGH | immediate/high_priority | APPROACH_NOW |
| any | any | not_recommended | NOT_RECOMMENDED |

## What It Does NOT Promise

- Does **not** diagnose gaps (depends on `GapDiagnosisResult`)
- Does **not** call external APIs or LLMs
- Does **not** generate product RAG context
- Does **not** persist results
- Does **not** produce a full briefing (only per-gap recommendations)

## Experiment Generation

`SuggestedTechnicalExperiment` is only generated for `APPROACH_NOW` actions. 14 pre-built templates.

## Validation Rules

- No recommendation without a diagnosed gap
- No experiment without `APPROACH_NOW` action
- `missing_evidence` populated for inferred gaps
- Top recommendation is the highest-priority `APPROACH_NOW`

## Final Product Readiness Update - 2026-06-19

In the product path, recommendations are blocked unless productive calibration and RAG support are available. Each NVIDIA recommendation must expose evidence, RAG provenance, confidence, business impact, implementation complexity, and next best action. Decisions based on `UNCALIBRATED`, placeholder, synthetic, or `production_allowed=false` calibration records are non-productive and must fail readiness or quality gates instead of silently emitting a recommendation.

## Contract Version
1.0 — June 2026
