---
title: "Decision 015: Recommendation Engine"
date: 2026-06-09
status: accepted
tags: [decision, recommendation, deterministic]
---

# Decision 015: Recommendation Engine

## Context

Epic 8 required a Recommendation Engine that maps diagnosed technical gaps to NVIDIA technologies, generating per-gap recommendations with actions, priorities, and suggested experiments.

## Decision

1. **Deterministic (no LLM/RAG)** — The engine uses pre-built experiment templates and rule-based action/priority logic. No LangGraph, no external API calls.
2. **Independent module** — Lives in `src/recommendation/`, not integrated into the pipeline. Integration deferred to Epic 10.
3. **Action matrix** — 4 actions (APPROACH_NOW, VALIDATE_MANUALLY, MONITOR, NOT_RECOMMENDED) determined by gap confidence, detection status, and recommended motion.
4. **SuggestedTechnicalExperiment** — Only generated for APPROACH_NOW actions. 14 pre-built templates covering all TechnicalGap values.
5. **Old NvidiaRecommendation removed** — Replaced by `PerGapRecommendation` + `RecommendationResult` in the new module.

## Consequences

- New module: `src/recommendation/` with `schemas.py`, `recommendation_engine.py`, `__init__.py`
- 22 unit tests added
- `agents/state.py` simplified (recommendations field removed)
- `extraction/schemas.py`: NvidiaRecommendation removed
- `tests/unit/test_schemas.py`: NvidiaRecommendation test removed
- Total test count: 117 → 138

## Status

Accepted. Implemented in Epic 8.
