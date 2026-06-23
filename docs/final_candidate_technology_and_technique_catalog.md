# Final Candidate Technology and Technique Catalog

The machine-readable catalog is generated from section 8 of the canonical
roadmap:

```bash
make evidence-pack
python scripts/check_candidate_catalog.py
```

The generated CSV lives at:

```text
final_case_evidence/candidate_catalog.csv
```

Each row records candidate name, category, status, hypothesis, baseline,
metrics, benchmark, required configuration, expected runtime use, cost,
latency, risk, gate, evidence, and promotion/rejection/removal criteria.

Most candidates start as `DOCUMENTED_CANDIDATE`. Existing local runtime and
governance components are upgraded to `BENCHMARK_CONFIGURED` or `BENCHMARKED`
when an executable local check exists. Runtime promotion requires benchmark
evidence and a decision ledger record.
