# Epic 66 - Evidence Sufficiency Abstention Product Spike

## Goal

Turn the `evidence_sufficiency_abstention` family benchmark into a real, opt-in product spike that prevents weakly supported recommendations from being presented as proven when required evidence is missing or unresolved counter-evidence exists.

## Scope

- Add deterministic evidence sufficiency and abstention assessment under `src/rag/`.
- Compute required evidence coverage, provenance coverage, counter-evidence pressure, adjusted confidence, uncertainty, missing evidence, and recommended action.
- Keep the behavior opt-in and experimental; do not change default recommendation behavior.
- Add a product-spike benchmark comparing baseline high-confidence outputs against sufficiency-aware outputs.
- Generate JSON and Markdown reports in `final_case_evidence/`.
- Wire the report into evidence pack generation and quick proof.
- Add focused unit tests.

## Non-Goals

- No default runtime activation.
- No external judge or network call.
- No Qdrant schema change.
- No UI change in this increment.

## Validation

- Focused pytest for evidence sufficiency and benchmark script.
- Focused black, ruff, and mypy on touched files.
- `python scripts/prove_final_product.py --quick --skip-live`.
