import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.accounts import UserModel, UserGroupModel, UserGroupEnum


@pytest.mark.asyncio
async def test_patch_user_success(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: AsyncSession,
):
    # Create a user
    user = UserModel.create(
        email="patchuser@example.com",
        raw_password="StrongPassword123!",
        group_id=1,
    )
    user.is_active = False
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    # Create admin group if not exists
    admin_group = await db_session.scalar(
        select(UserGroupModel).where(
            UserGroupModel.name == UserGroupEnum.ADMIN
        )
    )
    if not admin_group:
        admin_group = UserGroupModel(name=UserGroupEnum.ADMIN)
        db_session.add(admin_group)
        await db_session.commit()
        await db_session.refresh(admin_group)
    admin = UserModel.create(
        email="admin@example.com",
        raw_password="AdminPassword123!",
        group_id=admin_group.id,
    )
    admin.is_active = True
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    login_resp = await client.post(
        "/api/v1/accounts/login/",
        json={"email": admin.email, "password": "AdminPassword123!"},
    )
    token = login_resp.json()["access_token"]
    # Patch user: activate and change group
    resp = await client.patch(
        f"/api/v1/users/{user.id}",
        json={"is_active": True, "group": "moderator"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == user.id
    assert data["is_active"] is True
    assert data["group"] == "moderator"


@pytest.mark.asyncio
async def test_patch_user_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: AsyncSession,
):
    # Create admin group if not exists
    admin_group = await db_session.scalar(
        select(UserGroupModel).where(
            UserGroupModel.name == UserGroupEnum.ADMIN
        )
    )
    if not admin_group:
        admin_group = UserGroupModel(name=UserGroupEnum.ADMIN)
        db_session.add(admin_group)
        await db_session.commit()
        await db_session.refresh(admin_group)
    admin = UserModel.create(
        email="admin2@example.com",
        raw_password="AdminPassword123!",
        group_id=admin_group.id,
    )
    admin.is_active = True
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    login_resp = await client.post(
        "/api/v1/accounts/login/",
        json={"email": admin.email, "password": "AdminPassword123!"},
    )
    token = login_resp.json()["access_token"]
    # Patch non-existent user
    resp = await client.patch(
        f"/api/v1/users/99999",
        json={"is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_patch_user_group_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
    # seed_user_groups: AsyncSession,
):
    # Create a user
    user = UserModel.create(
        email="patchuser2@example.com",
        raw_password="StrongPassword123!",
        group_id=1,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    # Create admin group if not exists
    admin_group = await db_session.scalar(
        select(UserGroupModel).where(
            UserGroupModel.name == UserGroupEnum.ADMIN
        )
    )
    if not admin_group:
        admin_group = UserGroupModel(name=UserGroupEnum.ADMIN)
        db_session.add(admin_group)
        await db_session.commit()
        await db_session.refresh(admin_group)
    admin = UserModel.create(
        email="admin3@example.com",
        raw_password="AdminPassword123!",
        group_id=admin_group.id,
    )
    admin.is_active = True
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    login_resp = await client.post(
        "/api/v1/accounts/login/",
        json={"email": admin.email, "password": "AdminPassword123!"},
    )
    token = login_resp.json()["access_token"]

    # Patch user with non-existent group
    resp = await client.patch(
        f"/api/v1/users/{user.id}",
        json={"group": "moderator"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
    assert "group" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_patch_user_forbidden(
    client: AsyncClient,
    db_session: AsyncSession,
    seed_user_groups: AsyncSession,
):
    # Create a user
    user = UserModel.create(
        email="patchuser3@example.com",
        raw_password="StrongPassword123!",
        group_id=1,
    )
    user.is_active = True
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    # Login as non-admin
    login_resp = await client.post(
        "/api/v1/accounts/login/",
        json={"email": user.email, "password": "StrongPassword123!"},
    )
    token = login_resp.json()["access_token"]
    # Try to patch another user
    resp = await client.patch(
        f"/api/v1/users/{user.id}",
        json={"is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403 or resp.status_code == 401
