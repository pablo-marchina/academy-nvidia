# Epic 22 Regression Dashboard

**Date:** 2026-06-10
**Status:** Implemented

## Summary

Epic 22 adds a local Markdown/JSON regression dashboard for corpus maintenance
runs. It consolidates ingestion, freshness, RAG evals, golden evals, Action Brief
checks, warnings, and blocking failures.

## Implemented

- `scripts/build_regression_dashboard.py`
- `data/regression_reports/latest_dashboard.md`
- `data/regression_reports/latest_dashboard.json`
- `docs/46_regression_dashboard.md`
- `make regression-dashboard`
- GitHub Actions Job Summary integration
- Artifact upload for dashboard files
- `tests/unit/test_regression_dashboard.py`

## Status Semantics

- `PASS`: no failures or warnings.
- `WARN`: stale sources, missing context/evidence, missing reports, or malformed reports.
- `FAIL`: validation errors, failed sources, expired sources, RAG eval failure, or golden eval failure.

## Notes

The dashboard reads existing reports only. It does not call retrieval, mutate Qdrant,
generate Action Briefs, or change scoring/diagnosis/recommendation logic.
