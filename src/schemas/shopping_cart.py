from datetime import datetime
from typing import List

from pydantic import BaseModel
from schemas.movies import MovieListItemSchema


class CartItemResponse(BaseModel):
    id: int
    movie_id: int
    movie_name: str
    added_at: datetime
    movie: MovieListItemSchema

    model_config = {"from_attributes": True}

    @classmethod
    def from_dict(cls, obj):
        """Create response from ORM object."""
        return cls(
            id=obj.id,
            movie_id=obj.movie_id,
            movie_name=obj.movie.name,
            added_at=obj.added_at,
            movie=MovieListItemSchema(
                id=obj.movie.id,
                name=obj.movie.name,
                year=obj.movie.year,
                imdb=obj.movie.imdb,
                price=obj.movie.price,
                genres=[g.name for g in getattr(obj.movie, 'genres', [])] if hasattr(obj.movie, 'genres') else []
            )
        )


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]

    model_config = {"from_attributes": True}

    @classmethod
    def from_dict(cls, obj):
        """Create response from ORM object."""
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            items=[CartItemResponse.from_dict(item) for item in obj.items]
        )
