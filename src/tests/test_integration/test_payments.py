import datetime
from unittest.mock import patch
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.orders import Order, OrderStatusEnum, OrderItem
from database.models.movies import MovieModel
from database.models.accounts import UserModel
from database.models.payments import PaymentModel
from services.payments.payments import PaymentService, PaymentServicesEnum
from typing import Any, Tuple


class MockStripePaymentService(PaymentService):
    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def validate_payment_method(cls, payment_method: str) -> None:
        return

    async def create_payment_session(self, order: Order) -> str:
        return "http://test_session.com"

    async def handle_event(self) -> PaymentModel | None:
        raise NotImplementedError


@pytest.fixture
async def payment_test_movie(db_session: AsyncSession) -> MovieModel:
    movie = MovieModel(
        uuid="uuid-2",
        name="Payment Test Movie",
        year=2024,
        time=100,
        imdb=7.5,
        votes=500,
        meta_score=80.0,
        gross=500000.0,
        description="A payment test movie.",
        price=9.99,
        certification_id=1,
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)
    return movie


@pytest.fixture
async def payment_test_order_item(
    db_session: AsyncSession, payment_test_movie: MovieModel, seed_active_user: UserModel
) -> Tuple[Order, OrderItem]:
    order = Order(
        user_id=seed_active_user.id,
        created_at=datetime.date(2025, 6, 6),
        status=OrderStatusEnum.PENDING,
        total_amount=9.99,
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    order_item = OrderItem(
        order_id=order.id,
        movie_id=payment_test_movie.id,
        price_at_order=9.99,
    )
    db_session.add(order_item)
    await db_session.commit()
    await db_session.refresh(order_item)
    return order, order_item


@pytest.mark.asyncio
@patch("schemas.payments.get_payment_service", MockStripePaymentService)
async def test_create_payment_session_success(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    seed_active_user: UserModel,
    payment_test_order_item: Tuple[Order, OrderItem],
) -> None:

    order, _ = payment_test_order_item

    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    assert login_resp.status_code == 201
    token = login_resp.json()["access_token"]

    # Call payment session endpoint
    payload = {
        "order_id": order.id,
        "payment_service": PaymentServicesEnum.STRIPE.value,
        "payment_method": "card",
    }

    with patch(
        "routes.payments.get_payment_service",
        return_value=MockStripePaymentService,
    ):
        resp = await client.post(
            "/api/v1/payments/payment-session",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        print("response dasd", resp.json())
        assert resp.status_code == 200
        assert "session_url" in resp.json()


@pytest.mark.asyncio
@patch("schemas.payments.get_payment_service", MockStripePaymentService)
async def test_create_payment_session_order_not_found(
    client: AsyncClient,
    seed_user_groups: Any,
    seed_active_user: UserModel,
) -> None:
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    payload = {
        "order_id": 99999,
        "payment_service": PaymentServicesEnum.STRIPE.value,
        "payment_method": "card",
    }
    resp = await client.post(
        "/api/v1/payments/payment-session",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
@patch("schemas.payments.get_payment_service", MockStripePaymentService)
async def test_create_payment_session_unauthorized(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    seed_active_user: UserModel,
    payment_test_movie: MovieModel,
    payment_test_order_item: Tuple[Order, OrderItem],
) -> None:
    # Create a second user
    user2 = UserModel.create(
        email="other@email.com",
        raw_password="StrongP@ssword1",
        group_id=seed_active_user.group_id,
    )
    user2.is_active = True
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    # Create a movie and order for user2
    order, _ = payment_test_order_item

    order.user_id = user2.id
    await db_session.commit()

    # Login as first user
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    payload = {
        "order_id": order.id,
        "payment_service": PaymentServicesEnum.STRIPE.value,
        "payment_method": "card",
    }
    resp = await client.post(
        "/api/v1/payments/payment-session",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert "not authorized" in resp.json()["detail"].lower()


@pytest.mark.asyncio
@patch("schemas.payments.get_payment_service", MockStripePaymentService)
async def test_create_payment_session_not_pending(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    seed_active_user: UserModel,
    payment_test_order_item: Tuple[Order, OrderItem],
) -> None:
    order, _ = payment_test_order_item

    order.status = OrderStatusEnum.PAID
    await db_session.commit()

    # Login
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    payload = {
        "order_id": order.id,
        "payment_service": PaymentServicesEnum.STRIPE.value,
        "payment_method": "card",
    }
    resp = await client.post(
        "/api/v1/payments/payment-session",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409
    assert "does not have status" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_payment_session_invalid_method(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: Any,
    seed_active_user: UserModel,
    payment_test_order_item: Tuple[Order, OrderItem],
) -> None:
    order, _ = payment_test_order_item

    invalid_payment_method = "invalid_payment_method"

    # Login
    login_payload = {
        "email": seed_active_user.email,
        "password": "StrongP@ssword1",
    }
    login_resp = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    token = login_resp.json()["access_token"]
    payload = {
        "order_id": order.id,
        "payment_service": PaymentServicesEnum.STRIPE.value,
        "payment_method": invalid_payment_method,
    }
    resp = await client.post(
        "/api/v1/payments/payment-session",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422

    assert (
        f"'{invalid_payment_method}' is not a supported payment method"
        in str(resp.text).lower()
    )
