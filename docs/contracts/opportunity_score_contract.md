# Opportunity Score Contract

## Module
- `src/services/product/opportunity_score_service.py` — `OpportunityScoreService`
- `src/repositories/opportunity_score.py` — `OpportunityScoreRepository`
- `src/database/models.py` — `OpportunityScoreRecord`

## What the Opportunity Score Promises

### Formula
final_score = clamp(base_score - penalty_total, 0.0, 1.0)

Where:
- **base_score** = sum of (component_value * redistributed_weight) for all present components
- **penalty_total** = sum of all penalty values

### Components (10 total, weights sum to 1.0)
| Component | Weight | Source |
|-----------|--------|--------|
| composite_ranking | 0.20 | ScoreRecord.composite → output_snapshot |
| evidence_coverage | 0.15 | ClaimRepository.get_evidence_coverage_summary |
| gap_resolution | 0.12 | GapDiagnosisRecord ratio of non-detected gaps |
| nvidia_mapping | 0.10 | NvidiaMappingRecord with high/critical priority |
| activation_readiness | 0.10 | ActivationRecommendationRecord next_step + confidence |
| dossier_completeness | 0.10 | ActivationDossierRecord.evidence_coverage |
| quality_score | 0.08 | ProductQualityRun.export_readiness_score |
| claim_support | 0.07 | Ratio of supported (strong/medium) to total claims |
| review_status | 0.05 | Latest ReviewDecision → score map |
| production_readiness | 0.03 | ScoreRecord.production_readiness / 100 |

Missing components have their weight redistributed proportionally to present components.

### Penalties (8 types)
| Penalty | Max | Condition |
|---------|-----|-----------|
| unsupported_claims | 0.15 | Unsupported / total claims |
| critical_unsupported | 0.20 | Critical claims unsupported |
| low_evidence_coverage | 0.10 | coverage < 0.30 (0.05 if < 0.50) |
| degraded_states | 0.12 | Per degraded state * 0.03 |
| low_confidence | 0.05 | composite confidence == "low" |
| contraindication | 1.0 | risk_claim with strong evidence containing "not_recommended" |
| incomplete_data | 0.10 | Proportional to missing component count |
| non_ai_classification | 1.0 | classification_score < 0.1 |

### Score Tiers
- critical: >= 0.85
- high: >= 0.70
- medium: >= 0.50
- low: >= 0.30
- not_recommended: < 0.30 OR contraindication OR non_ai

### Idempotency
- Each call to `compute_score` creates a new version (increments `score_version`)
- Latest version is used for all queries

### Explanation Model
Each result includes:
- Per-component values with weights
- List of missing components
- Penalties with type, value, and detail
- Human-readable reasoning text

### Evidence Refs
Aggregated from claim evidence_refs, activation recommendation evidence_refs, dossier evidence_refs, and RAG chunk references.

### Recommended Action
Determined from (in priority order):
1. Top activation recommendation `next_step`
2. Top activation recommendation `recommended_motion`
3. Latest dossier `recommended_motion`
4. Latest dossier `next_action`
5. "needs_more_evidence" (fallback)

## What It Does NOT Promise
- Does not modify RAG retrieval or Qdrant ingestion
- Does not produce startup discovery candidates
- Does not modify analysis run outputs
- Does not use LLM as primary judge

## Validation Rules
- Score must be float 0.0–1.0
- All component values must be float or null
- Penalty values must be float 0.0–1.0
- Version always increments

## Contract Version
1.0 — June 2026
