# Epic 26.2 Workspace Output Validation Gate

## Decision

Add a workspace Output Validation Gate in two layers:

1. Behavioral rule in `AGENTS.md`.
2. Minimal deterministic validators in `src/validation/`.

## Rationale

The project already had contracts, schemas, CI, Answer Quality Eval, JUnit
reports, and a regression dashboard, but there was no single workspace rule that
required generated outputs to be checked before completion.

## Implementation Choice

Use existing Pydantic schemas and deterministic checks:

- `StartupActionBrief`
- API response schemas
- `TechnicalGap`
- NVIDIA gap-to-technology mapping matrix

Do not add dependencies or mandatory LLM judges.

## Consequences

- Structured outputs have a consistent `PASS/WARN/FAIL` validation result.
- Missing schemas or unknown response types can be surfaced as controlled
  warnings.
- Hotfixes stay lightweight and do not require heavy validation ritual.
