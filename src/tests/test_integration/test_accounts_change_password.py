import pytest
from sqlalchemy import select
from database import UserModel


@pytest.mark.asyncio
async def test_change_password_success(
    client, db_session, seed_user_groups, seed_active_user
):
    """
    Test successful password change for an authenticated user.
    """
    # Login to get access token
    login_payload = {"email": seed_active_user.email, "password": "StrongP@ssword1"}
    login_response = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    assert login_response.status_code == 201
    access_token = login_response.json()["access_token"]

    # Change password
    change_payload = {
        "old_password": "StrongP@ssword1",
        "new_password": "NewStrongP@ssword2",
    }
    response = await client.post(
        "/api/v1/accounts/change-password/",
        json=change_payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully."

    # Verify new password works
    login_payload_new = {
        "email": seed_active_user.email,
        "password": "NewStrongP@ssword2",
    }
    login_response_new = await client.post(
        "/api/v1/accounts/login/", json=login_payload_new
    )
    assert login_response_new.status_code == 201


@pytest.mark.asyncio
async def test_change_password_invalid_old_password(
    client, db_session, seed_user_groups, seed_active_user
):
    """
    Test change password with invalid old password returns 401.
    """
    login_payload = {"email": seed_active_user.email, "password": "StrongP@ssword1"}
    login_response = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    assert login_response.status_code == 201
    access_token = login_response.json()["access_token"]

    change_payload = {
        "old_password": "WrongPassword1",
        "new_password": "NewStrongP@ssword2",
    }
    response = await client.post(
        "/api/v1/accounts/change-password/",
        json=change_payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid old password."


@pytest.mark.asyncio
async def test_change_password_weak_new_password(
    client, db_session, seed_user_groups, seed_active_user
):
    """
    Test change password with weak new password returns 422.
    """
    login_payload = {"email": seed_active_user.email, "password": "StrongP@ssword1"}
    login_response = await client.post(
        "/api/v1/accounts/login/", json=login_payload
    )
    assert login_response.status_code == 201
    access_token = login_response.json()["access_token"]

    change_payload = {
        "old_password": "StrongP@ssword1",
        "new_password": "short",
    }
    response = await client.post(
        "/api/v1/accounts/change-password/",
        json=change_payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422
    assert "Password must contain at least 8 characters." in str(
        response.json()
    )
