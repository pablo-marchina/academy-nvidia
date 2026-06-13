# Startup Activation Dossier

**Status:** Implementado (Epic 34)
**Module:** `src/services/product/dossier_service.py`
**API:** `src/api/product_routes.py`

## Purpose

The Startup Activation Dossier is a deterministic, versioned snapshot of all
product intelligence for a single `AnalysisRun`. It consolidates scores, gaps,
NVIDIA technology mappings, activation recommendations, claims, review
decisions, and readiness checks into a single JSON artifact that can be
rendered as Markdown for human consumption or exported for downstream systems.

Unlike the Action Brief (which is a lightweight executive summary driven by the
pipeline), the Dossier is an exhaustive, evidence-first projection of every
persisted record related to an analysis run, enriched with uncertainty markers
and risk indicators.

## Design Principles

1. **Deterministic** — Dossier content depends only on persisted records.
   No LLM calls, no embedding similarity, no random variation. Same run always
   produces the same dossier.

2. **Idempotent** — `POST /dossier` returns the existing latest dossier if
   one exists. Use `?force=true` to regenerate with a new version.

3. **Versioned** — Each dossier carries `version` (1, 2, 3…) per analysis run.
   Previous versions are preserved but marked `is_latest=False`.

4. **Honest about gaps** — Missing data becomes explicit `uncertainty` or
   `risk` entries in the dossier JSON. The Markdown template displays "Not
   available" or "Missing" for absent fields.

5. **Non-blocking readiness** — Readiness checks (low coverage, unsupported
   claims, missing review) are recorded as risks in the dossier but do not
   prevent generation.

## Dossier JSON Structure

```jsonc
{
  "dossier_id": "uuid",
  "analysis_run_id": "uuid",
  "version": 1,
  "created_at": "2026-06-12T12:00:00Z",
  "startup_summary": {
    "name": "String",
    "sector": "String",
    "status": "String",
    "tags": ["String"]
  },
  "scores": {
    "composite_score": 45.2,
    "defensibility_score": 60.0,
    "inception_fit_score": 40.0,
    "production_readiness_score": 35.0,
    "confidence": 0.7,
    "evidence_coverage": 65.0
  },
  "detected_gaps": [
    {
      "gap_id": "latency_inference",
      "type": "latency_optimization",
      "severity": "high",
      "detected": true,
      "missing_evidence": ["..."]
    }
  ],
  "nvidia_technologies": [
    {"gap_id": "latency_inference", "technology": "TensorRT", "confidence": 0.85}
  ],
  "activation_recommendations": [],
  "claims": {
    "total": 5,
    "unsupported_count": 1,
    "items": []
  },
  "review": {"decision": null, "reviewer": null},
  "readiness_checks": [],
  "uncertainties": [
    {"source": "unsupported_claims", "description": "1 claim(s) lack evidence support", "impact": "high"},
    {"source": "low_coverage", "description": "Evidence coverage is low (0%)", "impact": "high"}
  ],
  "risks": [
    {"risk": "Dossier has unsupported critical claims", "severity": "high", "code": "DOSSIER_UNSUPPORTED_CRITICAL_CLAIMS"}
  ],
  "executive_verdict": {
    "unsupported_claim_count": 1,
    "coverage_pct": 0.0,
    "has_review": false,
    "has_activation_playbook": false,
    "has_complete_scores": false
  }
}
```

## Markdown Template Sections

1. Startup Activation Dossier (header with metadata)
2. Startup Summary
3. Executive Verdict
4. Scores
5. Risks & Uncertainties
6. Claims
7. Diagnosed Gaps
8. NVIDIA Technologies
9. Activation Recommendations
10. Readiness Checks
11. Human Review

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/analysis-runs/{id}/dossier` | Generate dossier (idempotent) |
| POST | `/api/v1/analysis-runs/{id}/dossier?force=true` | Regenerate with new version |
| GET | `/api/v1/analysis-runs/{id}/dossier` | Return latest dossier JSON |
| GET | `/api/v1/analysis-runs/{id}/dossier/markdown` | Return latest dossier Markdown |

## Integration Points

- `AnalysisRunRead` includes `dossier_summary` (created_at, version, risk_count,
  unsupported_claim_count)
- `OpportunityListItem` includes `dossier_available` and `latest_dossier_id`
- Readiness checks in `degraded.py` cover dossier-specific states

## Future Work (v2)

- Auto-update dossier when review decision is submitted
- Export link between ExportRecord and dossier_id
- Differential view between dossier versions
- PDF export of dossier Markdown
