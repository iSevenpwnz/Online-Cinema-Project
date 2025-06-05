from pydantic import BaseModel, conint
from typing import Optional


class LikeDislikeSchema(BaseModel):
    movie_id: int
    is_liked: Optional[bool]  # True (Like), False (Dislike), None (Empty/Neutral)

class FavoriteSchema(BaseModel):
    movie_id: int

class RatingSchema(BaseModel):
    movie_id: int
    rating: conint(ge=1, le=10)