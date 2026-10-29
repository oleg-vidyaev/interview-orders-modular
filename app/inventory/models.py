from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class StockItem(Base):
    __tablename__ = "stock_items"

    sku: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[int]  # cents
    available: Mapped[int]


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    sku: Mapped[str] = mapped_column(ForeignKey("stock_items.sku"))
    qty: Mapped[int]


class StockMovement(Base):
    """Audit trail: every change of `available` must have a movement."""

    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(ForeignKey("stock_items.sku"))
    delta: Mapped[int]
    reason: Mapped[str]
