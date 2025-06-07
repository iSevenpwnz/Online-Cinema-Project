import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_like_dislike_movie(
    client,
    seed_user_groups,
    seed_active_user,
    test_movie,
    db_session,
    jwt_manager,
):
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    # Like
    resp = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"movie_id": test_movie.id, "is_liked": True},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Reaction added"

    # Dislike (update)
    resp = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"movie_id": test_movie.id, "is_liked": False},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Reaction updated"

    # Remove reaction
    resp = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"movie_id": test_movie.id, "is_liked": False},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Reaction removed"


@pytest.mark.asyncio
async def test_toggle_favorite(
    client,
    seed_user_groups,
    seed_active_user,
    test_movie,
    db_session,
    jwt_manager,
):
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    # Add to favorites
    resp = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/favorite",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Added to favorites"

    # Remove from favorites
    resp = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/favorite",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Removed from favorites"


@pytest.mark.asyncio
async def test_rate_movie(
    client,
    seed_user_groups,
    seed_active_user,
    test_movie,
    db_session,
    jwt_manager,
):
    token = jwt_manager.create_access_token({"user_id": seed_active_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    # Rate
    resp = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/rate",
        json={"movie_id": test_movie.id, "rating": 8},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["rating"] == 8
    assert data["movie_id"] == test_movie.id

    # Update rating
    resp = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/rate",
        json={"movie_id": test_movie.id, "rating": 10},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["rating"] == 10


@pytest.mark.asyncio
async def test_get_average_rating(client, test_movie):
    resp = await client.get(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/average-rating"
    )
    assert resp.status_code == 200
    assert "average_rating" in resp.json()
