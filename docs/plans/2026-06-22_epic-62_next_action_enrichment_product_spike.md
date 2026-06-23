# Epic 62 - Recommendation Next-Action Enrichment Product Spike

## Goal

Turn the second-ranked family spike, `recommendation_specificity_next_action`, into a narrow product spike that enriches existing recommendations with measurable next-best actions.

## Scope

- Add deterministic next-action enrichment for `PerGapRecommendation`.
- Preserve default recommendation behavior unless enrichment is explicitly called.
- Generate structured experiment details: owner, technology, metric, threshold, timeframe, evidence requirement, and success decision.
- Add a product-spike benchmark comparing generic next actions vs enriched next actions.
- Register the report in `final_case_evidence/` and quick proof.
- Add focused unit tests.

## Non-Goals

- Do not replace `build_recommendations()`.
- Do not make enriched next actions default runtime behavior yet.
- Do not call LLMs, network, paid services, Docker, or external tools.
- Do not claim runtime promotion based only on this spike.

## Artifacts

- `final_case_evidence/next_action_enrichment_product_spike_report.json`
- `final_case_evidence/next_action_enrichment_product_spike_report.md`

## Promotion Criteria Later

This spike may be promoted only after it improves real acceptance/product outputs without increasing unsupported recommendations or hiding missing evidence.

## Validation

- Focused pytest for enrichment and report generation.
- `ruff`, `black --check`, `mypy`.
- `python scripts/prove_final_product.py --quick --skip-live`.
