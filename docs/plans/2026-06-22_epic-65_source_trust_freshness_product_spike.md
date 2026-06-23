# Epic 65 - Source Trust Freshness Product Spike

## Goal

Turn the `source_trust_freshness_ranking` family benchmark into a real, opt-in product spike that improves output quality by ranking evidence with explicit source trust, provenance, lifecycle, and freshness signals before it is used in recommendations.

## Scope

- Add deterministic source trust and freshness ranking under `src/rag/`.
- Score retrieved contexts using official NVIDIA source signals, URL provenance, active/deprecated lifecycle, expiration, and relevance.
- Keep the behavior opt-in and experimental; do not change default RAG ranking.
- Add a product-spike benchmark comparing relevance-only baseline ordering against trust/freshness-aware ordering.
- Generate JSON and Markdown reports in `final_case_evidence/`.
- Wire the report into evidence pack generation and quick proof.
- Add focused unit tests.

## Non-Goals

- No network calls.
- No live source freshness checks.
- No default runtime activation.
- No Qdrant schema change.

## Validation

- Focused pytest for source trust/freshness ranking and benchmark script.
- Focused black, ruff, and mypy on touched files.
- `python scripts/prove_final_product.py --quick --skip-live`.
