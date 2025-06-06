# type: ignore
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database.models.movies import MovieModel
from database.models.shopping_cart import CartItem, Cart
from database.models.accounts import UserModel
from services.shopping_cart import ShoppingCartService
from tests.conftest import db_session, seed_user_groups


@pytest.fixture
async def user(db_session: AsyncSession, seed_user_groups):
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
async def country(db_session: AsyncSession):
    """Create a test country."""
    country = type('Country', (), {'id': 1, 'code': 'USA', 'name': 'United States'})()
    return country


@pytest.fixture
async def movie(db_session: AsyncSession, country):
    """Create a test movie."""
    movie = MovieModel(
        uuid="test-movie-uuid",
        name="Test Movie",
        year=2024,
        time=90,
        imdb=8.5,
        votes=1000,
        meta_score=80.0,
        gross=100000.0,
        description="Test overview",
        price=100.0,
        certification_id=1
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)
    return movie


@pytest.fixture
async def service(db_session: AsyncSession):
    """Create a shopping cart service instance."""
    return ShoppingCartService(db_session)


@pytest.mark.asyncio
async def test_get_or_create_cart(service: ShoppingCartService, user: UserModel):
    """Test getting or creating a cart."""
    # Get cart first time (should create new)
    cart = await service.get_or_create_cart(user)
    assert isinstance(cart, Cart)
    assert cart.user_id == user.id
    
    # Get cart again (should return existing)
    cart2 = await service.get_or_create_cart(user)
    assert cart2.id == cart.id
    assert cart2.user_id == user.id


@pytest.mark.asyncio
async def test_add_movie_to_cart(
    service: ShoppingCartService,
    user: UserModel,
    movie: MovieModel
):
    """Test adding a movie to cart."""
    await service.add_movie_to_cart(user, movie.id)
    cart = await service.get_cart(user)
    assert len(cart.items) == 1
    assert cart.items[0].movie_id == movie.id


@pytest.mark.asyncio
async def test_add_nonexistent_movie_to_cart(
    service: ShoppingCartService,
    user: UserModel
):
    """Test adding a nonexistent movie to cart."""
    with pytest.raises(ValueError, match="Movie with id 999 not found"):
        await service.add_movie_to_cart(user, 999)


@pytest.mark.asyncio
async def test_add_duplicate_movie_to_cart(
    service: ShoppingCartService,
    user: UserModel,
    movie: MovieModel
):
    """Test adding a movie that's already in cart."""
    # Add movie first time
    await service.add_movie_to_cart(user, movie.id)

    # Try to add the same movie again
    with pytest.raises(ValueError, match="Movie is already in cart"):
        await service.add_movie_to_cart(user, movie.id)


@pytest.mark.asyncio
async def test_remove_movie_from_cart(
    service: ShoppingCartService,
    user: UserModel,
    movie: MovieModel
):
    """Test removing a movie from cart."""
    # Add movie first
    await service.add_movie_to_cart(user, movie.id)

    # Remove movie
    await service.remove_movie_from_cart(user, movie.id)

    # Verify cart is empty
    cart = await service.get_cart(user)
    assert len(cart.items) == 0


@pytest.mark.asyncio
async def test_clear_cart(
    service: ShoppingCartService,
    user: UserModel,
    movie: MovieModel,
    db_session: AsyncSession
):
    """Test clearing the cart."""
    # Add multiple movies
    movie2 = MovieModel(
        uuid="test-movie2-uuid",
        name="Test Movie 2",
        year=2024,
        time=100,
        imdb=9.0,
        votes=2000,
        meta_score=85.0,
        gross=200000.0,
        description="Test overview 2",
        price=150.0,
        certification_id=1
    )
    db_session.add(movie2)
    await db_session.commit()
    await db_session.refresh(movie2)

    # Add movies to cart
    await service.add_movie_to_cart(user, movie.id)
    await service.add_movie_to_cart(user, movie2.id)

    # Clear cart
    await service.clear_cart(user)
    cart = await service.get_cart(user)
    assert len(cart.items) == 0 