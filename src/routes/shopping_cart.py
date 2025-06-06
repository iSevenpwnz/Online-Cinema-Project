from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models.accounts import UserModel
from security.http import get_current_user
from schemas.shopping_cart import CartResponse
from services.shopping_cart import ShoppingCartService

router = APIRouter()


@router.get(
    "/",
    response_model=CartResponse,
    summary="Get user's shopping cart",
    description=(
        "<h3>This endpoint retrieves the current user's shopping cart with all items.</h3>"
    ),
    responses={
        200: {
            "description": "Shopping cart retrieved successfully.",
        }
    },
)
async def get_cart(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    """Get user's shopping cart with all items."""
    service = ShoppingCartService(db)
    cart = await service.get_cart(current_user)
    return CartResponse.from_dict(cart)


@router.post(
    "/add/{movie_id}",
    response_model=CartResponse,
    summary="Add movie to cart",
    description=("<h3>This endpoint adds a movie to the user's shopping cart.</h3>"),
    responses={
        200: {
            "description": "Movie added to cart successfully.",
        },
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {"example": {"detail": "Movie not found."}}
            },
        },
        400: {
            "description": "Invalid operation.",
            "content": {
                "application/json": {"example": {"detail": "Movie is already in cart."}}
            },
        },
    },
)
async def add_movie_to_cart(
    movie_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    """
    Add movie to user's shopping cart.

    :raises HTTPException:
        - 404 if movie not found
        - 400 if movie is already in cart or already purchased
    """
    service = ShoppingCartService(db)
    try:
        await service.add_movie_to_cart(current_user, movie_id)
        cart = await service.get_cart(current_user)
        print(f"DEBUG: cart.items = {[item.movie for item in cart.items]}")
        return CartResponse.from_dict(cart)
    except ValueError as e:
        status = 404 if "not found" in str(e).lower() else 400
        raise HTTPException(status_code=status, detail=str(e))


@router.delete(
    "/remove/{movie_id}",
    response_model=CartResponse,
    summary="Remove movie from cart",
    description=(
        "<h3>This endpoint removes a movie from the user's shopping cart.</h3>"
    ),
    responses={
        200: {
            "description": "Movie removed from cart successfully.",
        }
    },
)
async def remove_movie_from_cart(
    movie_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    """Remove movie from user's shopping cart."""
    service = ShoppingCartService(db)
    await service.remove_movie_from_cart(current_user, movie_id)
    cart = await service.get_cart(current_user)
    return CartResponse.from_dict(cart)


@router.delete(
    "/clear",
    response_model=CartResponse,
    summary="Clear cart",
    description=(
        "<h3>This endpoint removes all items from the user's shopping cart.</h3>"
    ),
    responses={
        200: {
            "description": "Cart cleared successfully.",
        }
    },
)
async def clear_cart(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CartResponse:
    """Clear user's shopping cart."""
    service = ShoppingCartService(db)
    await service.clear_cart(current_user)
    cart = await service.get_cart(current_user)
    return CartResponse.from_dict(cart)
