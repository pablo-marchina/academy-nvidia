# Epic 36 — Structured Output Reliability Layer

**Decision:** Create centralized `structured_outputs.py` module with parse, repair, validate, retry, readiness, and quality metrics.

**Context:** Dossier JSON validation was a simple try/except with no retry, no repair, no structured failure tracking, no quality metrics.

**Rationale:** Centralization ensures consistent failure handling across all structured output consumers. Retry with repair handles common failure patterns (trailing commas, truncated JSON).

**Key components:**
- `src/evaluation/structured_outputs.py` — core module
- 5 degraded state codes in `src/services/product/degraded.py`
- 6 quality metric constants in `src/quality/constants.py`
- Integration with Activation Dossier (`DossierJsonSchema` + `_validate_dossier_json()`)
- Optional Instructor trial adapter (`src/evaluation/llm_judge_instructor_adapter.py`)
- `[llm-judge]` extra in `pyproject.toml`

**Status:** Implementado.

**Related:** Decision 038 (Confidence), Decision 041 (this decision in DECISIONS.md)
