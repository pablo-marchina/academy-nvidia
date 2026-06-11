# Epic 27 - Demo Acceptance & E2E Smoke Tests

**Date:** 2026-06-11

## Summary

Epic 27 adds a repeatable acceptance layer for the existing demo API and UI.
It validates that the API starts, the sample startup input generates a Startup
Action Brief, the UI builds, and the browser smoke path renders scores, gaps,
evidence, warnings/status, and evaluation output.

## What was built

- API acceptance tests in `tests/integration/test_demo_acceptance.py`
- Playwright smoke tests in `tests/e2e/test_demo_ui.spec.ts`
- Playwright config in `frontend/playwright.config.ts`
- Makefile targets for `demo-acceptance`, `ui-e2e`, and `demo-full-check`
- Demo acceptance documentation in `docs/52_demo_acceptance.md`

## Principle

Acceptance tests verify wiring and output shape only. They do not alter or
recompute scoring, diagnosis, recommendation, RAG retrieval, Qdrant ingestion,
or Action Brief generation.
