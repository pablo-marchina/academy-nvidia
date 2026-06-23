# Epic 63 - GraphRAG Evidence Graph Product Spike

## Goal

Turn the `graphrag_evidence_graph` family benchmark into a real, opt-in product spike that measures whether an evidence graph improves output quality through explicit lineage, source-to-gap-to-technology paths, and alternatives-lost explanations.

## Scope

- Add a local deterministic GraphRAG evidence graph module under `src/rag/`.
- Build graph nodes and edges from existing retrieved NVIDIA contexts, diagnosed gap, recommended technology, and alternative technologies.
- Keep behavior opt-in and experimental; do not make it default runtime behavior.
- Add a product-spike benchmark script that compares baseline evidence summaries against graph-backed lineage output.
- Generate JSON and Markdown evidence reports in `final_case_evidence/`.
- Wire the report into final evidence pack generation and quick proof.
- Add focused unit tests for graph construction, alternatives lost, and benchmark decision.

## Non-Goals

- No Qdrant schema change.
- No LLM graph extraction.
- No automatic promotion to default runtime.
- No new external dependency.

## Validation

- Focused pytest for the new GraphRAG product spike.
- Focused black, ruff, and mypy on touched Python files.
- `python scripts/prove_final_product.py --quick --skip-live`.
