# type: ignore
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.shopping_cart import Cart, CartItem
from database.models.movies import MovieModel, CertificationModel, CertificationEnum
from database.models.accounts import UserModel, UserGroupModel, UserGroupEnum
from database.models.base import Base
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import client, db_session, seed_user_groups
from decimal import Decimal


@pytest.fixture
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user_group(session):
    group = UserGroupModel(name=UserGroupEnum.USER)
    session.add(group)
    session.commit()
    return group


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
def country(session):
    country = type('Country', (), {'id': 1, 'code': 'USA', 'name': 'United States'})()
    return country


@pytest.fixture
async def certification(db_session: AsyncSession):
    """Create a test certification."""
    certification = CertificationModel(name=CertificationEnum.PARENTAL_GUIDANCE_SUGGESTED)
    db_session.add(certification)
    await db_session.commit()
    await db_session.refresh(certification)
    return certification


@pytest.fixture
async def movie(db_session: AsyncSession, certification):
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
        price=Decimal("100.00"),
        certification_id=certification.id
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)
    return movie


@pytest.fixture
async def auth_headers(client: AsyncClient, user: UserModel):
    """Get authentication headers for the test user."""
    response = await client.post(
        "/api/v1/accounts/login/",
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
    response = await client.get("/api/v1/cart/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] is not None
    assert data["items"] == []


@pytest.mark.asyncio
async def test_add_movie_to_cart(client: AsyncClient, auth_headers, movie: MovieModel):
    """Test adding a movie to cart."""
    # Clear cart first
    await client.delete("/api/v1/cart/clear", headers=auth_headers)
    
    response = await client.post(
        f"/api/v1/cart/add/{movie.id}",
        headers=auth_headers
    )
    if response.status_code != 200:
        print(f"Error response: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert len(data["items"]) == 1
    assert data["items"][0]["movie_id"] == movie.id


@pytest.mark.asyncio
async def test_add_nonexistent_movie_to_cart(client: AsyncClient, auth_headers):
    """Test adding a nonexistent movie to cart."""
    response = await client.post(
        "/api/v1/cart/add/999",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "Movie with id 999 not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_duplicate_movie_to_cart(
    client: AsyncClient,
    auth_headers,
    movie: MovieModel
):
    """Test adding a movie that's already in cart."""
    # Add movie first time
    await client.post(
        f"/api/v1/cart/add/{movie.id}",
        headers=auth_headers
    )
    # Try to add the same movie again
    response = await client.post(
        f"/api/v1/cart/add/{movie.id}",
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
        f"/api/v1/cart/add/{movie.id}",
        headers=auth_headers
    )
    # Remove movie
    response = await client.delete(
        f"/api/v1/cart/remove/{movie.id}",
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
    db_session: AsyncSession,
    certification: CertificationModel
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
        price=Decimal("150.00"),
        certification_id=certification.id
    )
    db_session.add(movie2)
    await db_session.commit()
    await db_session.refresh(movie2)

    # Add movies to cart
    await client.post(
        f"/api/v1/cart/add/{movie.id}",
        headers=auth_headers
    )
    await client.post(
        f"/api/v1/cart/add/{movie2.id}",
        headers=auth_headers
    )

    # Clear cart
    response = await client.delete(
        "/api/v1/cart/clear",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
