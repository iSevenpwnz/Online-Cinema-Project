from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.shopping_cart import CartItem
from database.models.movies import MovieModel


async def validate_movie_exists(session: AsyncSession, movie_id: int) -> None:
    """Validate that movie exists"""
    movie = await session.get(MovieModel, movie_id)
    if not movie:
        raise ValueError("Movie not found")


async def validate_movie_not_in_cart(
    session: AsyncSession, cart_id: int, movie_id: int
) -> None:
    """Validate that movie is not already in cart"""
    stmt = select(CartItem).where(
        CartItem.cart_id == cart_id, CartItem.movie_id == movie_id
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Movie is already in cart")


async def validate_movie_not_purchased(
    session: AsyncSession, user_id: int, movie_id: int
) -> None:
    """
    Validate that movie is not already purchased by user.
    This is a placeholder - we'll need to implement the actual check
    once we have the purchased movies model.
    """
    # TODO: Implement check against purchased movies
    pass
