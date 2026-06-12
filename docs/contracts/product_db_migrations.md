# Product Database Migrations Contract

**Module:** `migrations/`
**Date:** 2026-06-12

## Purpose

Manage versioned schema changes for the transactional product database using Alembic. Supports both SQLite (default local) and PostgreSQL (production future).

## Setup

Alembic is configured via:
- `alembic.ini` — root config pointing to `migrations/`
- `migrations/env.py` — reads `PRODUCT_DB_URL` from environment (config overrides env var)
- `migrations/versions/` — versioned migration scripts
- `migrations/script.py.mako` — template for new revisions

## Commands

```bash
# Apply all pending migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# Auto-generate a new migration from model changes
alembic revision --autogenerate -m "description"

# Show current revision
alembic current

# Show migration history
alembic history
```

Or via Makefile:
```bash
make db-upgrade
make db-downgrade
make db-migrate msg="description"
make db-current
make db-history
```

## Connection

The database URL is resolved in this order:
1. `sqlalchemy.url` from alembic config (if set via `--sqlalchemy.url` or `config.set_main_option`)
2. `PRODUCT_DB_URL` environment variable
3. Default: `sqlite:///data/product/product.db`

## SQLite Support

- Default local database
- `render_as_batch=True` — required because SQLite does not support `ALTER TABLE DROP COLUMN` or `ALTER TABLE ALTER COLUMN`
- `check_same_thread=False` for FastAPI concurrency
- Directory is auto-created for file-based SQLite

## PostgreSQL Support

- Validated via `PRODUCT_DB_TEST_URL` environment variable
- `docker compose up postgres -d` to start a local PostgreSQL instance
- Connection string: `postgresql://postgres:postgres@localhost:5432/startup_radar`

### Differences from SQLite

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| JSON type | `JSON` (stored as text) | `JSON` (stored as json) |
| Boolean | Stored as 0/1 | Stored as true/false |
| DateTime with tz | Stored as ISO text | Stored as `timestamptz` |
| ALTER TABLE | Batch mode (recreate) | Direct ALTER |
| Foreign Keys | Optional (`PRAGMA foreign_keys`) | Enforced by default |
| UniqueConstraint | Enforced | Enforced |
| Indexes | Supported | Supported |

All SQLAlchemy models use portable types (`String`, `Text`, `Float`, `Boolean`, `DateTime(timezone=True)`, `JSON`). No queries depend on SQLite-only features.

## Migration Policy

- Each migration must be reviewable standalone
- Downgrade must be possible for the last migration (`alembic downgrade -1`)
- Auto-generated migrations must be reviewed before commit
- Migration scripts go in `migrations/versions/`
- The `alembic_version` table tracks the current revision

## Testing

Unit tests in `tests/unit/test_alembic_migrations.py`:
- Verify migration metadata and head revision
- Test full upgrade → downgrade cycle on a temporary SQLite database

Integration tests in `tests/integration/test_postgres_migration.py`:
- Require `PRODUCT_DB_TEST_URL` environment variable
- Marked `@pytest.mark.integration` and skippable by default
- Test upgrade, JSON columns, and repository smoke on PostgreSQL

## Entity List (10 tables)

| Table | Purpose |
|-------|---------|
| `startups` | Product startup identity |
| `startup_evidence` | Public evidence attached to startups |
| `analysis_runs` | Persisted pipeline lifecycle |
| `score_records` | Score results per analysis run |
| `gap_diagnosis_records` | Diagnosed technical gaps |
| `nvidia_mapping_records` | Gap-to-technology mappings |
| `action_brief_records` | Versioned Action Brief records |
| `product_readiness_checks` | Dependency and quality checks |
| `review_decisions` | Human review decisions |
| `export_records` | Generated export artifacts |
