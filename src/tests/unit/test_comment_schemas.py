import pytest
from datetime import datetime
from pydantic import ValidationError
from schemas.comments import (
    CommentCreate,
    CommentOut,
    CommentLikeOut,
    NotificationOut
)


@pytest.mark.asyncio
async def test_comment_create_valid():
    """Test valid CommentCreate schema."""
    schema = CommentCreate(content="Hello", movie_id=1, parent_id=None)
    assert schema.content == "Hello"
    assert schema.movie_id == 1
    assert schema.parent_id is None


@pytest.mark.asyncio
async def test_comment_create_invalid_empty_content():
    """Test that user cannot create empty comment."""
    with pytest.raises(ValidationError) as exc_info:
        CommentCreate(content="", movie_id=1)
    assert "content" in str(exc_info.value)


@pytest.mark.asyncio
async def test_comment_out_valid():
    """Test valid CommentOut schema."""
    out = CommentOut(
        id=1,
        content="Test comment",
        movie_id=42,
        user_id=7,
        created_at=datetime(2024, 1, 1, 12, 0),
        parent_id=None
    )
    assert out.id == 1
    assert out.content == "Test comment"
    assert out.movie_id == 42
    assert out.user_id == 7
    assert isinstance(out.created_at, datetime)
    assert out.parent_id is None


@pytest.mark.asyncio
async def test_comment_like_out_valid():
    """Test valid CommentLikeOut schema."""
    schema = CommentLikeOut(
        id=3,
        user_id=4,
        comment_id=10
    )
    assert schema.id == 3
    assert schema.user_id == 4
    assert schema.comment_id == 10


@pytest.mark.asyncio
async def test_notification_out_valid():
    """Test valid NotificationOut schema."""
    schema = NotificationOut(
        id=5,
        message="You have a new message.",
        is_read=False,
        created_at=datetime(2024, 1, 1, 12, 30)
    )
    assert schema.id == 5
    assert schema.message == "You have a new message."
    assert schema.is_read is False
    assert isinstance(schema.created_at, datetime)
