from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models.accounts import UserGroupModel, UserModel
from schemas.users import PatchUserRequestSchema, PatchUserResponseSchema
from security.http import require_admin

from database import (
    get_db,
)

router = APIRouter()


@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    update_user_data: PatchUserRequestSchema,
    _: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PatchUserResponseSchema:

    try:
        user = await db.scalar(
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(joinedload(UserModel.group))
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )

        if update_user_data.is_active is not None:
            user.is_active = update_user_data.is_active

        group = None
        if update_user_data.group:
            group = await db.scalar(
                select(UserGroupModel).where(
                    UserGroupModel.name == update_user_data.group
                )
            )

            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Group '{update_user_data.group}' not found",
                )

            user.group_id = group.id

        await db.commit()

        await db.refresh(user)

        if group:
            user.group = group

        return PatchUserResponseSchema(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            group=user.group.name,
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating user.",
        )
