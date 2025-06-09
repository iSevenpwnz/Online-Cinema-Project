import datetime
from shlex import join

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from database.models.orders import OrderItem
from database.models.payments import (
    PaymentItemModel,
    PaymentModel,
    PaymentStatusEnum,
)


async def fetch_payments(
    user_id: int | None = None,
    from_date: datetime.date | None = None,
    to_date: datetime.date | None = None,
    status: PaymentStatusEnum | None = None,
):
    query = select(PaymentModel)

    if user_id:
        query = query.where(PaymentModel.user_id == user_id)

    if from_date:
        query = query.where(
            PaymentModel.created_at
            > datetime.datetime.combine(from_date, datetime.time.min)
        )

    if to_date:
        query = query.where(
            PaymentModel.created_at
            < datetime.datetime.combine(to_date, datetime.time.max)
        )

    if status:
        query = query.where(PaymentModel.status == status)

    query = query.options(
        joinedload(PaymentModel.order),
        selectinload(PaymentModel.payment_items)
        .selectinload(PaymentItemModel.order_item)
        .joinedload(OrderItem.movie),
    )

    return query
