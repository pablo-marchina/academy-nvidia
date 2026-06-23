# Epic 59 - Diagnostic Value Triage Before Technology Spikes

## Goal

Replace technology-first benchmarking with marginal system-value discovery. The product should first identify measurable opportunities to improve the current result or the product system around it, then map those opportunities to promising technology families through cheap oracle-style interventions before any product implementation is attempted.

## Scope

- Add a local-first diagnostic value triage script.
- Score baseline value across evidence sufficiency, unsupported claims, source trust/freshness, contradiction handling, recommendation specificity, next action quality, uncertainty calibration, lineage, alternatives-lost rationale, query robustness, evaluator auditability, and operational efficiency.
- Define oracle interventions that estimate whether a technology family could improve output without implementing the full technology.
- Produce evidence artifacts under `final_case_evidence/`.
- Integrate the diagnostic triage into quick final proof.
- Add focused unit tests.

## Non-Goals

- Do not implement GraphRAG, rerankers, query rewriting, or new recommendation engines in product runtime.
- Do not promote any candidate to runtime based only on oracle lift.
- Do not use network, paid SaaS, credentials, or Docker.
- Do not replace the existing ranked benchmark reports; this adds a pre-spike decision layer.

## Output Artifacts

- `final_case_evidence/diagnostic_value_triage_report.json`
- `final_case_evidence/diagnostic_value_triage_report.md`
- `final_case_evidence/diagnostic_eval_cases.json`

## Quality Method

1. Run deterministic diagnostic cases that represent likely improvement opportunities, not only failures.
2. Compute a baseline value score for the output and surrounding product behavior.
3. Apply explicit oracle interventions per improvement family:
   - query rewriting / multi-query expansion
   - GraphRAG / evidence graph expansion
   - source trust and freshness ranking
   - counter-evidence retrieval
   - evidence sufficiency / abstention
   - recommendation specificity / next-best-action enrichment
4. Report only `PROMISING_ORACLE_LIFT` when score lift crosses threshold.
5. Report `NO_MEASURED_HEADROOM` when baseline is already strong.
6. Report `SPIKE_CANDIDATE` only for families with measurable oracle lift.

## Validation

- Unit tests for scoring, oracle lift, and report generation.
- `ruff`, `black --check`, and `mypy` on touched Python files.
- `python scripts/prove_final_product.py --quick --skip-live`.
