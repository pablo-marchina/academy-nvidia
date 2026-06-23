# Epic 61 - Query Rewriting Product Spike

## Goal

Turn the highest-ranked family spike, `query_rewriting_multiquery`, into a narrow product spike that can be measured against baseline retrieval without promoting it to default runtime behavior.

## Scope

- Add deterministic query variant generation for RAG retrieval.
- Add multi-query lexical retrieval with dedupe by chunk id and best relevance score.
- Integrate the feature into `run_rag_pipeline()` behind an explicit optional config.
- Add a focused product-spike benchmark report under `final_case_evidence/`.
- Keep default behavior unchanged unless the config is explicitly passed.
- Add unit tests for variant generation, retrieval lift, pipeline mode, and report generation.

## Non-Goals

- Do not make query rewriting the default product path yet.
- Do not use LLMs, external APIs, network, Docker, or credentials.
- Do not choose a third-party query rewriting tool yet.
- Do not alter Qdrant requirements for product readiness.

## Artifacts

- `final_case_evidence/query_rewriting_product_spike_report.json`
- `final_case_evidence/query_rewriting_product_spike_report.md`

## Promotion Criteria Later

This spike may be promoted only after:

- real corpus/product acceptance shows measurable retrieval or recommendation lift;
- latency/cost/risk are measured;
- no regression in provenance, source freshness, or unsupported claim control;
- decision ledger records the promotion decision.

## Validation

- Focused pytest for query rewriting and product spike benchmark.
- `ruff`, `black --check`, `mypy`.
- `python scripts/prove_final_product.py --quick --skip-live`.
