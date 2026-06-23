# Final External Reviewer Mode

This mode lets an external evaluator reproduce the product from a clean checkout without hidden local state.

## Commands

```bash
git clone <repo>
cd <repo>
cp .env.example .env
docker compose up -d
make setup
make ingest-real-sources
make run-evals
make prove-final-product
make run
```

## Rules

- The reviewer must use `.env.example` as the configuration template.
- PostgreSQL and Qdrant readiness must be proven by official commands.
- RAG recommendations must cite persisted evidence and retrieval support.
- The final source release must be generated with `make package-final-release`.
- The release ZIP must pass `make check-final-release-zip`.
- No cache, manual export, notebook output, local database, or prebuilt frontend artifact is required for success.

## Evidence

- `final_case_evidence/external_reviewer_mode_report.json`
- `final_case_evidence/cold_start_report.json`
- `final_case_evidence/final_proof_summary.json`
