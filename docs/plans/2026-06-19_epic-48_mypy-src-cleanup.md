# Epic 48 - mypy src cleanup

## Context
`python -m mypy src` currently fails with type errors in scoring calibration,
source/evidence calibration evaluation, RAG ingestion/evaluation, scraper base,
API service URL construction, and orchestration optional dependencies.

## Scope
- Fix only files reported by `mypy src`.
- Preserve runtime behavior and existing quantitative decisions.
- Prefer narrow type guards, local variables, casts, and missing-import ignores
  over broad refactors.

## Files Expected
- `src/scoring/startup_scoring.py`
- `src/evaluation/source_evidence_baseline.py`
- `src/scraping/scrapers/base_scraper.py`
- `src/rag/ingestion_pipeline.py`
- `src/evaluation/rag_eval.py`
- `src/api/service.py`
- `src/orchestration/runner.py`

## Plan
1. Add explicit guards where values are already runtime-validated but mypy still
   sees `None`.
2. Avoid variable reuse between source-quality and evidence-confidence result
   types in calibration evaluation.
3. Narrow union-valued calibration parameters before `int(...)`.
4. Type optional external imports in orchestration without changing runtime
   dependency behavior.
5. Re-run `python -m mypy src`; if clean, run targeted unit tests around touched
   modules where available.

## Validation
- `.venv\Scripts\python.exe -m mypy src`
- Targeted pytest suites for touched modules where feasible.
