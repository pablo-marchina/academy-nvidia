"""Alembic environment configuration for the product database.

Reads PRODUCT_DB_URL from the environment (defaults to SQLite).
Supports both SQLite (batch mode) and PostgreSQL.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.database.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

database_url = (
    os.getenv("PRODUCT_DB_URL") or config.get_main_option("sqlalchemy.url") or "sqlite:///data/product/product.db"
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    is_sqlite = database_url.startswith("sqlite")
    connect_args: dict = {}
    if is_sqlite:
        from pathlib import Path
        from sqlalchemy.engine import make_url

        url_obj = make_url(database_url)
        if url_obj.database and url_obj.database != ":memory:":
            Path(url_obj.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        connect_args["check_same_thread"] = False

    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = database_url

    engine = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
