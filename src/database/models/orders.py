import datetime
from enum import Enum
from typing import List

from sqlalchemy import ForeignKey, Date, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base, UserModel, MovieModel


class OrderStatusEnum(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    CANCELED = "Canceled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[OrderStatusEnum] = mapped_column(default=OrderStatusEnum.PENDING, nullable=False)
    total_amount: Mapped[DECIMAL] = mapped_column(DECIMAL(10, 2))

    user: Mapped["UserModel"] = relationship()
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, user_id={self.user_id}, "
            f"status='{self.status}', total_amount={self.total_amount}, "
            f"created_at={self.created_at})>"
        )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="order_items")
    movie: Mapped["MovieModel"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<OrderItem(id={self.id}, order_id={self.order_id}, "
            f"movie_id={self.movie_id})>"
        )
