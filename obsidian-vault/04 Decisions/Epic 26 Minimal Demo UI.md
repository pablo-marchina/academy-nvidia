# Minimal Demo UI

**Decision:** Create a local Vite + React + TypeScript UI under `frontend/`
that consumes the existing FastAPI demo API.

**Date:** 2026-06-11

## Context

The CLI demo and FastAPI API already demonstrate the pipeline programmatically,
but evaluators still need terminal or Swagger. A small local UI removes that
friction without changing product logic.

## Decision

- Use Vite + React + TypeScript because no frontend package existed.
- Keep state local to `App`; no global state library.
- Use plain CSS; no design system or component library.
- Configure API base URL with `VITE_API_BASE_URL`.
- Treat Qdrant offline as warning/status, not a fatal UI failure.
- Render API outputs directly and do not recompute business logic in the UI.

## Status

Implemented in Epic 26.
