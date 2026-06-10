# Epic 21 Scheduled Corpus Maintenance Workflow

**Date:** 2026-06-10
**Status:** Implemented

## Summary

Epic 21 adds a controlled corpus maintenance workflow for the NVIDIA corpus. It
orchestrates source sync dry-run, freshness audit, Qdrant ingest dry-run, optional
real ingestion, RAG evals, golden evals, and report generation.

## Implemented

- `.github/workflows/corpus-maintenance.yml`
- `scripts/run_corpus_maintenance.py`
- `docs/45_scheduled_corpus_maintenance.md`
- Makefile targets:
  - `corpus-maintenance-dry-run`
  - `corpus-maintenance-evals`
  - `corpus-maintenance-ingest`
- GitHub Actions artifact upload for maintenance reports

## Invariants

- Real Qdrant ingestion is disabled by default.
- Source promotion is disabled by default.
- Schedule runs only the safe path.
- Expired corpus sources fail by default.
- No auto-commit and no external report publication.

## Validation

- Local safe-mode script execution.
- Full repo quality gates: pytest, ruff, black, mypy.

## Notes

No new tests were added because the approved Epic 21 scope excluded `tests/`.
Operational validation is captured by maintenance reports and existing quality
gates.
