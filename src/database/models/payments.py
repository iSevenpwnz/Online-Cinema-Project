from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List

from sqlalchemy import DECIMAL, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.accounts import UserModel
from database.models.base import Base
from database.models.orders import Order, OrderItem


class PaymentStatusEnum(str, Enum):
    SUCCESSFUL = "successful"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentModel(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    status: Mapped[PaymentStatusEnum] = mapped_column(nullable=False)
    external_payment_id: Mapped[str] = mapped_column(nullable=False)

    user: Mapped[UserModel] = relationship()
    order: Mapped[Order] = relationship()
    payment_items: Mapped[List["PaymentItemModel"]] = relationship(
        back_populates="payment",
    )

    @property
    def amount(self) -> Decimal:
        return sum(
            (
                Decimal(str(item.price_at_payment))
                for item in self.payment_items
            ),
            Decimal("0"),
        )


class PaymentItemModel(Base):
    __tablename__ = "payment_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id"),
        nullable=False,
    )
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id"),
        nullable=False,
    )
    price_at_payment: Mapped[DECIMAL] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
    )

    payment: Mapped[PaymentModel] = relationship(
        back_populates="payment_items",
    )
    order_item: Mapped[OrderItem] = relationship()
