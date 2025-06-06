from pydantic import BaseModel, ValidationInfo, field_validator

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
        payment_service = info.data.get("payment_service")
        payment_service_class = get_payment_service(payment_service)
        payment_service_class.validate_payment_method(payment_method)

        return payment_method


class CreatePaymentSessionResponseSchema(BaseModel):
    session_url: AnyUrl
