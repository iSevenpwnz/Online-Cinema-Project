import datetime
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
from database.models.orders import Order, OrderStatusEnum, OrderItem
from database.models.payments import (
    PaymentModel,
    PaymentStatusEnum,
    PaymentItemModel,
)
from database.models.movies import MovieModel
from database.models.accounts import UserGroupEnum, UserGroupModel, UserModel


@pytest.fixture
async def payment_with_items(
    db_session: AsyncSession,
    seed_user_groups: Any,
    seed_active_user: UserModel,
) -> PaymentModel:
    # Create a movie
    movie = MovieModel(
        uuid="uuid-10",
        name="Retrieve Test Movie",
        year=2024,
        time=120,
        imdb=8.0,
        votes=1000,
        meta_score=90.0,
        gross=1000000.0,
        description="A test movie for payment retrieval.",
        price=19.99,
        certification_id=1,
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    # Create an order
    order = Order(
        user_id=seed_active_user.id,
        created_at=datetime.date(2025, 6, 6),
        status=OrderStatusEnum.PAID,
        total_amount=19.99,
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        movie_id=movie.id,
        price_at_order=19.99,
    )
    db_session.add(order_item)
    await db_session.commit()
    await db_session.refresh(order_item)

    # Create payment
    payment = PaymentModel(
        user_id=order.user_id,
        order_id=order.id,
        status=PaymentStatusEnum.SUCCESSFUL,
        external_payment_id="pi_test_retrieve",
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)

    # Create payment item
    payment_item = PaymentItemModel(
        payment_id=payment.id,
        order_item_id=order_item.id,
        price_at_payment=19.99,
    )
    db_session.add(payment_item)
    await db_session.commit()
    await db_session.refresh(payment_item)

    return payment


@pytest.fixture
async def more_payments(
    db_session: AsyncSession,
    seed_user_groups: Any,
    seed_active_user: UserModel,
) -> List[PaymentModel]:
    payments: List[PaymentModel] = []
    for i in range(3):
        movie = MovieModel(
            uuid=f"uuid-{20+i}",
            name=f"Movie {i}",
            year=2024,
            time=90 + i * 10,
            imdb=7.0 + i,
            votes=100 * (i + 1),
            meta_score=70.0 + i * 5,
            gross=100000.0 * (i + 1),
            description=f"Movie {i} for payment testing.",
            price=10.0 + i,
            certification_id=1,
        )
        db_session.add(movie)
        await db_session.flush()
        order = Order(
            user_id=seed_active_user.id,
            created_at=datetime.date(2025, 6, 10 + i),
            status=OrderStatusEnum.PAID,
            total_amount=movie.price,
        )
        db_session.add(order)
        await db_session.flush()
        order_item = OrderItem(
            order_id=order.id,
            movie_id=movie.id,
            price_at_order=movie.price,
        )
        db_session.add(order_item)
        await db_session.flush()
        payment = PaymentModel(
            user_id=order.user_id,
            order_id=order.id,
            status=PaymentStatusEnum.SUCCESSFUL,
            external_payment_id=f"pi_test_{i}",
        )
        db_session.add(payment)
        await db_session.flush()
        payment_item = PaymentItemModel(
            payment_id=payment.id,
            order_item_id=order_item.id,
            price_at_payment=movie.price,
        )
        db_session.add(payment_item)
        await db_session.flush()
        payments.append(payment)
    await db_session.commit()
    return payments


@pytest.mark.asyncio
async def test_get_payments_returns_paginated(
    client: AsyncClient,
    payment_with_items: PaymentModel,
    seed_user_groups,
    seed_active_user: UserModel,
):
    # Login to get token
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    assert login_resp.status_code == 201
    token = login_resp.json()["access_token"]

    # Call payments endpoint
    resp = await client.get(
        "/api/v1/payments/?page=1&per_page=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert data["total_results"] >= 1
    found = any(p["id"] == payment_with_items.id for p in data["results"])
    assert found
    # Check nested fields
    payment = next(
        p for p in data["results"] if p["id"] == payment_with_items.id
    )
    assert payment["order"]["id"] == payment_with_items.order_id
    assert payment["status"] == PaymentStatusEnum.SUCCESSFUL
    assert payment["external_payment_id"] == "pi_test_retrieve"
    assert len(payment["payment_items"]) == 1
    assert (
        payment["payment_items"][0]["order_item"]["movie"]["name"]
        == "Retrieve Test Movie"
    )


@pytest.mark.asyncio
async def test_get_payments_filters_by_status(
    client: AsyncClient,
    payment_with_items: PaymentModel,
    seed_active_user: UserModel,
):
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    # Should return payment when status matches
    resp = await client.get(
        f"/api/v1/payments/?status=successful&page=1&per_page=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any(p["id"] == payment_with_items.id for p in data["results"])
    # Should not return payment when status does not match
    resp = await client.get(
        f"/api/v1/payments/?status=refunded&page=1&per_page=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not any(p["id"] == payment_with_items.id for p in data["results"])


@pytest.mark.asyncio
async def test_get_payments_pagination(
    client: AsyncClient,
    payment_with_items: PaymentModel,
    seed_user_groups,
    seed_active_user: UserModel,
    db_session: AsyncSession,
):
    # Add a second payment for pagination
    movie2 = MovieModel(
        uuid="uuid-11",
        name="Second Movie",
        year=2024,
        time=100,
        imdb=7.0,
        votes=500,
        meta_score=80.0,
        gross=500000.0,
        description="Second test movie.",
        price=9.99,
        certification_id=1,
    )
    db_session.add(movie2)
    await db_session.commit()
    await db_session.refresh(movie2)
    order2 = Order(
        user_id=seed_active_user.id,
        created_at=datetime.date(2025, 6, 7),
        status=OrderStatusEnum.PAID,
        total_amount=9.99,
    )
    db_session.add(order2)
    await db_session.commit()
    await db_session.refresh(order2)
    order_item2 = OrderItem(
        order_id=order2.id,
        movie_id=movie2.id,
        price_at_order=9.99,
    )
    db_session.add(order_item2)
    await db_session.commit()
    await db_session.refresh(order_item2)
    payment2 = PaymentModel(
        user_id=order2.user_id,
        order_id=order2.id,
        status=PaymentStatusEnum.SUCCESSFUL,
        external_payment_id="pi_test_2",
    )
    db_session.add(payment2)
    await db_session.commit()
    await db_session.refresh(payment2)
    payment_item2 = PaymentItemModel(
        payment_id=payment2.id,
        order_item_id=order_item2.id,
        price_at_payment=9.99,
    )
    db_session.add(payment_item2)
    await db_session.commit()
    await db_session.refresh(payment_item2)

    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    # page=1, per_page=1 should only return one result
    resp = await client.get(
        "/api/v1/payments/?page=1&per_page=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_results"] >= 2
    assert len(data["results"]) == 1
    # page=2, per_page=1 should return the other result
    resp = await client.get(
        "/api/v1/payments/?page=2&per_page=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data2 = resp.json()
    assert len(data2["results"]) == 1
    assert data["results"][0]["id"] != data2["results"][0]["id"]


@pytest.mark.asyncio
async def test_admin_can_see_all_payments(
    client: AsyncClient,
    payment_with_items: PaymentModel,
    more_payments: List[PaymentModel],
    seed_user_groups: Any,
    db_session: AsyncSession,
):
    # Create admin user
    admin_user = UserModel.create(
        email="admin@email.com",
        raw_password="AdminP@ssword1",
        group_id=(
            await db_session.scalar(
                select(UserGroupModel).where(
                    UserGroupModel.name == UserGroupEnum.ADMIN
                )
            )
        ).id,
    )
    admin_user.is_active = True
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)
    login_payload = {"email": admin_user.email, "password": "AdminP@ssword1"}
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    resp = await client.get(
        "/api/v1/payments/?page=1&per_page=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Admin should see all payments
    assert data["total_results"] >= 4


@pytest.mark.asyncio
async def test_user_sees_only_own_payments(
    client: AsyncClient,
    payment_with_items: PaymentModel,
    more_payments: List[PaymentModel],
    seed_user_groups: Any,
    seed_active_user: UserModel,
):
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    resp = await client.get(
        "/api/v1/payments/?page=1&per_page=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # All payments should belong to this user
    for p in data["results"]:
        assert p["user"]["id"] == seed_active_user.id


@pytest.mark.asyncio
async def test_payments_filter_by_from_date_and_to_date(
    client: AsyncClient,
    payment_with_items: PaymentModel,
    more_payments: List[PaymentModel],
    seed_user_groups: Any,
    seed_active_user: UserModel,
):
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    # from_date filter (should only get payments after 2025-06-11)
    resp = await client.get(
        "/api/v1/payments/?from_date=2025-06-11&page=1&per_page=50",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, f"Bad response status code: {resp.status_code}. Message: {resp.json()}"
    data = resp.json()
    for p in data["results"]:
        assert p["created_at"][:10] >= "2025-06-11"
    # to_date filter (should only get payments before 2025-06-11)
    resp = await client.get(
        "/api/v1/payments/?to_date=2025-06-11&page=1&per_page=50",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    for p in data["results"]:
        assert p["created_at"][:10] <= "2025-06-11"
