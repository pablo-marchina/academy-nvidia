# Diagnosis Contract

## Module
`src/diagnosis/gap_diagnosis.py` — `diagnose_gaps()`

## What It Promises

- Accepts: `StartupProfile`, `ClassificationResult`, `list[ValidatedEvidence]`, all 3 score results, `CompositeResult`
- Returns a `GapDiagnosisResult` with:
  - `diagnosed_gaps: list[GapWithEvidence]` — each with gap type, detection flag, confidence, evidence tag, reasoning, evidence list
  - `nvidia_technology_candidates: list[NvidiaTechnologyCandidate]` — mapped technologies per gap
  - `confidence: ConfidenceLevel` — overall diagnosis confidence
  - `reasoning: str` — aggregate reasoning
  - `evidence_used: list[ValidatedEvidence]`
  - `missing_evidence: list[str]`

## Gap Detectors (15)

`high_inference_cost`, `high_latency`, `external_api_dependency`, `agent_governance_gap`, `slow_data_pipeline`, `heavy_tabular_processing`, `privacy_or_controlled_deployment_gap`, `voice_need`, `computer_vision_need`, `observability_gap`, `model_evaluation_gap`, `simulation_need`, `robotics_need`, `healthcare_compliance_need`, `ai_cybersecurity_need`

## What It Does NOT Promise

- Does **not** generate final recommendations (see `recommendation_contract.md`)
- Does **not** suggest experiments
- Does **not** call any external API
- Does **not** guarantee every gap is detected (some are heuristic)

## Evidence Tags

Each gap is tagged: `FACT` (direct evidence), `INFERRED` (indirect), `HYPOTHESIS` (plausible but unverified)

## Validation Rules

- Every detected gap must have a confidence level
- Every gap must have at least one candidate technology mapped
- Gaps inferred without direct evidence are tagged `INFERRED`

## Contract Version
1.0 — June 2026
