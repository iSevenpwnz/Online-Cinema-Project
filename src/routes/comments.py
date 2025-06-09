from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from database import get_db
from database.models.comments import Comment, CommentLike, Notification
from database.models.accounts import UserModel
from schemas.comments import CommentCreate, CommentOut, NotificationOut
from security.http import get_current_user


router = APIRouter()


@router.post("/", response_model=CommentOut)
async def create_comment(
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Create a new comment.
    Sends a notification to the 'parent' comment's author if it's a reply.
    """
    new_comment = Comment(
        content=comment.content,
        movie_id=comment.movie_id,
        user_id=user.id,
        parent_id=comment.parent_id
    )
    db.add(new_comment)
    await db.flush()

    if comment.parent_id:
        parent = await db.get(Comment, comment.parent_id)
        if parent and parent.user_id != user.id:
            notification = Notification(
                user_id=parent.user_id,
                message=f"{user.email} replied to your comment."
            )
            db.add(notification)

    await db.commit()
    await db.refresh(new_comment)
    return new_comment


@router.post("/{comment_id}/like")
async def like_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Like a comment. Prevents duplicate likes.
    Sends a notification to the comment's author.
    """
    existing_like = await db.execute(
        select(CommentLike).where(
            and_(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == user.id
            )
        )
    )
    if existing_like.scalar():
        raise HTTPException(status_code=400, detail="Comment already liked.")

    like = CommentLike(comment_id=comment_id, user_id=user.id)
    db.add(like)

    comment = await db.get(Comment, comment_id)
    if comment and comment.user_id != user.id:
        notification = Notification(
            user_id=comment.user_id,
            message=f"{user.email} liked your comment."
        )
        db.add(notification)

    await db.commit()
    return {"detail": "Liked and notification sent."}


@router.get("/notifications/", response_model=list[NotificationOut])
async def get_notifications(
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List of all notifications for the current user.
    """
    result = await db.execute(
        select(Notification).where(Notification.user_id == user.id)
    )
    return result.scalars().all()
