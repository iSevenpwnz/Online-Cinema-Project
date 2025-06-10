from datetime import date
from decimal import Decimal
from typing import List, Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from database.models.shopping_cart import Cart, CartItem
from database.models.orders import Order, OrderItem, OrderStatusEnum
from database.models.accounts import UserModel, UserGroupEnum


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order_from_cart(
        self, user: UserModel, cart_item_ids: Optional[List[int]] = None
    ) -> Order:
        cart_query = (
            select(Cart)
            .where(Cart.user_id == user.id)
            .options(selectinload(Cart.items).selectinload(CartItem.movie))
        )
        cart_result = await self.session.execute(cart_query)
        cart: Optional[Cart] = cart_result.scalar_one_or_none()

        if not cart or not cart.items:
            raise ValueError("Cart is empty.")

        if cart_item_ids:
            filtered_items = [item for item in cart.items if item.id in cart_item_ids]
            if not filtered_items:
                raise ValueError("Selected cart items not found in your cart.")
        else:
            filtered_items = cart.items

        movie_ids = [item.movie_id for item in filtered_items]

        existing_query = (
            select(OrderItem.movie_id)
            .join(Order)
            .where(
                Order.user_id == user.id,
                OrderItem.movie_id.in_(movie_ids),
                Order.status.in_([OrderStatusEnum.PAID, OrderStatusEnum.PENDING]),
            )
        )
        existing_result = await self.session.execute(existing_query)
        excluded_movie_ids = set(existing_result.scalars().all())

        valid_items = [item for item in filtered_items if item.movie_id not in excluded_movie_ids]

        if not valid_items:
            raise ValueError("All selected movies are already purchased or pending in another order.")

        total_amount = Decimal("0.00")
        order_items: List[OrderItem] = []

        for item in valid_items:
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

        for item in valid_items:
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
            raise HTTPException(status_code=404, detail="Order not found or access denied.")

        if not user.has_group(UserGroupEnum.ADMIN):
            if new_status != OrderStatusEnum.CANCELED:
                raise HTTPException(status_code=403, detail="You can only cancel your order.")

        order.status = new_status
        await self.session.commit()
        await self.session.refresh(order)

        return order
