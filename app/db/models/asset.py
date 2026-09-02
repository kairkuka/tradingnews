import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)

    display_name: Mapped[str] = mapped_column(nullable=False)
    asset_class: Mapped[str] = mapped_column(nullable=False, index=True)

    exchange: Mapped[str | None] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(nullable=False)

    timezone: Mapped[str] = mapped_column(nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

