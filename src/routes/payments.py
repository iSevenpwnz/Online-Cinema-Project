from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.dependencies import get_settings
from database.models.accounts import UserModel
from database.models.orders import Order, OrderStatusEnum
from schemas.payments import (
    CreatePaymentSessionRequestSchema,
    CreatePaymentSessionResponseSchema,
)
from security.http import get_current_user
from services.payments.payments import get_payment_service, PaymentServicesEnum

from database import (
    get_db,
)

router = APIRouter()


@router.post("/payment-session")
async def create_payment_session(
    payment_session_data: CreatePaymentSessionRequestSchema,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
) -> CreatePaymentSessionResponseSchema:
    PaymentService = get_payment_service(payment_session_data.payment_service)

    if payment_session_data.payment_service == PaymentServicesEnum.STRIPE:
        payment_service = PaymentService(
            settings=get_settings(),
            payment_method=payment_session_data.payment_method,
        )

    order = await db.scalar(
        select(Order)
        .where(Order.id == payment_session_data.order_id)
        .options(selectinload(Order.order_items))
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {payment_session_data.order_id} not found",
        )

    if user.id != order.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this order.",
        )

    if not order.status == OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Order with id {payment_session_data.order_id} does not have status 'PENDING'."
                f"Current status: {order.status.value}"
            ),
        )

    session_url = await payment_service.create_payment_session(order)

    return CreatePaymentSessionResponseSchema(session_url=session_url)
