# Epic 64 - Counter-Evidence Retrieval Product Spike

## Goal

Turn the `counter_evidence_retrieval` family benchmark into a real, opt-in product spike that improves output quality by finding conflicting or limiting evidence before a NVIDIA recommendation is treated as strongly supported.

## Scope

- Add a deterministic local counter-evidence retriever under `src/rag/`.
- Search existing retrieved contexts or a `ChunkIndex` for risk, limitation, contradiction, stale, unsupported, and tradeoff signals.
- Return explicit contradiction records, degraded check candidates, confidence adjustment, uncertainty, and missing evidence prompts.
- Add a product-spike benchmark comparing baseline recommendation confidence against counter-evidence-aware output.
- Generate JSON and Markdown reports in `final_case_evidence/`.
- Wire the report into evidence pack generation and quick proof.
- Add focused unit tests.

## Non-Goals

- No default runtime activation.
- No external LLM judge.
- No network calls.
- No Qdrant schema change.

## Validation

- Focused pytest for counter-evidence retrieval and the benchmark script.
- Focused black, ruff, and mypy on touched files.
- `python scripts/prove_final_product.py --quick --skip-live`.
