from datetime import date
from decimal import Decimal
from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.shopping_cart import Cart, CartItem
from database.models.orders import Order, OrderItem, OrderStatusEnum
from database.models.accounts import UserModel


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order_from_cart(self, user: UserModel) -> Order:
        cart_query = (
            select(Cart)
            .where(Cart.user_id == user.id)
            .options(selectinload(Cart.items).selectinload(CartItem.movie))
        )
        cart_result = await self.session.execute(cart_query)
        cart: Optional[Cart] = cart_result.scalar_one_or_none()

        if not cart or not cart.items:
            raise ValueError("Cart is empty.")

        total_amount = Decimal("0.00")
        order_items: List[OrderItem] = []

        for item in cart.items:
            movie = item.movie
            total_amount += movie.price
            order_items.append(OrderItem(movie_id=movie.id, price_at_order=movie.price))

        order = Order(
            user_id=user.id,
            created_at=date.today(),
            status=OrderStatusEnum.PENDING,
            total_amount=total_amount,
            order_items=order_items,
        )
        self.session.add(order)

        for item in cart.items:
            await self.session.delete(item)

        await self.session.commit()

        order_query = (
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.movie))
        )
        order_result = await self.session.execute(order_query)
        created_order: Order = order_result.scalar_one()

        return created_order

    async def get_order_history(
        self, user: UserModel, status_filter: Optional[List[OrderStatusEnum]] = None
    ) -> Sequence[Order]:
        query = (
            select(Order)
            .where(Order.user_id == user.id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.movie))
            .order_by(Order.created_at.desc())
        )

        if status_filter:
            query = query.where(Order.status.in_(status_filter))

        result = await self.session.execute(query)
        orders: Sequence[Order] = result.scalars().all()
        return orders

    async def get_order_by_id(self, order_id: int, user: UserModel) -> Order:
        query = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user.id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.movie))
        )
        result = await self.session.execute(query)
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Order not found or access denied.")
        return order

    async def change_order_status(
        self, order_id: int, new_status: OrderStatusEnum, user: UserModel
    ) -> Order:
        query = (
            select(Order)
            .where(Order.id == order_id, Order.user_id == user.id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.movie))
        )
        result = await self.session.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise ValueError("Order not found or access denied.")

        order.status = new_status
        await self.session.commit()
        await self.session.refresh(order)

        return order
