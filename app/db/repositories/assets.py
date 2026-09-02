from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.assets import SUPPORTED_ASSETS, AssetConfig
from app.db.models import Asset


class AssetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_supported_assets(
        self,
        assets: Iterable[AssetConfig] = SUPPORTED_ASSETS.values(),
    ) -> int:
        count = 0
        for config in assets:
            self.upsert(config)
            count += 1
        return count

    def upsert(self, config: AssetConfig) -> Asset:
        existing = self.session.execute(
            select(Asset).where(Asset.symbol == config.symbol)
        ).scalar_one_or_none()

        if existing is None:
            asset = Asset(
                symbol=config.symbol,
                display_name=config.display_name,
                asset_class=config.asset_class.value,
                exchange=config.exchange,
                currency=config.quote_currency,
                timezone=config.timezone,
                enabled=config.enabled,
            )
            self.session.add(asset)
            return asset

        existing.display_name = config.display_name
        existing.asset_class = config.asset_class.value
        existing.exchange = config.exchange
        existing.currency = config.quote_currency
        existing.timezone = config.timezone
        existing.enabled = config.enabled
        return existing

    def list_enabled_symbols(self) -> tuple[str, ...]:
        rows = self.session.scalars(
            select(Asset.symbol).where(Asset.enabled.is_(True)).order_by(Asset.symbol)
        )
        return tuple(rows)

