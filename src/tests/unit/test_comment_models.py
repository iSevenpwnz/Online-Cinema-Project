import pytest
from datetime import datetime
from database.models.comments import Comment, Notification, CommentLike



@pytest.mark.asyncio
async def test_create_comment():
    """
    Test creating a Comment model.
    """
    comment = Comment(
        content="This is a test comment.",
        user_id=1,
        movie_id=2,
        created_at=datetime(2024, 1, 1, 12, 0),
        parent_id=None
    )

    assert comment.content == "This is a test comment."
    assert comment.user_id == 1
    assert comment.movie_id == 2
    assert comment.created_at == datetime(2024, 1, 1, 12, 0)
    assert comment.parent_id is None


@pytest.mark.asyncio
async def test_comment_content_field():
    """
    Test that the Comment model has a valid content field.
    """
    comment = Comment(
        content="Nice!",
        user_id=5,
        movie_id=10
    )

    assert hasattr(comment, "content")
    assert isinstance(comment.content, str)


@pytest.mark.asyncio
async def test_comment_reply_relationship():
    """
    Test reply relationship between 'parent' and 'child' comments.
    """
    parent = Comment(id=1, content="Parent", user_id=1, movie_id=1)
    reply = Comment(content="Reply", user_id=2, movie_id=1, parent=parent)
    parent.replies.append(reply)

    assert reply.parent == parent
    assert reply in parent.replies


@pytest.mark.asyncio
async def test_create_comment_like():
    """
    Test creating a CommentLike instance.
    """
    like = CommentLike(user_id=1, comment_id=2)

    assert like.user_id == 1
    assert like.comment_id == 2


@pytest.mark.asyncio
async def test_create_notification():
    """
    Test creating an instance of the Notification model.
    """
    notif = Notification(
        user_id=1,
        message="You got a like!",
        is_read=False,
        created_at=datetime(2024, 1, 1, 12, 0)
    )

    assert notif.user_id == 1
    assert notif.message == "You got a like!"
    assert notif.is_read is False
    assert notif.created_at == datetime(2024, 1, 1, 12, 0)


@pytest.mark.asyncio
async def test_notification_default_is_read_false(db_session):
    """
    Test that the is_read field defaults to False when not explicitly set.
    """
    notif = Notification(user_id=2, message="New reply!")
    db_session.add(notif)
    await db_session.commit()
    await db_session.refresh(notif)

    assert notif.is_read is False
