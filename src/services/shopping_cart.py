from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from database.models.movies import MovieModel
from database.models.shopping_cart import CartItem, Cart
from database.models.accounts import UserModel, UserGroupEnum
from validation.shopping_cart import (
    validate_movie_exists,
    validate_movie_not_in_cart,
    validate_movie_not_purchased,
    validate_cart_ownership,
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
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Please activate your account before adding items to cart."
                )
            cart = await self.get_or_create_cart(user)
            await validate_cart_ownership(self.session, cart.id, user.id)
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
        await validate_cart_ownership(self.session, cart.id, user.id)

        stmt = delete(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.movie_id == movie_id
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def clear_cart(self, user: UserModel) -> None:
        """Clear user's cart."""
        cart = await self.get_or_create_cart(user)
        await validate_cart_ownership(self.session, cart.id, user.id)

        stmt = delete(CartItem).where(CartItem.cart_id == cart.id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def is_movie_in_any_cart(self, movie_id: int) -> bool:
        """
        Check if movie is present in any user's cart.

        Args:
            movie_id: ID of the movie to check

        Returns:
            bool: True if movie is in any cart, False otherwise
        """
        query = select(CartItem).where(CartItem.movie_id == movie_id)
        result = await self.session.execute(query)
        return result.first() is not None

    async def get_cart(self, user: UserModel) -> Cart:
        """Get user's cart with all items."""
        cart = await self.get_or_create_cart(user)
        await validate_cart_ownership(self.session, cart.id, user.id)

        query = (
            select(Cart)
            .where(Cart.id == cart.id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.movie).selectinload(MovieModel.genres)
            )
        )
        result = await self.session.execute(query)
        cart = result.scalar_one()
        return cart

    async def get_user_cart(self, admin: UserModel, user_id: int) -> Cart:
        """
        Get any user's cart (admin only).

        Args:
            admin: The admin user making the request
            user_id: ID of the user whose cart to retrieve

        Returns:
            Cart: The requested user's cart

        Raises:
            HTTPException: If admin is not authorized or user not found
        """
        if not admin.has_group(UserGroupEnum.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view other users' carts."
            )

        user_query = select(UserModel).where(UserModel.id == user_id)
        user_result = await self.session.execute(user_query)
        target_user = user_result.scalar_one_or_none()

        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        cart = await self.get_or_create_cart(target_user)

        cart_query = (
            select(Cart)
            .where(Cart.id == cart.id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.movie).selectinload(MovieModel.genres)
            )
        )
        cart_result = await self.session.execute(cart_query)
        cart_with_items = cart_result.scalar_one()
        return cart_with_items
