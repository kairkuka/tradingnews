from sqlalchemy import create_engine, inspect

from app.db.models import Base


def test_models_create_expected_tables_on_sqlite() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == {
        "assets",
        "candles",
        "event_reactions",
        "events",
        "historical_statistics",
        "market_context",
        "news",
    }


def test_candles_have_required_unique_constraint() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    constraints = inspector.get_unique_constraints("candles")
    assert {
        "column_names": ["symbol", "timeframe", "timestamp"],
        "name": "uq_candles_symbol_timeframe_timestamp",
    } in constraints

