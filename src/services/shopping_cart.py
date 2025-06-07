from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.movies import MovieModel
from database.models.shopping_cart import CartItem, Cart
from database.models.accounts import UserModel
from validation.shopping_cart import (
    validate_movie_exists,
    validate_movie_not_in_cart,
    validate_movie_not_purchased,
)


class ShoppingCartService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_cart(self, user: UserModel) -> Cart:
        """Get existing cart or create new one for user."""
        query = select(Cart).where(Cart.user_id == user.id)
        result = await self.session.execute(query)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user.id)
            self.session.add(cart)
            await self.session.commit()
            await self.session.refresh(cart)

        return cart

    async def add_movie_to_cart(self, user: UserModel, movie_id: int) -> None:
        """Add movie to user's cart."""
        try:
            cart = await self.get_or_create_cart(user)
            await validate_movie_exists(self.session, movie_id)
            await validate_movie_not_in_cart(self.session, cart.id, movie_id)
            await validate_movie_not_purchased(self.session, user.id, movie_id)

            cart_item = CartItem(cart_id=cart.id, movie_id=movie_id)
            self.session.add(cart_item)
            await self.session.commit()
        except ValueError:
            await self.session.rollback()
            raise

    async def remove_movie_from_cart(self, user: UserModel, movie_id: int) -> None:
        """Remove movie from user's cart."""
        cart = await self.get_or_create_cart(user)
        query = select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.movie_id == movie_id
        )
        result = await self.session.execute(query)
        cart_item = result.scalar_one_or_none()

        if cart_item:
            await self.session.delete(cart_item)
            await self.session.commit()

    async def clear_cart(self, user: UserModel) -> None:
        """Clear user's cart."""
        cart = await self.get_or_create_cart(user)
        query = select(CartItem).where(CartItem.cart_id == cart.id)
        result = await self.session.execute(query)
        items = result.scalars().all()

        if items:
            for item in items:
                await self.session.delete(item)
            await self.session.commit()

    async def get_cart(self, user: UserModel) -> Cart:
        """Get user's cart with all items."""
        cart = await self.get_or_create_cart(user)
        # Eagerly load items and their related movie data
        query = (
            select(Cart)
            .where(Cart.id == cart.id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.movie)
            )
        )
        result = await self.session.execute(query)
        cart = result.scalar_one()
        return cart
