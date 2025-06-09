from typing import List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    movie_id: int
    movie_name: str
    price_at_order: Decimal

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            movie_id=obj.movie_id,
            movie_name=obj.movie.name,
            price_at_order=obj.price_at_order
        )


class OrderResponse(BaseModel):
    id: int
    status: str
    created_at: date
    total_amount: Decimal
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            status=obj.status.value if hasattr(obj.status, "value") else obj.status,
            created_at=obj.created_at,
            total_amount=obj.total_amount,
            items=[OrderItemResponse.from_orm(item) for item in obj.order_items]
        )
