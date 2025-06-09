import pytest
from httpx import AsyncClient

from database.models.accounts import UserModel
# adding comment to push



@pytest.mark.asyncio
async def test_create_comment_success(
        client: AsyncClient,
        seed_user_groups,
        seed_active_user: UserModel,
        jwt_manager
):
    """
    Test successful creation of a root-level comment.
    """
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/api/v1/comments/", json={
        "content": "Awesome movie!",
        "movie_id": 1
    }, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["id"], int)
    assert data["content"] == "Awesome movie!"
    assert data["movie_id"] == 1
    assert data["parent_id"] is None
    assert "created_at" in data
    assert isinstance(data["user_id"], int)

@pytest.fixture
async def seed_another_user(db_session):
    user = UserModel(
        email="another@email.com",
        is_active=True,
        _hashed_password="hashed"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_reply_comment_and_notification(
        client: AsyncClient,
        db_session,
        seed_user_groups,
        seed_active_user: UserModel,
        jwt_manager
):
    """
    Test that replying to a comment creates a notification
    for the original comment's author.
    """
    user1 = UserModel(email="user1@test.com", is_active=True, _hashed_password="hashed", group_id=1)
    db_session.add(user1)
    await db_session.commit()
    await db_session.refresh(user1)

    token1 = jwt_manager.create_access_token({"user_id": user1.id})
    headers1 = {"Authorization": f"Bearer {token1}"}

    user2 = UserModel(email="user2@test.com", is_active=True, _hashed_password="hashed", group_id=1)
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    token2 = jwt_manager.create_access_token({"user_id": user2.id})
    headers2 = {"Authorization": f"Bearer {token2}"}

    parent_resp = await client.post("/api/v1/comments/", json={
        "content": "Parent comment",
        "movie_id": 1
    }, headers=headers1)
    assert parent_resp.status_code == 200
    parent_id = parent_resp.json()["id"]

    reply_resp = await client.post("/api/v1/comments/", json={
        "content": "Reply comment",
        "movie_id": 1,
        "parent_id": parent_id
    }, headers=headers2)
    assert reply_resp.status_code == 200

    notif_resp = await client.get("/api/v1/comments/notifications/", headers=headers1)
    assert notif_resp.status_code == 200
    notifications = notif_resp.json()
    assert any("replied" in n["message"] for n in notifications)


@pytest.mark.asyncio
async def test_like_comment_creates_notification(
        client: AsyncClient,
        db_session,
        seed_user_groups,
        seed_active_user: UserModel,
        jwt_manager
):
    """
    Test that liking a comment sends a notification to the comment author
    """
    user1 = UserModel(email="user1@test.com", is_active=True, _hashed_password="hashed", group_id=1)
    db_session.add(user1)
    await db_session.commit()
    await db_session.refresh(user1)

    token1 = jwt_manager.create_access_token({"user_id": user1.id})
    headers1 = {"Authorization": f"Bearer {token1}"}

    user2 = UserModel(email="user2@test.com", is_active=True, _hashed_password="hashed", group_id=1)
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    token2 = jwt_manager.create_access_token({"user_id": user2.id})
    headers2 = {"Authorization": f"Bearer {token2}"}

    comment_resp = await client.post("/api/v1/comments/", json={
        "content": "Like this comment",
        "movie_id": 1
    }, headers=headers1)
    comment_id = comment_resp.json()["id"]

    like_resp = await client.post(f"/api/v1/comments/{comment_id}/like", headers=headers2)
    assert like_resp.status_code == 200
    assert like_resp.json()["detail"] == "Liked and notification sent."

    notif_resp = await client.get("/api/v1/comments/notifications/", headers=headers1)
    assert notif_resp.status_code == 200
    notifications = notif_resp.json()
    assert any("liked" in n["message"] for n in notifications)


@pytest.mark.asyncio
async def test_duplicate_like_comment_fails(
        client: AsyncClient,
        seed_user_groups,
        seed_active_user: UserModel,
        jwt_manager
):
    """
    Test that a user cannot like the same comment more than once.
    """
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/comments/", json={
        "content": "Double like",
        "movie_id": 1
    }, headers=headers)
    comment_id = resp.json()["id"]

    await client.post(f"/api/v1/comments/{comment_id}/like", headers=headers)
    second_like = await client.post(f"/api/v1/comments/{comment_id}/like", headers=headers)

    assert second_like.status_code == 400
    assert second_like.json()["detail"] == "Comment already liked."


@pytest.mark.asyncio
async def test_get_notifications_list_schema_and_data(
        client: AsyncClient,
        seed_user_groups,
        seed_active_user: UserModel,
        jwt_manager
):
    """
    Test get the current user's notifications.
    """
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/comments/notifications/", headers=headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)

    for item in data:
        assert "id" in item
        assert "message" in item
        assert "is_read" in item
        assert "created_at" in item
