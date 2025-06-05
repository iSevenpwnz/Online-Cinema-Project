import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database.models.movies import MovieModel, MovieStatusEnum
from database.models.accounts import UserModel
from tests.conftest import client, db_session, seed_user_groups


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
async def movie(db_session: AsyncSession):
    """Create a test movie."""
    movie = MovieModel(
        name="Test Movie",
        date=datetime(2024, 1, 1).date(),
        score=85.5,
        overview="Test overview",
        status=MovieStatusEnum.RELEASED,
        budget=1000000,
        revenue=2000000
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)
    return movie


@pytest.fixture
async def auth_headers(client: AsyncClient, user: UserModel):
    """Get authentication headers for the test user."""
    response = await client.post(
        "/theater/accounts/login/",
        json={
            "email": user.email,
            "password": "TestPassword1!"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_empty_cart(client: AsyncClient, auth_headers):
    """Test getting an empty cart."""
    response = await client.get("/theater/cart/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] is not None
    assert data["items"] == []


@pytest.mark.asyncio
async def test_add_movie_to_cart(client: AsyncClient, auth_headers, movie: MovieModel):
    """Test adding a movie to cart."""
    response = await client.post(
        f"/theater/cart/items/{movie.id}/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["movie_id"] == movie.id
    assert data["items"][0]["movie_name"] == movie.name


@pytest.mark.asyncio
async def test_add_nonexistent_movie_to_cart(client: AsyncClient, auth_headers):
    """Test adding a nonexistent movie to cart."""
    response = await client.post(
        "/theater/cart/items/999/",
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Movie not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_duplicate_movie_to_cart(
    client: AsyncClient,
    auth_headers,
    movie: MovieModel
):
    """Test adding a movie that's already in cart."""
    # Add movie first time
    await client.post(
        f"/theater/cart/items/{movie.id}/",
        headers=auth_headers
    )
    # Try to add the same movie again
    response = await client.post(
        f"/theater/cart/items/{movie.id}/",
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "Movie is already in cart" in response.json()["detail"]


@pytest.mark.asyncio
async def test_remove_movie_from_cart(
    client: AsyncClient,
    auth_headers,
    movie: MovieModel
):
    """Test removing a movie from cart."""
    # Add movie first
    await client.post(
        f"/theater/cart/items/{movie.id}/",
        headers=auth_headers
    )
    # Remove movie
    response = await client.delete(
        f"/theater/cart/items/{movie.id}/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_clear_cart(
    client: AsyncClient,
    auth_headers,
    movie: MovieModel,
    db_session: AsyncSession
):
    """Test clearing the cart."""
    # Add multiple movies
    movie2 = MovieModel(
        name="Test Movie 2",
        date=datetime(2024, 1, 2).date(),
        score=90.0,
        overview="Test overview 2",
        status=MovieStatusEnum.RELEASED,
        budget=2000000,
        revenue=4000000
    )
    db_session.add(movie2)
    await db_session.commit()
    await db_session.refresh(movie2)

    await client.post(
        f"/theater/cart/items/{movie.id}/",
        headers=auth_headers
    )
    await client.post(
        f"/theater/cart/items/{movie2.id}/",
        headers=auth_headers
    )

    # Clear cart
    response = await client.delete(
        "/theater/cart/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0 