# Final Evaluator Checklist

Use this checklist after `make prove-final-product`.

## Runtime

- Product configuration comes from `.env.example` plus environment values.
- PostgreSQL and Qdrant readiness are checked by official commands.
- No demo route, fixture, or mock provider participates in runtime promotion.

## Evidence

- Every recommendation has evidence, RAG support, confidence, business impact, implementation complexity, and next best action.
- Facts, inferences, and hypotheses remain separated in outputs.
- Evidence records include URL, timestamp, source trust, and lineage.

## Benchmarks

- `candidate_catalog.csv`, `benchmark_results.jsonl`, and `decision_ledger.csv` include `benchmark_type`.
- `LOCAL_READINESS` and `PROXY` do not promote runtime adoption alone.
- Mock providers are never classified as `OUTPUT_VALUE`.

## Release

- `make package-final-release` creates `release/academy-nvidia-final-case.zip`.
- `make check-final-release-zip` passes on the generated ZIP.
- The ZIP excludes `.env`, `.git`, `node_modules`, caches, builds, logs, local databases, and temporary exports.
