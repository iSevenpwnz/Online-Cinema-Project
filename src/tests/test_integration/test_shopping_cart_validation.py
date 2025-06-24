import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import uuid

from database.models.movies import MovieModel, CertificationModel, CertificationEnum
from database.models.shopping_cart import Cart, CartItem
from database.models.accounts import UserModel
from validation.shopping_cart import (
    validate_movie_exists,
    validate_movie_not_in_cart,
    validate_movie_not_purchased,
    validate_cart_ownership,
)


@pytest.fixture
async def user(db_session: AsyncSession):
    """Create a test user."""
    user = UserModel.create(
        email="test@example.com",
        raw_password="TestPassword1!",
        group_id=1
    )
    user.is_active = True
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def movie(db_session: AsyncSession):
    """Create a test movie."""
    certification = CertificationModel(name=CertificationEnum.GENERAL_AUDIENCE)
    db_session.add(certification)
    await db_session.commit()

    movie = MovieModel(
        uuid=uuid.uuid4(),
        name="Test Movie",
        year=2024,
        time=120,
        imdb=8.0,
        votes=1000,
        description="Test description",
        price=9.99,
        certification_id=certification.id
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)
    return movie


@pytest.fixture
async def cart(db_session: AsyncSession, user: UserModel):
    """Create a test cart."""
    cart = Cart(user_id=user.id)
    db_session.add(cart)
    await db_session.commit()
    await db_session.refresh(cart)
    return cart


@pytest.mark.asyncio
async def test_validate_movie_exists_success(db_session: AsyncSession, movie: MovieModel):
    """Test successful movie existence validation."""
    await validate_movie_exists(db_session, movie.id)


@pytest.mark.asyncio
async def test_validate_movie_exists_failure(db_session: AsyncSession):
    """Test movie existence validation failure."""
    with pytest.raises(ValueError, match="Movie with id 999 not found"):
        await validate_movie_exists(db_session, 999)


@pytest.mark.asyncio
async def test_validate_movie_not_in_cart_success(
    db_session: AsyncSession, cart: Cart, movie: MovieModel
):
    """Test successful validation that movie is not in cart."""
    await validate_movie_not_in_cart(db_session, cart.id, movie.id)


@pytest.mark.asyncio
async def test_validate_movie_not_in_cart_failure(
    db_session: AsyncSession, cart: Cart, movie: MovieModel
):
    """Test validation failure when movie is already in cart."""
    cart_item = CartItem(cart_id=cart.id, movie_id=movie.id)
    db_session.add(cart_item)
    await db_session.commit()

    with pytest.raises(ValueError, match="Movie is already in cart"):
        await validate_movie_not_in_cart(db_session, cart.id, movie.id)


@pytest.mark.asyncio
async def test_validate_cart_ownership_success(
    db_session: AsyncSession, cart: Cart, user: UserModel
):
    """Test successful cart ownership validation."""
    await validate_cart_ownership(db_session, cart.id, user.id)


@pytest.mark.asyncio
async def test_validate_cart_ownership_failure(
    db_session: AsyncSession, cart: Cart
):
    """Test cart ownership validation failure."""
    with pytest.raises(HTTPException) as exc_info:
        await validate_cart_ownership(db_session, cart.id, 999)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You don't have permission to modify this cart"


@pytest.mark.asyncio
async def test_validate_movie_not_purchased_success(
    db_session: AsyncSession, user: UserModel, movie: MovieModel
):
    """Test successful validation that movie is not purchased."""
    # This test will pass as the validation is currently a placeholder
    await validate_movie_not_purchased(db_session, user.id, movie.id) 