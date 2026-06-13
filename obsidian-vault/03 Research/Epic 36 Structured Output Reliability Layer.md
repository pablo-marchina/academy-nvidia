# Epic 36 — Structured Output Reliability Layer

## What
Centralized layer for JSON parsing, structural repair, Pydantic validation, retry with repair, quality metrics, and readiness check integration.

## Why
Every module that parses JSON was doing its own error handling inconsistently. The Activation Dossier had no schema validation at all.

## How
- `parse_json_output()` — safe json.loads with error capture
- `repair_json_if_safe()` — deterministic structural repair (trailing commas, truncated JSON)
- `validate_output()` — Pydantic validation with structured error details
- `run_validation_with_repair()` — retry (max 1) with repair between attempts
- `build_structured_output_result()` — unified result dataclass with status, parsed object, errors
- 5 degraded state codes for structured output failures
- 6 quality metric constants with thresholds

## Integration
- Activation Dossier: `DossierJsonSchema` model, `_validate_dossier_json()` method, readiness check on failure
- Quality: evaluator in `quality/evaluators/structured_output_reliability.py`
- Optional Instructor trial: `llm_judge_instructor_adapter.py` with lazy import

## Files
- `src/evaluation/structured_outputs.py`
- `src/services/product/degraded.py` (5 new codes)
- `src/quality/constants.py` (6 new constants)
- `src/quality/evaluators/structured_output_reliability.py`
- `src/evaluation/llm_judge_instructor_adapter.py`

## Test Results
- 34 unit tests, 4 integration tests — all passing
