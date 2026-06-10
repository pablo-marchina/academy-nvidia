# Briefing Contract

## Module
`src/briefing/` — `build_action_brief()`, `render_action_brief_markdown()`

## What It Promises

- Accepts a `PipelineResult` (from `run_full_pipeline()`)
- Returns a `StartupActionBrief` with:
  - `startup_name`, `website`, `sector`, `one_line_summary`
  - `verdict` (high_priority, promising, early_stage, needs_validation, not_recommended)
  - `final_priority_score`, `recommended_motion`, `confidence`
  - `sections: list[BriefSection]` — 13 possible sections (some conditional)
  - Raw data dicts: `ai_native_classification`, `defensibility_score`, `inception_fit_score`, `production_readiness_score`, `composite_score`
  - `diagnosed_gaps`, `nvidia_technology_candidates`, `recommendations`
  - `evidence_used: list[BriefEvidenceItem]`
  - `missing_evidence: list[str]`
  - `uncertainties: list[BriefUncertainty]`
  - `next_action_for_nvidia_team: str`
  - `reasoning: str`
- Renders a Markdown string via `render_action_brief_markdown(brief)`
- Serializes to JSON via `brief.model_dump_json(indent=2)`

## Verdict Logic

| Condition | Verdict |
|---|---|
| `motion == "not_recommended"` | NOT_RECOMMENDED |
| `confidence == LOW` or `evidence_count == 0` | NEEDS_VALIDATION |
| `has_approach_now` and `confidence == HIGH` | HIGH_PRIORITY |
| `total_gaps == 0` and `confidence == HIGH` | PROMISING |
| `motion in (monitor_and_nurture, lack_evidence)` | EARLY_STAGE |
| `has_approach_now` (any confidence) | HIGH_PRIORITY |
| Default | PROMISING |

## What It Does NOT Promise

- Does **not** generate new gaps, scores, or recommendations
- Does **not** call external APIs
- Does **not** persist results
- Does **not** produce PDF exports
- Does **not** add new dependencies

## Brief Sections (13)

1. Executive Summary
2. Why This Startup Matters
3. AI-Native Maturity
4. Scores Overview
5. Production AI Gaps
6. NVIDIA Fit
7. Recommended NVIDIA Technologies
8. Suggested Technical Experiment (conditional: only if APPROACH_NOW)
9. Recommended Motion
10. Evidence
11. Missing Evidence (conditional: only if non-empty)
12. Uncertainties / Limitations (conditional: only if non-empty)
13. Next Action

## Validation Rules

- Verdict is derived deterministically from confidence + motion + approach_now count
- No NVIDIA technology appears without a diagnosed gap
- `missing_evidence` is always included (even if empty)
- `uncertainties` includes every gap tagged INFERRED or HYPOTHESIS
- Low confidence never maps to HIGH_PRIORITY verdict
- Brief is always JSON-serializable

## Contract Version
1.0 — June 2026 (Epic 10)
