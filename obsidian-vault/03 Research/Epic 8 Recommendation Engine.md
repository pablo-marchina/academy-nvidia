---
title: "Epic 8: Recommendation Engine"
date: 2026-06-09
status: completed
tags: [epic, recommendation, deterministic]
---

# Epic 8: Recommendation Engine

## Summary

Deterministic recommendation engine that maps diagnosed technical gaps to NVIDIA technologies without RAG or LLM.

## Deliverables

- `src/recommendation/schemas.py` — 4 Pydantic models
- `src/recommendation/recommendation_engine.py` — engine with build_recommendations
- `src/recommendation/__init__.py` — re-exports
- `tests/unit/test_recommendation_engine.py` — 22 tests
- `docs/06_recommendation_logic.md` — rewritten

## Key Design

- Action matrix: APPROACH_NOW / VALIDATE_MANUALLY / MONITOR / NOT_RECOMMENDED
- 14 experiment templates covering all TechnicalGap values
- Complexity mapped to 16 NVIDIA technologies (3 levels)
- Old `NvidiaRecommendation` removed from `extraction/schemas.py`

## Dependencies

- `src/diagnosis/` schemas (GapDiagnosisResult, GapWithEvidence, EvidenceTag)
- `src/diagnosis/nvidia_mapping.py` — technology candidates per gap
- `src/scoring/composite_ranking.py` — composite result with motion

## Not integrated yet

Engine exists but is not called by the pipeline. Integration deferred to Epic 10.
