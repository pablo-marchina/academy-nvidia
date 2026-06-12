from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


def test_alembic_metadata_imports() -> None:
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config(str(ALEMBIC_INI))
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1
    head = script.get_revision(heads[0])
    assert head is not None
    assert head.doc in ("create all product entities", "create claim_records")


def test_alembic_upgrade_and_downgrade_sqlite(tmp_path: Path) -> None:
    db_path = tmp_path / "test_migrate.db"
    db_url = f"sqlite:///{db_path.as_posix()}"

    from alembic import command
    from alembic.config import Config

    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(config, "head")
    engine = None
    try:
        from sqlalchemy import create_engine

        engine = create_engine(db_url)
        tables = inspect(engine).get_table_names()
        required = {
            "startups",
            "startup_evidence",
            "analysis_runs",
            "score_records",
            "gap_diagnosis_records",
            "nvidia_mapping_records",
            "action_brief_records",
            "product_readiness_checks",
            "review_decisions",
            "export_records",
            "claim_records",
        }
        assert required.issubset(tables), f"Missing tables: {required - set(tables)}"
        assert "alembic_version" in tables

        original_tables = {
            "startups",
            "startup_evidence",
            "analysis_runs",
            "score_records",
            "gap_diagnosis_records",
            "nvidia_mapping_records",
            "action_brief_records",
            "product_readiness_checks",
            "review_decisions",
            "export_records",
        }

        command.downgrade(config, "-1")
        tables_after = inspect(engine).get_table_names()
        remaining = set(tables_after) - {"alembic_version"}
        assert "claim_records" not in tables_after, "claim_records should have been removed"
        missing_tables = original_tables - remaining
        assert original_tables.issubset(remaining), f"Original tables missing: {missing_tables}"
    finally:
        if engine is not None:
            engine.dispose()
