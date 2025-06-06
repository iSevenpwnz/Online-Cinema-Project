from abc import ABC, abstractmethod, abstractstaticmethod
from decimal import Decimal
from enum import Enum
from typing import Literal, Type

from config.dependencies import get_settings
from database.models.orders import Order
from config.settings import BaseAppSettings
from database.models.payments import PaymentModel

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
    @classmethod
    @abstractmethod
    def validate_payment_method(cls, payment_method: str) -> None:
        pass

    @abstractmethod
    async def create_payment_session(self, order: Order) -> str:
        pass

    @abstractmethod
    async def handle_event(self) -> PaymentModel | None:
        pass


class StripePaymentService(PaymentService):
    AVAILABLE_PAYMENT_METHODS: list[StripePaymentMethod] = [
        "card",
    ]

    def __init__(
        self, settings: BaseAppSettings, payment_method: StripePaymentMethod
    ) -> None:
        super().__init__()
        self.secret_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        self.validate_payment_method(payment_method=payment_method)

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
        line_items = []
        for order_item in order.order_items:
            line_items.append(
                {
                    "price_data": {
                        "currency": "usd",  # TODO: get currency from .env
                        "product_data": {
                            "name": order_item.movie.name,
                            "metadata": {
                                "movie_id": str(order_item.movie.id),
                            },
                        },
                        "unit_amount": int(
                            order_item.price_at_order * Decimal("100")
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
            success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",  # TODO: add url builder function and SUCCESS url to .env
            cancel_url="https://yourdomain.com/cancel",  # TODO: add cancel url,
        )

    async def create_payment_session(self, order: Order) -> str:
        session = await run_in_threadpool(self._create_payment_session, order)
        return session.url

    async def handle_event(self) -> PaymentModel | None:
        raise NotImplementedError


class PaymentServicesEnum(str, Enum):
    STRIPE = "stripe"


def get_payment_service(
    payment_service: PaymentServicesEnum,
) -> Type[PaymentService]:
    if payment_service == PaymentServicesEnum.STRIPE:
        return StripePaymentService

    raise ValueError(f"Unknown payment service '{payment_service}'")
