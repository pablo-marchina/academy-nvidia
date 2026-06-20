# Scoring Contract

## Modules
- `src/scoring/defensibility_score.py` — `compute_defensibility_score()`
- `src/scoring/inception_fit_score.py` — `compute_inception_fit_score()`
- `src/scoring/production_readiness.py` — `compute_production_readiness()`
- `src/scoring/composite_ranking.py` — `compute_composite_ranking()`
- `src/services/product/opportunity_score_service.py` — `OpportunityScoreService` (consolidated 0.0–1.0 score)

## What Each Score Promises

### Defensibility Score (0–100)
- 6 dimensions: `competitive_moat`, `data_advantage`, `technical_barrier`, `talent_depth`, `customer_lock_in`, `capital_efficiency`
- Each dimension scored 0–100
- Final score = weighted average of dimensions
- Requires: `StartupProfile` + `ValidatedEvidence`

### Inception Fit Score (0–100)
- 4 dimensions: `nvidia_ecosystem_alignment`, `ai_native_maturity`, `scalability_potential`, `market_relevance`
- Each dimension scored 0–100
- Final score = weighted average of dimensions
- Requires: `StartupProfile` + `ClassificationResult` + `ValidatedEvidence`

### Production Readiness (0–100)
- 4 dimensions: `deployment_maturity`, `monitoring_observability`, `scalability_infra`, `team_ml_ops`
- Each dimension scored 0–100
- Final score = weighted average with confidence penalty
- Requires: `StartupProfile` + `ClassificationResult` + `ValidatedEvidence`

### Composite Score (0–100)
- Weighted aggregation: defensibility 30%, inception fit 25%, production readiness 35%, classification level 10%
- Redistributes weights proportionally when a score is absent
- Applies confidence penalty based on evidence coverage
- Returns `recommended_motion` hint
- Requires: all 3 scores + `ClassificationResult` + `ValidatedEvidence`

## What They Do NOT Promise

- Do not diagnose technical gaps
- Do not recommend NVIDIA technologies
- Do not produce human-readable briefings
- Do not persist data

## Validation Rules

- All scores must be float 0–100
- All dimensions must be float 0–100
- `composite_ranking` always returns a `recommended_motion` even if data is sparse

## Final Product Readiness Update - 2026-06-19

Product scoring must be registry-backed. Weights, thresholds, confidence penalties, and recommendation gates used in productive decisions must come from the calibration registry and must be marked production-allowed. Uncalibrated, placeholder, synthetic-only, or disabled calibration entries can remain for tests or research reports, but cannot produce product recommendations, scores, or readiness success.

## Contract Version
1.0 — June 2026
