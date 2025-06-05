import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.shopping_cart import Cart, CartItem
from database.models.movies import MovieModel, CountryModel, MovieStatusEnum
from database.models.accounts import UserModel, UserGroupModel, UserGroupEnum
from database.models.base import Base
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import client, db_session, seed_user_groups


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
    country = CountryModel(code="USA", name="United States")
    session.add(country)
    session.commit()
    return country


@pytest.fixture
async def movie(db_session: AsyncSession, country):
    """Create a test movie."""
    movie = MovieModel(
        name="Test Movie",
        date=datetime(2024, 1, 1).date(),
        score=85.5,
        overview="Test overview",
        status=MovieStatusEnum.RELEASED,
        budget=1000000,
        revenue=2000000,
        country_id=country.id
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


class TestCart:
    def test_create_cart(self, session, user):
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        assert cart.id is not None
        assert cart.user_id == user.id
        assert len(cart.items) == 0

    def test_cart_repr(self, session, user):
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        assert repr(cart) == f"<Cart(user_id={user.id})>"

    def test_cart_unique_user(self, session, user):
        cart1 = Cart(user_id=user.id)
        session.add(cart1)
        session.commit()

        cart2 = Cart(user_id=user.id)
        session.add(cart2)

        with pytest.raises(Exception):
            session.commit()

    def test_cart_items_relationship(self, session, user, movie):
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        cart_item = CartItem(cart_id=cart.id, movie_id=movie.id)
        session.add(cart_item)
        session.commit()

        assert len(cart.items) == 1
        assert cart.items[0] == cart_item
        assert cart_item.cart == cart

    def test_cart_cascade_delete(self, session, user, movie):
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        cart_item = CartItem(cart_id=cart.id, movie_id=movie.id)
        session.add(cart_item)
        session.commit()

        session.delete(cart)
        session.commit()

        assert session.query(CartItem).filter_by(id=cart_item.id).first() is None

    def test_cart_with_multiple_items(self, session, user, country):
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        movies = []
        for i in range(3):
            movie = MovieModel(
                name=f"Test Movie {i}",
                date=datetime(2024, 1, 1).date(),
                overview=f"Test Description {i}",
                score=8.5,
                status=MovieStatusEnum.RELEASED,
                budget=1000000.0,
                revenue=2000000.0,
                country_id=country.id
            )
            session.add(movie)
            movies.append(movie)
        session.commit()

        for movie in movies:
            cart_item = CartItem(cart_id=cart.id, movie_id=movie.id)
            session.add(cart_item)
        session.commit()

        assert len(cart.items) == 3
        assert all(isinstance(item, CartItem) for item in cart.items)
        assert all(item.cart_id == cart.id for item in cart.items)


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
    response = await client.post(
        f"/api/v1/cart/add/{movie.id}",
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
        "/api/v1/cart/add/999",
        headers=auth_headers
    )
    assert response.status_code == 400
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
        revenue=4000000,
        country_id=movie.country_id
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
