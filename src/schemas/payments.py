from calendar import c
import datetime
from decimal import Decimal
from typing import cast
from pydantic import (
    BaseModel,
    ValidationInfo,
    field_validator,
)

from database.models.orders import OrderItem
from database.models.payments import PaymentStatusEnum
from schemas.accounts import UserRegistrationResponseSchema
from schemas.orders import OrderItemResponse
from services.payments.payments import PaymentServicesEnum, get_payment_service
from pydantic import AnyUrl


class CreatePaymentSessionRequestSchema(BaseModel):
    order_id: int
    payment_service: PaymentServicesEnum
    payment_method: str

    @field_validator("payment_service")
    @classmethod
    def validate_payment_service(cls, payment_service: PaymentServicesEnum):
        get_payment_service(payment_service)
        return payment_service

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(
        cls, payment_method: str, info: ValidationInfo
    ):
        payment_service = cast(
            PaymentServicesEnum, info.data.get("payment_service")
        )
        payment_service_class = get_payment_service(payment_service)
        payment_service_class.validate_payment_method(payment_method)

        return payment_method


class CreatePaymentSessionResponseSchema(BaseModel):
    session_url: AnyUrl


class MovieSchema(BaseModel):
    name: str

    model_config = {"from_attributes": True}


class OrderItemSchema(BaseModel):
    movie_id: int
    price_at_order: Decimal
    movie: MovieSchema

    model_config = {"from_attributes": True}


class PaymentItemSchema(BaseModel):
    id: int
    order_item_id: int
    price_at_payment: Decimal
    order_item: OrderItemSchema

    model_config = {"from_attributes": True}


class OrderSchema(BaseModel):
    id: int
    status: str
    created_at: datetime.date
    total_amount: Decimal

    model_config = {"from_attributes": True}


class PaymentModelSchema(BaseModel):
    id: int
    order_id: int
    order: OrderSchema
    created_at: datetime.datetime
    status: PaymentStatusEnum
    external_payment_id: str

    user: UserRegistrationResponseSchema
    payment_items: list[PaymentItemSchema]

    model_config = {"from_attributes": True}


class RetrievePaymentsRequestSchema(BaseModel):
    user_id: int | None
    from_date: datetime.date | None
    to_date: datetime.date | None
    status: PaymentStatusEnum | None
