from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    movie_id: int
    parent_id: Optional[int] = None


class CommentOut(BaseModel):
    id: int
    content: str
    movie_id: int
    user_id: int
    created_at: datetime
    parent_id: Optional[int]

    model_config = {
        "from_attributes" : True
    }


class CommentLikeOut(BaseModel):
    id: int
    user_id: int
    comment_id: int

    model_config = {
        "from_attributes" : True
    }


class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes" : True
    }
