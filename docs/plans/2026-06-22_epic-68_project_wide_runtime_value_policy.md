# Epic 68 - Project-Wide Runtime Value Policy

## Goal

Apply the value-first benchmark policy to the whole project, including tools and technologies already promoted to runtime.

## Scope

- Extend the benchmark-first policy to explicitly cover existing runtime components.
- Add a runtime value policy gate/report that reads the runtime BOM and candidate catalog.
- Require every active runtime component to have benchmark evidence and a decision reference.
- Record known alternative families and whether free external/API alternatives must be benchmarked before replacement.
- Keep current runtime components unless a direct benchmark proves an alternative has higher output value after cost, latency, risk, governance, and reproducibility.
- Integrate the report into evidence pack generation and quick proof.
- Add focused unit tests.

## Non-Goals

- No runtime replacement in this increment.
- No live external API calls.
- No credential collection.
- No automatic promotion of free external services.

## Validation

- Unit tests for runtime value policy classification.
- Focused black/ruff on touched files.
- `python scripts/prove_final_product.py --quick --skip-live`.
