from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
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
    description="Create an order based on the current user's cart.",
    responses={
        201: {"description": "Order created successfully."},
        400: {"description": "Cart is empty or contains unavailable movies."},
    },
)
@router.post(
    "/create-from-cart",
    response_model=OrderResponse,
    status_code=201,
    summary="Create order from cart",
    description="Create an order based on the current user's cart."
                " Optionally specify a movie_id to order only that movie.",
    responses={
        201: {"description": "Order created successfully."},
        400: {"description": "Cart is empty or contains unavailable movies."},
    },
)
async def create_order_from_cart(
    movie_id: Optional[int] = Query(None, description="ID of the movie to order from the cart."
                                                      " If not provided, all movies from the cart will be ordered."),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    service = OrderService(db)
    try:
        order = await service.create_order_from_cart(current_user, movie_id)
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
    status: Optional[List[str]] = Query(
        None,
        description="Filter orders by status (e.g. Pending, Paid, Canceled). Multiple statuses allowed.",
    ),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[OrderResponse]:
    if status:
        invalid_statuses = [s for s in status if s not in OrderStatusEnum._value2member_map_]
        if invalid_statuses:
            allowed = [e.value for e in OrderStatusEnum]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status values: {invalid_statuses}. Allowed values: {allowed}",
            )
    service = OrderService(db)
    status_filter = [OrderStatusEnum(s) for s in status] if status else None
    orders = await service.get_order_history(current_user, status_filter)
    return [OrderResponse.from_orm(order) for order in orders]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order by ID",
    description="Retrieve a specific order by its ID for the current user.",
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
    description="Change the status of an order. Admins can change to any status. Users can only cancel their orders.",
)
async def change_order_status(
    order_id: int = Path(..., description="ID of the order to update"),
    new_status: str = Query(..., description="New status for the order"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    if new_status not in OrderStatusEnum._value2member_map_:
        allowed = [e.value for e in OrderStatusEnum]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status value: {new_status}. Allowed values: {allowed}",
        )

    status_enum = OrderStatusEnum(new_status)

    service = OrderService(db)
    order = await service.change_order_status(order_id, status_enum, current_user)
    return OrderResponse.from_orm(order)
