from datetime import datetime
from typing import List

from pydantic import BaseModel


class CartItemResponse(BaseModel):
    id: int
    movie_id: int
    movie_name: str
    added_at: datetime

    model_config = {
        "from_attributes": True
    }

    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object."""
        return cls(
            id=obj.id,
            movie_id=obj.movie_id,
            movie_name=obj.movie.name,
            added_at=obj.added_at
        )


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]

    model_config = {
        "from_attributes": True
    }

    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM object."""
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            items=[CartItemResponse.from_orm(item) for item in obj.items]
        ) 