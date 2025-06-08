import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_favorites_empty(
    client: AsyncClient, seed_user_groups, seed_active_user, jwt_manager
):
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get(
        "/api/v1/extra_functionality/favorites", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["movies"] == []
    assert data["total_items"] == 0
    assert data["total_pages"] == 0


@pytest.mark.asyncio
async def test_get_user_favorites_with_movies(
    client: AsyncClient,
    seed_user_groups,
    seed_active_user,
    db_session,
    test_movies,
    jwt_manager,
):
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get(
        "/api/v1/extra_functionality/favorites", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_items"] == len(test_movies)
    names = [m["name"] for m in data["movies"]]
    for movie in test_movies:
        assert movie.name in names


@pytest.mark.asyncio
async def test_get_user_favorites_with_search(
    client: AsyncClient,
    seed_user_groups,
    seed_active_user,
    db_session,
    test_movies,
    jwt_manager,
):
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get(
        "/api/v1/extra_functionality/favorites?search=Test", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any("Test" in m["name"] for m in data["movies"])


@pytest.mark.asyncio
async def test_get_user_favorites_pagination(
    client: AsyncClient,
    seed_user_groups,
    seed_active_user,
    db_session,
    test_movies,
    jwt_manager,
):
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get(
        "/api/v1/extra_functionality/favorites?page=1&per_page=2",
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["movies"]) <= 2
    assert data["total_items"] == len(test_movies)
    assert data["total_pages"] == (len(test_movies) + 1) // 2
