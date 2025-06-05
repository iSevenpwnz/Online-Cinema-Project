import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models.cart import Cart, CartItem
from src.database.models.movies import MovieModel
from src.database.models.accounts import UserModel
from src.database.models.base import Base

# Test database setup
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
    """Creates a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def user(session):
    user = UserModel(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password"
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def movie(session):
    movie = MovieModel(
        title="Test Movie",
        description="Test Description",
        release_year=2024,
        duration=120,
        rating=8.5
    )
    session.add(movie)
    session.commit()
    return movie

class TestCart:
    def test_create_cart(self, session, user):
        """Test basic cart creation"""
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        assert cart.id is not None
        assert cart.user_id == user.id
        assert len(cart.items) == 0

    def test_cart_repr(self, session, user):
        """Test cart string representation"""
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        assert repr(cart) == f"<Cart(user_id={user.id})>"

    def test_cart_unique_user(self, session, user):
        """Test that a user can only have one cart"""
        cart1 = Cart(user_id=user.id)
        session.add(cart1)
        session.commit()

        cart2 = Cart(user_id=user.id)
        session.add(cart2)
        
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            session.commit()

    def test_cart_items_relationship(self, session, user, movie):
        """Test relationship between cart and cart items"""
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
        """Test that cart items are deleted when cart is deleted"""
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        cart_item = CartItem(cart_id=cart.id, movie_id=movie.id)
        session.add(cart_item)
        session.commit()

        # Delete the cart
        session.delete(cart)
        session.commit()

        # Verify cart item is also deleted
        assert session.query(CartItem).filter_by(id=cart_item.id).first() is None

    def test_cart_with_multiple_items(self, session, user):
        """Test cart with multiple items"""
        cart = Cart(user_id=user.id)
        session.add(cart)
        session.commit()

        # Create multiple movies
        movies = []
        for i in range(3):
            movie = MovieModel(
                title=f"Test Movie {i}",
                description=f"Test Description {i}",
                release_year=2024,
                duration=120,
                rating=8.5
            )
            session.add(movie)
            movies.append(movie)
        session.commit()

        # Add all movies to cart
        for movie in movies:
            cart_item = CartItem(cart_id=cart.id, movie_id=movie.id)
            session.add(cart_item)
        session.commit()

        assert len(cart.items) == 3
        assert all(isinstance(item, CartItem) for item in cart.items)
        assert all(item.cart_id == cart.id for item in cart.items) 