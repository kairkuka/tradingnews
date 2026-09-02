from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_creates_foundation_schema(tmp_path: Path) -> None:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'phase1.db'}"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "events" in inspector.get_table_names()
    assert "historical_statistics" in inspector.get_table_names()

