from pydantic import BaseModel, conint, Field
from typing import Optional


class LikeDislikeSchema(BaseModel):
    movie_id: int
    is_liked: Optional[bool] = None  # True (Like), False (Dislike), None (Empty/Neutral)


class FavoriteSchema(BaseModel):
    movie_id: int


class MovieRatingSchema(BaseModel):
    movie_id: int
    rating: int = Field(ge=1, le=10)


class AverageRatingResponse(BaseModel):
    average_rating: Optional[float] = None
    message: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
