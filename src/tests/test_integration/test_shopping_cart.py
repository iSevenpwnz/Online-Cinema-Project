# type: ignore
import pytest
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from database.models.shopping_cart import Cart, CartItem
from database.models.movies import (
    MovieModel,
    CertificationEnum,
    CertificationModel,
)
from database.models.accounts import UserModel, UserGroupModel, UserGroupEnum
from database.models.base import Base
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.conftest import client, db_session, seed_user_groups
from decimal import Decimal
from typing import Any
import uuid


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
        uuid=uuid.uuid4(),
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
    response = await client.get("/api/v1/shopping-cart/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []


@pytest.mark.asyncio
async def test_add_movie_to_cart(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession, movie: MovieModel
):
    """Test adding a movie to cart."""
    response = await client.post(
        f"/api/v1/shopping-cart/add/{movie.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["movie"]["id"] == movie.id


@pytest.mark.asyncio
async def test_add_nonexistent_movie_to_cart(client: AsyncClient, auth_headers: dict):
    """Test adding a nonexistent movie to cart."""
    response = await client.post(
        "/api/v1/shopping-cart/add/999999", headers=auth_headers
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_duplicate_movie_to_cart(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession, movie: MovieModel
):
    """Test adding a movie that's already in cart."""
    # First add
    await client.post(f"/api/v1/shopping-cart/add/{movie.id}", headers=auth_headers)
    # Try to add again
    response = await client.post(
        f"/api/v1/shopping-cart/add/{movie.id}", headers=auth_headers
    )
    assert response.status_code == 400
    assert "already in cart" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_remove_movie_from_cart(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession, movie: MovieModel
):
    """Test removing a movie from cart."""
    # First add
    await client.post(f"/api/v1/shopping-cart/add/{movie.id}", headers=auth_headers)
    # Then remove
    response = await client.delete(
        f"/api/v1/shopping-cart/remove/{movie.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_clear_cart(
    client: AsyncClient, auth_headers: dict, db_session: AsyncSession, movie: MovieModel
):
    """Test clearing the cart."""
    # First add a movie
    await client.post(f"/api/v1/shopping-cart/add/{movie.id}", headers=auth_headers)
    # Then clear
    response = await client.delete("/api/v1/shopping-cart/clear", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_admin_view_user_cart(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
):
    """Test admin viewing another user's cart."""
    # Create admin user
    admin = UserModel.create(
        email="admin@example.com",
        raw_password="AdminPass123!",
        group_id=3  # Admin group
    )
    admin.is_active = True
    db_session.add(admin)
    
    # Create regular user
    user = UserModel.create(
        email="user@example.com",
        raw_password="UserPass123!",
        group_id=1  # User group
    )
    user.is_active = True
    db_session.add(user)
    
    # Create certification
    certification = CertificationModel(name="G")
    db_session.add(certification)
    await db_session.commit()
    
    # Create a movie
    movie = MovieModel(
        uuid=uuid.uuid4(),
        name="Test Movie",
        year=2024,
        time=120,
        imdb=8.5,
        votes=1000,
        description="Test Description",
        price=Decimal("10.00"),
        certification_id=certification.id
    )
    db_session.add(movie)
    
    await db_session.commit()
    
    # Create cart for regular user and add movie
    cart = Cart(user_id=user.id)
    db_session.add(cart)
    await db_session.commit()
    await db_session.refresh(cart)
    
    cart_item = CartItem(cart_id=cart.id, movie_id=movie.id)
    db_session.add(cart_item)
    await db_session.commit()
    
    # Get admin token
    admin_token = jwt_manager.create_access_token({"user_id": admin.id})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin views user's cart
    response = await client.get(
        f"/api/v1/shopping-cart/users/{user.id}",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["movie"]["id"] == movie.id


@pytest.mark.asyncio
async def test_regular_user_cannot_view_other_cart(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
):
    """Test that regular users cannot view other users' carts."""
    # Create two regular users
    user1 = UserModel.create(
        email="user1@example.com",
        raw_password="User1Pass123!",
        group_id=1  # User group
    )
    user1.is_active = True
    db_session.add(user1)
    
    user2 = UserModel.create(
        email="user2@example.com",
        raw_password="User2Pass123!",
        group_id=1  # User group
    )
    user2.is_active = True
    db_session.add(user2)
    
    await db_session.commit()
    
    # Get user1's token
    user1_token = jwt_manager.create_access_token({"user_id": user1.id})
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    
    # User1 tries to view user2's cart
    response = await client.get(
        f"/api/v1/shopping-cart/users/{user2.id}",
        headers=user1_headers
    )
    assert response.status_code == 403
    assert "only administrators" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_view_nonexistent_user_cart(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
):
    """Test admin viewing cart of nonexistent user."""
    # Create admin user
    admin = UserModel.create(
        email="admin@example.com",
        raw_password="AdminPass123!",
        group_id=3  # Admin group
    )
    admin.is_active = True
    db_session.add(admin)
    await db_session.commit()
    
    # Get admin token
    admin_token = jwt_manager.create_access_token({"user_id": admin.id})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Admin tries to view nonexistent user's cart
    response = await client.get(
        "/api/v1/shopping-cart/users/999999",
        headers=admin_headers
    )
    assert response.status_code == 404
    assert "user not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_check_movie_in_carts_when_present(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
    movie: MovieModel
):
    """Test checking if movie is in any cart when it is present."""
    # Create admin user
    admin = UserModel.create(
        email="admin@example.com",
        raw_password="AdminPass123!",
        group_id=3  # Admin group
    )
    admin.is_active = True
    db_session.add(admin)
    await db_session.commit()

    # Get admin auth token
    response = await client.post(
        "/api/v1/accounts/login/",
        json={
            "email": admin.email,
            "password": "AdminPass123!"
        }
    )
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Add movie to cart
    await client.post(f"/api/v1/shopping-cart/add/{movie.id}", headers=admin_headers)

    # Check movie presence
    response = await client.get(
        f"/api/v1/shopping-cart/check-movie/{movie.id}",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_in_cart"] is True


@pytest.mark.asyncio
async def test_check_movie_in_carts_when_not_present(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
    movie: MovieModel
):
    """Test checking if movie is in any cart when it is not present."""
    # Create admin user
    admin = UserModel.create(
        email="admin@example.com",
        raw_password="AdminPass123!",
        group_id=3  # Admin group
    )
    admin.is_active = True
    db_session.add(admin)
    await db_session.commit()

    # Get admin auth token
    response = await client.post(
        "/api/v1/accounts/login/",
        json={
            "email": admin.email,
            "password": "AdminPass123!"
        }
    )
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = await client.get(
        f"/api/v1/shopping-cart/check-movie/{movie.id}",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_in_cart"] is False


@pytest.mark.asyncio
async def test_check_movie_in_carts_unauthorized(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
    movie: MovieModel
):
    """Test checking if movie is in any cart without admin rights."""
    # Create regular user
    user = UserModel.create(
        email="user@example.com",
        raw_password="UserPass123!",
        group_id=1  # User group
    )
    user.is_active = True
    db_session.add(user)
    await db_session.commit()

    # Get auth token for regular user
    response = await client.post(
        "/api/v1/accounts/login/",
        json={
            "email": user.email,
            "password": "UserPass123!"
        }
    )
    user_token = response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Try to check movie presence
    response = await client.get(
        f"/api/v1/shopping-cart/check-movie/{movie.id}",
        headers=user_headers
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Only administrators can check movie presence in carts."


@pytest.mark.asyncio
async def test_check_movie_in_carts_with_multiple_carts(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
    movie: MovieModel
):
    """Test checking if movie is in any cart when it is present in multiple carts."""
    # Create admin user
    admin = UserModel.create(
        email="admin@example.com",
        raw_password="AdminPass123!",
        group_id=3  # Admin group
    )
    admin.is_active = True
    db_session.add(admin)
    
    # Create regular user
    user = UserModel.create(
        email="user@example.com",
        raw_password="UserPass123!",
        group_id=1  # User group
    )
    user.is_active = True
    db_session.add(user)
    await db_session.commit()

    # Get auth tokens
    admin_response = await client.post(
        "/api/v1/accounts/login/",
        json={
            "email": admin.email,
            "password": "AdminPass123!"
        }
    )
    admin_token = admin_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    user_response = await client.post(
        "/api/v1/accounts/login/",
        json={
            "email": user.email,
            "password": "UserPass123!"
        }
    )
    user_token = user_response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Add movie to both users' carts
    await client.post(f"/api/v1/shopping-cart/add/{movie.id}", headers=admin_headers)
    await client.post(f"/api/v1/shopping-cart/add/{movie.id}", headers=user_headers)

    # Check movie presence as admin
    response = await client.get(
        f"/api/v1/shopping-cart/check-movie/{movie.id}",
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_in_cart"] is True


@pytest.mark.asyncio
async def test_add_movie_to_cart_unverified_user(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    jwt_manager: Any,
    movie: MovieModel
):
    """Test adding movie to cart with inactive user."""
    # Create inactive user
    user = UserModel.create(
        email="inactive@example.com",
        raw_password="TestPass123!",
        group_id=1
    )
    user.is_active = False  # Explicitly set as inactive
    db_session.add(user)
    await db_session.commit()

    # Try to login with inactive user
    response = await client.post(
        "/api/v1/accounts/login/",
        json={
            "email": user.email,
            "password": "TestPass123!"
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "User account is not activated."
