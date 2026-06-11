# Demo Acceptance & E2E Smoke Tests

**Decision:** Add a small Playwright smoke suite and API acceptance tests for
the existing local demo.

**Date:** 2026-06-11

## Context

The FastAPI demo API and React/Vite UI already exist, but the demo needed a
repeatable acceptance check to prove the end-to-end path works without relying
only on manual review.

## Decision

- Use FastAPI `TestClient` for API acceptance tests.
- Use Playwright for the minimal UI smoke because `frontend/package.json` and
  Vite scripts are already stable.
- Keep the smoke path offline and Qdrant-optional.
- Capture Playwright trace, screenshot, and video only on failure.
- Keep CI changes optional/local for E2E to avoid requiring Qdrant or LLM calls.

## Status

Implemented in Epic 27.
