import datetime
from typing import cast
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    routing,
    status,
)
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import LimitOffsetPage
from pydantic import AnyUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config.dependencies import get_settings
from config.settings import BaseAppSettings
from database.models.accounts import UserGroupEnum, UserModel
from database.models.orders import Order, OrderStatusEnum, OrderItem
from database.models.payments import PaymentStatusEnum
from database.pagination.custom_pagination import CustomPage, CustomParams
from schemas.payments import (
    CreatePaymentSessionRequestSchema,
    CreatePaymentSessionResponseSchema,
    PaymentModelSchema,
    RetrievePaymentsRequestSchema,
)
from security.http import get_current_user, get_current_user_if_active
from services.payments.payments import (
    StripePaymentService,
    get_payment_service,
    PaymentServicesEnum,
)

from database import (
    get_db,
)
from services.payments.payments_crud import fetch_payments

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
        .options(selectinload(Order.order_items).selectinload(OrderItem.movie))
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

    return CreatePaymentSessionResponseSchema(
        session_url=cast(AnyUrl, session_url)
    )


@router.post("/stripe/webhook")
async def handle_stripe_webhook_event(
    request: Request,
    settings: BaseAppSettings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
):
    stripe_service = StripePaymentService(settings, None)

    await stripe_service.handle_event(request, db)

    await db.commit()

    return {"message": "OK"}


def get_filters(
    user_id: int | None = Query(default=None),
    from_date: datetime.date | None = Query(default=None),
    to_date: datetime.date | None = Query(default=None),
    status: PaymentStatusEnum | None = Query(default=None),
):
    return RetrievePaymentsRequestSchema(
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        status=status,
    )


@router.get("/")
async def get_payments(
    request: Request,
    db: AsyncSession = Depends(get_db),
    filters: RetrievePaymentsRequestSchema = Depends(get_filters),
    user: UserModel = Depends(get_current_user_if_active),
    params: CustomParams = Depends(CustomParams),
) -> CustomPage[PaymentModelSchema]:
    if user.has_group(UserGroupEnum.USER):
        filters.user_id = user.id

    payments = await fetch_payments(
        filters.user_id,
        filters.from_date,
        filters.to_date,
        filters.status,
    )

    return await paginate(db, payments, params, additional_data={
        "path": request.url.path,
        "query_params": request.query_params,
    })
