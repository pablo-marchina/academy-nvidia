# Epic 60 - Family Spike Benchmarks for Promising Value Families

## Goal

Run real local micro-spike benchmarks for the promising technology families identified by diagnostic value triage, without integrating those technologies into the product runtime.

## Scope

- Add a disposable family spike benchmark runner.
- Test the promising families in ranked order:
  - counter-evidence retrieval / contradiction checks
  - GraphRAG / evidence graph expansion
  - query rewriting / multi-query expansion
  - recommendation specificity / next-action enrichment
  - evidence sufficiency / abstention
  - source trust / freshness ranking
- Compare baseline output vs spike output using the same value dimensions from diagnostic triage.
- Produce adoption guidance as `ADOPT_CANDIDATE`, `PROMISING_NEEDS_PRODUCT_SPIKE`, or `REJECT_NO_REAL_LIFT`.
- Keep all spikes outside product runtime.
- Integrate the report into the final evidence pack and quick proof.

## Non-Goals

- Do not promote any family or tool to runtime in this increment.
- Do not choose a concrete vendor/tool inside each family yet.
- Do not use network, paid services, Docker, or external credentials.
- Do not replace real production benchmarks; this stage only decides whether a family deserves product spike work.

## Artifacts

- `final_case_evidence/family_spike_cases.json`
- `final_case_evidence/family_spike_benchmark_report.json`
- `final_case_evidence/family_spike_benchmark_report.md`

## Evaluation

Each micro-spike is executable and deterministic. It changes a controlled product-like output:

- counter-evidence retrieves conflicting evidence and recalibrates confidence;
- GraphRAG builds explicit source-gap-technology-alternative lineage edges;
- query rewriting adds deterministic query variants and recovers missing relevant evidence;
- next-action enrichment turns a generic recommendation into a measurable technical experiment;
- evidence sufficiency abstains or downgrades when support is thin;
- source trust/freshness reranks evidence by trust and recency.

The result is scored across output quality, robustness, auditability, and operational value.

## Validation

- Unit tests for each spike family and report aggregation.
- `ruff`, `black --check`, `mypy` on touched Python files.
- `python scripts/prove_final_product.py --quick --skip-live`.
