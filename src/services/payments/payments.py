from abc import ABC, abstractmethod, abstractstaticmethod
import asyncio
from decimal import Decimal
from enum import Enum
from typing import Literal, Type, cast

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.dependencies import get_settings
from database.models.orders import Order, OrderStatusEnum
from config.settings import BaseAppSettings
from database.models.payments import (
    PaymentItemModel,
    PaymentModel,
    PaymentStatusEnum,
)

from starlette.concurrency import run_in_threadpool

import stripe
from typing import TypeAlias

StripePaymentMethod: TypeAlias = Literal[
    "acss_debit",
    "affirm",
    "afterpay_clearpay",
    "alipay",
    "alma",
    "amazon_pay",
    "au_becs_debit",
    "bacs_debit",
    "bancontact",
    "billie",
    "blik",
    "boleto",
    "card",
    "cashapp",
    "customer_balance",
    "eps",
    "fpx",
    "giropay",
    "grabpay",
    "ideal",
    "kakao_pay",
    "klarna",
    "konbini",
    "kr_card",
    "link",
    "mobilepay",
    "multibanco",
    "naver_pay",
    "oxxo",
    "p24",
    "pay_by_bank",
    "payco",
    "paynow",
    "paypal",
    "pix",
    "promptpay",
    "revolut_pay",
    "samsung_pay",
    "satispay",
    "sepa_debit",
    "sofort",
    "swish",
    "twint",
    "us_bank_account",
    "wechat_pay",
    "zip",
]


class PaymentService(ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @classmethod
    @abstractmethod
    def validate_payment_method(cls, payment_method: str) -> None:
        pass

    @abstractmethod
    async def create_payment_session(self, order: Order) -> str:
        pass

    @abstractmethod
    async def handle_event(
        self, request: Request, db: AsyncSession
    ) -> PaymentModel | None:
        pass


class StripePaymentService(PaymentService):
    AVAILABLE_PAYMENT_METHODS: list[StripePaymentMethod] = [
        "card",
    ]

    def __init__(
        self,
        settings: BaseAppSettings,
        payment_method: StripePaymentMethod | None,
    ) -> None:
        super().__init__()
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        if payment_method:
            self.payment_method: StripePaymentMethod = payment_method

    @classmethod
    def validate_payment_method(cls, payment_method: str):
        if payment_method not in cls.AVAILABLE_PAYMENT_METHODS:
            available_methods = ", ".join(cls.AVAILABLE_PAYMENT_METHODS)
            raise ValueError(
                f"'{payment_method}' is not a supported payment method. "
                f"Available methods are: {available_methods}."
            )

    def _create_payment_session(self, order: Order):
        line_items: list[stripe.checkout.Session.CreateParamsLineItem] = []
        for order_item in order.order_items:
            line_items.append(
                {
                    "price_data": {
                        "currency": "usd",  # TODO: get currency from .env
                        "product_data": {
                            "name": order_item.movie.name,
                            "metadata": {
                                "movie_id": str(order_item.movie.id),
                                "order_item_id": str(order_item.id),
                            },
                        },
                        "unit_amount": int(
                            cast(Decimal, order_item.price_at_order)
                            * Decimal("100")
                        ),
                    },
                    "quantity": 1,
                }
            )

        return stripe.checkout.Session.create(
            api_key=self.secret_key,
            payment_method_types=[self.payment_method],
            line_items=line_items,
            mode="payment",
            success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
            # TODO: add url builder function and SUCCESS url to .env
            cancel_url="https://yourdomain.com/cancel",  # TODO: add cancel url,
            metadata={"order_id": str(order.id)},
        )

    def _construct_stripe_event(
        self, payload: bytes, sig_header: str
    ) -> stripe.Event:
        event = stripe.Webhook.construct_event(
            payload, sig_header, self.webhook_secret
        )

        return event

    def _fetch_sessions_line_items(self, session: stripe.checkout.Session):
        line_items_response = stripe.checkout.Session.list_line_items(
            session["id"],
            api_key=self.secret_key,
        )

        return line_items_response

    def _fetch_order_item_id_from_line_item(self, line_item: stripe.LineItem):
        price = line_item.get("price", {})
        product = price.get("product")

        if product:
            product_obj = stripe.Product.retrieve(
                product, api_key=self.secret_key
            )
            order_item_id = int(
                product_obj.get("metadata", {}).get("order_item_id")
            )

        return order_item_id, price["unit_amount"]

    async def create_payment_session(self, order: Order) -> str:
        session = await run_in_threadpool(self._create_payment_session, order)
        return session.url

    async def handle_event(
        self, request: Request, db: AsyncSession
    ) -> PaymentModel | None:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if not payload or not sig_header:
            raise ValueError(
                "Invalid Stripe webhook: missing payload or Stripe signature header."
            )

        event = await run_in_threadpool(
            self._construct_stripe_event, payload, sig_header
        )

        payment = None

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            order_id = int(session["metadata"]["order_id"])
            line_items = await run_in_threadpool(
                self._fetch_sessions_line_items,
                session,
            )

            order_item_ids_and_amount = await asyncio.gather(
                *[
                    run_in_threadpool(
                        self._fetch_order_item_id_from_line_item, line_item
                    )
                    for line_item in line_items
                ]
            )

            order = await db.scalar(select(Order).where(Order.id == order_id))

            if order is None:
                raise ValueError(
                    f"Order with id {order_id} not found in the database."
                )

            payment = PaymentModel(
                user_id=order.user_id,
                order_id=order.id,
                status=PaymentStatusEnum.SUCCESSFUL,
                external_payment_id=session["payment_intent"],
            )

            db.add(payment)
            await db.flush()

            for (
                order_item_id,
                price_at_payment_cents,
            ) in order_item_ids_and_amount:
                payment_item = PaymentItemModel(
                    payment_id=payment.id,
                    order_item_id=order_item_id,
                    price_at_payment=Decimal(price_at_payment_cents)
                    / Decimal("100"),
                )
                db.add(payment_item)

            await db.flush()

            order.status = OrderStatusEnum.PAID
            await db.flush()
        elif event["type"] == "charge.refunded":
            session = event["data"]["object"]
            payment_intent_id = session.get("payment_intent")
            if not payment_intent_id:
                raise ValueError(
                    "No payment_intent found in charge.refunded event."
                )

            payment = await db.scalar(
                select(PaymentModel).where(
                    PaymentModel.external_payment_id == payment_intent_id
                )
            )
            if payment is None:
                raise ValueError(
                    f"Payment with external_payment_id {payment_intent_id} not found in the database."
                )
            payment.status = PaymentStatusEnum.REFUNDED
            await db.flush()

            order = await db.scalar(
                select(Order).where(Order.id == payment.order_id)
            )

            if not order:
                raise ValueError(
                    f"Order with id {payment.order_id} not found in the database."
                )
            order.status = OrderStatusEnum.CANCELED

            await db.flush()

        return payment


class PaymentServicesEnum(str, Enum):
    STRIPE = "stripe"


def get_payment_service(
    payment_service: PaymentServicesEnum,
) -> Type[PaymentService]:
    if payment_service == PaymentServicesEnum.STRIPE:
        return StripePaymentService

    raise ValueError(f"Unknown payment service '{payment_service}'")
