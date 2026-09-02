"""foundation schema

Revision ID: 0001_foundation_schema
Revises:
Create Date: 2026-09-02 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_foundation_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MARKET_NUMERIC = sa.Numeric(20, 8)


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("importance", sa.String(), nullable=True),
        sa.Column("actual", MARKET_NUMERIC, nullable=True),
        sa.Column("forecast", MARKET_NUMERIC, nullable=True),
        sa.Column("previous", MARKET_NUMERIC, nullable=True),
        sa.Column("revision", MARKET_NUMERIC, nullable=True),
        sa.Column("unit", sa.String(), nullable=True),
        sa.Column("surprise", MARKET_NUMERIC, nullable=True),
        sa.Column("surprise_pct", MARKET_NUMERIC, nullable=True),
        sa.Column("surprise_zscore", MARKET_NUMERIC, nullable=True),
        sa.Column("directionality", sa.String(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_category", "events", ["category"])
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_timestamp", "events", ["timestamp"])

    op.create_table(
        "assets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("asset_class", sa.String(), nullable=False),
        sa.Column("exchange", sa.String(), nullable=True),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("timezone", sa.String(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol"),
    )
    op.create_index("ix_assets_asset_class", "assets", ["asset_class"])
    op.create_index("ix_assets_symbol", "assets", ["symbol"])

    op.create_table(
        "candles",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("timeframe", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", MARKET_NUMERIC, nullable=False),
        sa.Column("high", MARKET_NUMERIC, nullable=False),
        sa.Column("low", MARKET_NUMERIC, nullable=False),
        sa.Column("close", MARKET_NUMERIC, nullable=False),
        sa.Column("volume", MARKET_NUMERIC, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "symbol",
            "timeframe",
            "timestamp",
            name="uq_candles_symbol_timeframe_timestamp",
        ),
    )
    op.create_index("ix_candles_symbol_timestamp", "candles", ["symbol", "timestamp"])
    op.create_index(
        "ix_candles_symbol_timeframe_timestamp",
        "candles",
        ["symbol", "timeframe", "timestamp"],
    )

    op.create_table(
        "news",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("event_id", sa.Uuid(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("importance", sa.String(), nullable=True),
        sa.Column("sentiment", sa.String(), nullable=True),
        sa.Column("sentiment_score", MARKET_NUMERIC, nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_news_category", "news", ["category"])
    op.create_index("ix_news_event_id", "news", ["event_id"])
    op.create_index("ix_news_source", "news", ["source"])
    op.create_index("ix_news_timestamp", "news", ["timestamp"])

    op.create_table(
        "market_context",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trend", sa.String(), nullable=True),
        sa.Column("atr", MARKET_NUMERIC, nullable=True),
        sa.Column("atr_percentile", MARKET_NUMERIC, nullable=True),
        sa.Column("rsi", MARKET_NUMERIC, nullable=True),
        sa.Column("dxy_change", MARKET_NUMERIC, nullable=True),
        sa.Column("us10y_change", MARKET_NUMERIC, nullable=True),
        sa.Column("vix", MARKET_NUMERIC, nullable=True),
        sa.Column("gold_change", MARKET_NUMERIC, nullable=True),
        sa.Column("silver_change", MARKET_NUMERIC, nullable=True),
        sa.Column("gold_silver_ratio", MARKET_NUMERIC, nullable=True),
        sa.Column("oil_change", MARKET_NUMERIC, nullable=True),
        sa.Column("btc_change", MARKET_NUMERIC, nullable=True),
        sa.Column("nq_change", MARKET_NUMERIC, nullable=True),
        sa.Column("session", sa.String(), nullable=True),
        sa.Column("volatility_regime", sa.String(), nullable=True),
        sa.Column("distance_from_daily_high", MARKET_NUMERIC, nullable=True),
        sa.Column("distance_from_daily_low", MARKET_NUMERIC, nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_market_context_event_id", "market_context", ["event_id"])
    op.create_index("ix_market_context_symbol", "market_context", ["symbol"])
    op.create_index("ix_market_context_timestamp", "market_context", ["timestamp"])

    op.create_table(
        "event_reactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("horizon", sa.String(), nullable=False),
        sa.Column("price_before", MARKET_NUMERIC, nullable=False),
        sa.Column("price_after", MARKET_NUMERIC, nullable=False),
        sa.Column("return_pct", MARKET_NUMERIC, nullable=False),
        sa.Column("high_after", MARKET_NUMERIC, nullable=True),
        sa.Column("low_after", MARKET_NUMERIC, nullable=True),
        sa.Column("max_favorable_excursion", MARKET_NUMERIC, nullable=True),
        sa.Column("max_adverse_excursion", MARKET_NUMERIC, nullable=True),
        sa.Column("volatility_before", MARKET_NUMERIC, nullable=True),
        sa.Column("volatility_after", MARKET_NUMERIC, nullable=True),
        sa.Column("volume_before", MARKET_NUMERIC, nullable=True),
        sa.Column("volume_after", MARKET_NUMERIC, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_reactions_event_id", "event_reactions", ["event_id"])
    op.create_index("ix_event_reactions_horizon", "event_reactions", ["horizon"])
    op.create_index("ix_event_reactions_symbol", "event_reactions", ["symbol"])

    op.create_table(
        "historical_statistics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("horizon", sa.String(), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("up_count", sa.Integer(), nullable=False),
        sa.Column("down_count", sa.Integer(), nullable=False),
        sa.Column("up_probability", MARKET_NUMERIC, nullable=False),
        sa.Column("down_probability", MARKET_NUMERIC, nullable=False),
        sa.Column("mean_return", MARKET_NUMERIC, nullable=True),
        sa.Column("median_return", MARKET_NUMERIC, nullable=True),
        sa.Column("std_return", MARKET_NUMERIC, nullable=True),
        sa.Column("p10", MARKET_NUMERIC, nullable=True),
        sa.Column("p25", MARKET_NUMERIC, nullable=True),
        sa.Column("p50", MARKET_NUMERIC, nullable=True),
        sa.Column("p75", MARKET_NUMERIC, nullable=True),
        sa.Column("p90", MARKET_NUMERIC, nullable=True),
        sa.Column("median_mfe", MARKET_NUMERIC, nullable=True),
        sa.Column("median_mae", MARKET_NUMERIC, nullable=True),
        sa.Column("confidence", sa.String(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "event_type",
            "symbol",
            "horizon",
            name="uq_historical_statistics_event_symbol_horizon",
        ),
    )
    op.create_index("ix_historical_statistics_event_type", "historical_statistics", ["event_type"])
    op.create_index("ix_historical_statistics_horizon", "historical_statistics", ["horizon"])
    op.create_index("ix_historical_statistics_symbol", "historical_statistics", ["symbol"])


def downgrade() -> None:
    op.drop_index("ix_historical_statistics_symbol", table_name="historical_statistics")
    op.drop_index("ix_historical_statistics_horizon", table_name="historical_statistics")
    op.drop_index("ix_historical_statistics_event_type", table_name="historical_statistics")
    op.drop_table("historical_statistics")

    op.drop_index("ix_event_reactions_symbol", table_name="event_reactions")
    op.drop_index("ix_event_reactions_horizon", table_name="event_reactions")
    op.drop_index("ix_event_reactions_event_id", table_name="event_reactions")
    op.drop_table("event_reactions")

    op.drop_index("ix_market_context_timestamp", table_name="market_context")
    op.drop_index("ix_market_context_symbol", table_name="market_context")
    op.drop_index("ix_market_context_event_id", table_name="market_context")
    op.drop_table("market_context")

    op.drop_index("ix_news_timestamp", table_name="news")
    op.drop_index("ix_news_source", table_name="news")
    op.drop_index("ix_news_event_id", table_name="news")
    op.drop_index("ix_news_category", table_name="news")
    op.drop_table("news")

    op.drop_index("ix_candles_symbol_timeframe_timestamp", table_name="candles")
    op.drop_index("ix_candles_symbol_timestamp", table_name="candles")
    op.drop_table("candles")

    op.drop_index("ix_assets_symbol", table_name="assets")
    op.drop_index("ix_assets_asset_class", table_name="assets")
    op.drop_table("assets")

    op.drop_index("ix_events_timestamp", table_name="events")
    op.drop_index("ix_events_event_type", table_name="events")
    op.drop_index("ix_events_category", table_name="events")
    op.drop_table("events")
