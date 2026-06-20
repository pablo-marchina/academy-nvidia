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
  - `rag_output: RagPipelineOutput | None` — RAG retrieval/packing result (Epic 14.1)

## Pipeline Steps (11 → 12 com RAG opcional)

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
**12. Product RAG (optional)** — hybrid retrieval (lexical/semantic), deterministic reranking, context packing, provenance tracking

## What It Does NOT Promise

- Does **not** produce a final brief or report (deferred to Briefing module)
- Does **not** write to any database
- Does **not** call external APIs
- Does **not** require RAG — `rag_output` is `None` when RAG is not configured

## Validation Rules

- `final_priority_score` must be 0–100
- `recommended_motion` must be one of the 5 enumerated values
- `composite_score` must be present (not None)
- `gap_diagnosis` and `recommendation` are optional (None when pipeline errors, but never None in normal operation)
- No NVIDIA technology is recommended without a diagnosed gap
- `rag_output.packing_result.packed` contexts carry source_id and url (provenance)
- `rag_output.missing_context` is `True` when corpus is empty or no gaps detected
- RAG does NOT alter `recommended_motion`, scores, or evidence_used

## Example

```python
result = run_full_pipeline("StartupX", raw_text)
assert result.gap_diagnosis is not None
assert result.recommendation is not None
assert len(result.recommendation.recommendations) >= 1
```

## Final Product Readiness Update - 2026-06-19

The library pipeline can still be exercised in isolated tests, but the product path is strict:

- Product API analysis runs require the readiness gate before persistence or orchestration.
- In `APP_MODE=product`, RAG is not optional; Qdrant, a real embedding model, a fresh populated corpus, and productive calibration are required before analysis.
- Lexical-only, in-memory, mock, fixture, or synthetic inputs are allowed only in explicit tests and cannot satisfy product readiness.
- Product outputs must preserve provenance and separate fact, inference, and hypothesis through the downstream brief, recommendation, dossier, and quality contracts.

## Contract Version
3.0 — June 2026 (integration of RAG reranking + context packing)
