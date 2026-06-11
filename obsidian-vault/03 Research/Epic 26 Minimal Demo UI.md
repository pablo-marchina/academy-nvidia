# Epic 26 - Minimal Demo UI

**Date:** 2026-06-11

## Summary

Minimal local web UI for the existing FastAPI demo API. It lets evaluators load
a fictional startup sample, generate a Startup Action Brief, inspect scores,
gaps, NVIDIA technologies, evidence, warnings, uncertainties, RAG/Qdrant status,
and run optional answer quality evaluation.

## What was built

- `frontend/` Vite + React + TypeScript app
- `frontend/src/api/client.ts` with helpers for health, RAG status, brief,
  evaluation, and demo artifacts
- Focused UI components for input, status, scores, gaps, evidence, brief, and
  eval
- Makefile targets for `ui-install`, `ui-dev`, `ui-build`, and `demo-full`
- `docs/51_minimal_demo_ui.md`

## Principle

The UI is a viewer/controller for the API. It does not duplicate scoring,
diagnosis, recommendation, RAG retrieval, Qdrant ingestion, or answer quality
metrics.
