import pytest
from datetime import date
from decimal import Decimal
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.accounts import UserModel, UserGroupEnum
from database.models.movies import MovieModel, CertificationModel, CertificationEnum
from database.models.shopping_cart import Cart, CartItem
from database.models.orders import Order, OrderItem, OrderStatusEnum


@pytest.fixture
async def user(db_session: AsyncSession, seed_user_groups):
    user = UserModel.create(
        email="orderuser@example.com",
        raw_password="OrderPassword1!",
        group_id=1  # Припускаємо, що це юзерська група (не admin)
    )
    user.is_active = True
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def certification(db_session: AsyncSession):
    cert = CertificationModel(name=CertificationEnum.PARENTAL_GUIDANCE_SUGGESTED)
    db_session.add(cert)
    await db_session.commit()
    await db_session.refresh(cert)
    return cert


@pytest.fixture
async def movie(db_session: AsyncSession, certification):
    movie = MovieModel(
        uuid="movie-uuid-test",
        name="Order Test Movie",
        year=2024,
        time=120,
        imdb=7.8,
        votes=500,
        meta_score=75.0,
        gross=50000.0,
        description="Test movie description",
        price=Decimal("150.00"),
        certification_id=certification.id,
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)
    return movie


@pytest.fixture
async def cart_with_items(db_session: AsyncSession, user: UserModel, movie: MovieModel):
    cart = Cart(user_id=user.id)
    db_session.add(cart)
    await db_session.commit()
    await db_session.refresh(cart)

    item = CartItem(cart_id=cart.id, movie_id=movie.id)
    db_session.add(item)
    await db_session.commit()
    return cart


@pytest.fixture
async def auth_headers(client: AsyncClient, user: UserModel):
    response = await client.post(
        "/api/v1/accounts/login/",
        json={"email": user.email, "password": "OrderPassword1!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_order_from_cart_success(client: AsyncClient, auth_headers: dict, cart_with_items: Cart, db_session: AsyncSession):
    response = await client.post("/api/v1/orders/create-from-cart", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == OrderStatusEnum.PENDING.value
    assert data["total_amount"] == "150.00"
    assert len(data["items"]) == 1

    # Перевіряємо, що кошик очищено
    result = await db_session.execute(select(CartItem).where(CartItem.cart_id == cart_with_items.id))
    items = result.scalars().all()
    assert len(items) == 0


@pytest.mark.asyncio
async def test_create_order_from_cart_empty_cart(client: AsyncClient, auth_headers: dict):
    response = await client.post("/api/v1/orders/create-from-cart", headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cart is empty" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_order_history_no_filter(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, user: UserModel, movie: MovieModel):
    order = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.PAID,
        total_amount=Decimal("100.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("100.00"))],
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    response = await client.get("/api/v1/orders/history", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(o["id"] == order.id for o in data)


@pytest.mark.asyncio
async def test_get_order_history_with_filter(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, user: UserModel, movie: MovieModel):
    order1 = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.PENDING,
        total_amount=Decimal("100.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("100.00"))],
    )
    order2 = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.PAID,
        total_amount=Decimal("150.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("150.00"))],
    )
    db_session.add_all([order1, order2])
    await db_session.commit()

    response = await client.get("/api/v1/orders/history?status=Pending", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(order["status"] == OrderStatusEnum.PENDING.value for order in data)


@pytest.mark.asyncio
async def test_get_order_history_invalid_status_filter(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/orders/history?status=INVALID", headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid status values" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_order_by_id_success(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, user: UserModel, movie: MovieModel):
    order = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.PENDING,
        total_amount=Decimal("120.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("120.00"))],
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    response = await client.get(f"/api/v1/orders/{order.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == order.id


@pytest.mark.asyncio
async def test_get_order_by_id_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/orders/999999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_order_status_success(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, user: UserModel, movie: MovieModel):
    order = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.PENDING,
        total_amount=Decimal("200.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("200.00"))],
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    # Користувач не admin, може скасувати
    response = await client.patch(f"/api/v1/orders/{order.id}/status?new_status=Canceled", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == OrderStatusEnum.CANCELED.value


@pytest.mark.asyncio
async def test_change_order_status_invalid_transition(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, user: UserModel, movie: MovieModel):
    order = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.PAID,
        total_amount=Decimal("250.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("250.00"))],
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    # Користувач не admin, спроба змінити статус не на CANCELED
    response = await client.patch(f"/api/v1/orders/{order.id}/status?new_status=Pending", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_change_order_status_from_canceled(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, user: UserModel, movie: MovieModel):
    order = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.CANCELED,
        total_amount=Decimal("180.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("180.00"))],
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    response = await client.patch(
        f"/api/v1/orders/{order.id}/status?new_status=Paid",
        headers=auth_headers
    )
    assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST)
    detail = response.json().get("detail", "").lower()
    assert (
        "cannot change status" in detail
        or "not allowed" in detail
        or "you can only cancel your order" in detail
    )


@pytest.mark.asyncio
async def test_change_order_status_invalid_status(client: AsyncClient, auth_headers: dict):
    response = await client.patch("/api/v1/orders/1/status?new_status=INVALID", headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid status value" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_order_status_bad_param_format(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, user: UserModel, movie: MovieModel):
    order = Order(
        user_id=user.id,
        created_at=date.today(),
        status=OrderStatusEnum.PENDING,
        total_amount=Decimal("100.00"),
        order_items=[OrderItem(movie_id=movie.id, price_at_order=Decimal("100.00"))],
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    response = await client.patch(f"/api/v1/orders/{order.id}/status?new_status=12345", headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid status value" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_order_status_order_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.patch("/api/v1/orders/999999/status?new_status=Paid", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()
