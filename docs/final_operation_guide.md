# Final Operation Guide

## Start

```bash
cp .env.example .env
docker compose up -d
make setup
make ingest-real-sources
make prove-final-product
make run
```

## Validate

```bash
make validate
make check-repository-clean
make package-final-release
make check-final-release-zip
```

## Operate

- Keep configuration in environment variables or `.env`; never commit secrets.
- Regenerate evidence with `make evidence-pack` after changing governance, benchmark, source, or release policy.
- Run `make prove-final-product` before release.
- Store release evidence in `final_case_evidence/`.

## Recover

- For unsupported recommendations, follow `docs/final_ai_incident_response_plan.md`.
- For failed gates, follow `docs/final_rca_workflow.md`.
- For stale or invalid sources, follow `docs/final_data_retention_policy.md`.
