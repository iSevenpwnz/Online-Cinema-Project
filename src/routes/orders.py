from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from database.models.accounts import UserModel
from security.http import get_current_user
from schemas.orders import OrderResponse
from services.orders import OrderService
from database.models.orders import OrderStatusEnum

router = APIRouter()


@router.post(
    "/create-from-cart",
    response_model=OrderResponse,
    status_code=201,
    summary="Create order from cart",
    description=(
        "Create an order based on the current user's cart. "
        "Optionally specify cart_item_ids to order only specific items. "
        "Movies already purchased or pending in another order will be excluded."
    ),
    responses={
        201: {"description": "Order created successfully."},
        400: {"description": "Cart is empty or contains only unavailable/duplicate movies."},
    },
)
async def create_order_from_cart(
    cart_item_ids: Optional[List[int]] = Query(
        None,
        description="IDs of specific cart items to include in the order. "
                    "If omitted, all valid cart items will be used."
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    service = OrderService(db)
    try:
        order = await service.create_order_from_cart(current_user, cart_item_ids)
        return OrderResponse.from_orm(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/history",
    response_model=List[OrderResponse],
    summary="Get order history",
    description="Retrieve a list of orders for the current user with optional status filtering.",
)
async def get_order_history(
    status: Optional[List[OrderStatusEnum]] = Query(
        None,
        description="Filter orders by status (e.g. Pending, Paid, Canceled). You can provide multiple statuses."
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OrderResponse]:
    service = OrderService(db)
    orders = await service.get_order_history(current_user, status)
    return [OrderResponse.from_orm(order) for order in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Retrieve a specific order by its ID for the current user.",
    responses={
        200: {"description": "Order found."},
        404: {"description": "Order not found or access denied."},
    },
)
async def get_order_by_id(
    order_id: int = Path(..., description="ID of the order to retrieve"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    service = OrderService(db)
    try:
        order = await service.get_order_by_id(order_id, current_user)
        return OrderResponse.from_orm(order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Change order status",
    description=(
        "Change the status of an order. "
        "Admins can change to any status. "
        "Regular users can only cancel their own orders (before payment)."
    ),
    responses={
        200: {"description": "Order status updated."},
        400: {"description": "Invalid status value."},
        403: {"description": "You are not allowed to perform this action."},
        404: {"description": "Order not found or access denied."},
    },
)
async def change_order_status(
    order_id: int = Path(..., description="ID of the order to update"),
    new_status: OrderStatusEnum = Query(..., description="New status for the order."),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    service = OrderService(db)
    order = await service.change_order_status(order_id, new_status, current_user)
    return OrderResponse.from_orm(order)
