import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.shopping_cart import Cart, CartItem
from database.models.movies import MovieModel, CountryModel, MovieStatusEnum
from database.models.accounts import UserModel, UserGroupModel, UserGroupEnum
from database.models.base import Base


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
def user(session, user_group):
    user = UserModel.create(
        email="test@example.com",
        raw_password="TestPassword1!",
        group_id=user_group.id
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def country(session):
    country = CountryModel(code="USA", name="United States")
    session.add(country)
    session.commit()
    return country


@pytest.fixture
def movie(session, country):
    movie = MovieModel(
        name="Test Movie",
        date=datetime(2024, 1, 1).date(),
        overview="Test Description",
        score=8.5,
        status=MovieStatusEnum.RELEASED,
        budget=1000000.0,
        revenue=2000000.0,
        country_id=country.id
    )
    session.add(movie)
    session.commit()
    return movie


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
