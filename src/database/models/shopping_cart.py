from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.database.models.base import Base
from src.database.models.movies import MovieModel


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Cart(user_id={self.user_id})>"


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "movie_id", name="unique_cart_movie"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    movie: Mapped["MovieModel"] = relationship("MovieModel")

    def __repr__(self) -> str:
        return f"<CartItem(cart_id={self.cart_id}, movie_id={self.movie_id})>"
