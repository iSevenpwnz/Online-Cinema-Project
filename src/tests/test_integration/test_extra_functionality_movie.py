import pytest
from httpx import AsyncClient

from tests.conftest import db_session
import pytest_asyncio
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.movies import (
    MovieModel,
    CountryModel,
    GenreModel,
    ActorModel,
    LanguageModel,
    MovieStatusEnum,
)



@pytest_asyncio.fixture(scope="function")
async def test_movie(db_session: AsyncSession):

    country = CountryModel(code="USA", name="United States")
    db_session.add(country)
    await db_session.flush()

    genre = GenreModel(name="Test Genre")
    db_session.add(genre)
    await db_session.flush()

    actor = ActorModel(name="Test Actor")
    db_session.add(actor)
    await db_session.flush()

    language = LanguageModel(name="English")
    db_session.add(language)
    await db_session.flush()

    movie = MovieModel(
        name="Test Movie",
        date=date(2022, 1, 1),
        score=8.5,
        overview="This is a test movie used for testing",
        status=MovieStatusEnum.RELEASED,
        budget=1000000.00,
        revenue=1500000.00,
        country_id=country.id,
        country=country,
        genres=[genre],
        actors=[actor],
        languages=[language],
    )
    db_session.add(movie)
    await db_session.commit()
    await db_session.refresh(movie)

    yield movie

@pytest.mark.asyncio
async def test_like_dislike_functionality(client, seed_user_groups, seed_user, test_movie, db_session, jwt_manager):
    """ Tests the like/dislike functionality for the movie.
    step 1: Add a like,
    step 2: Update to dislike,
    step 3: Remove the reaction by clicking dislike again. """
    seed_user.is_active = True
    await seed_user_groups.commit()
    await seed_user_groups.refresh(seed_user)

    token = jwt_manager.create_access_token({"user_id": seed_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    response_add = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"is_liked": True, "movie_id": test_movie.id},
        headers=headers
    )
    assert response_add.status_code == 200
    assert response_add.json()["message"] == "Reaction added"


    response_update = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"is_liked": False, "movie_id": test_movie.id},
        headers=headers
    )
    assert response_update.status_code == 200
    assert response_update.json()["message"] == "Reaction updated"

    response_remove = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"is_liked": False, "movie_id": test_movie.id},
        headers=headers
    )
    assert response_remove.status_code == 200
    assert response_remove.json()["message"] == "Reaction removed"


@pytest.mark.asyncio
async def test_toggle_favorite(client, seed_user_groups, seed_user, test_movie, db_session, jwt_manager):
    """ Tests add favorite functionality for the movie."""
    seed_user.is_active = True
    await seed_user_groups.commit()
    await seed_user_groups.refresh(seed_user)

    token = jwt_manager.create_access_token({"user_id": seed_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/favorite",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Added to favorites"


@pytest.mark.asyncio
async def test_rate_movie(client, seed_user_groups, seed_user, test_movie, db_session, jwt_manager):
    seed_user.is_active = True
    await seed_user_groups.commit()
    await seed_user_groups.refresh(seed_user)

    token = jwt_manager.create_access_token({"user_id": seed_user.id})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/rate",
        json={"rating": 9, "movie_id": test_movie.id},
        headers=headers
    )

    assert response.status_code == 200, f"Response text: {response.text}"
    data = response.json()
    assert data["rating"] == 9
    assert data["movie_id"] == test_movie.id


@pytest.mark.asyncio
async def test_get_average_rating(client: AsyncClient, test_movie):
    """ Tests the average rating functionality for the movie."""
    response = await client.get(f"/api/v1/extra_functionality/movies/{test_movie.id}/average-rating")
    assert response.status_code == 200
    assert "average_rating" in response.json()


@pytest.mark.asyncio
async def test_like_no_reaction_to_add(client, seed_user_groups, seed_user, test_movie, db_session, jwt_manager):
    """
    Test that when a user tries to add a like/dislike reaction with a value of None
    and the user has not reacted to the movie before,
    the response returns the message "No reaction to add".
    """
    token = jwt_manager.create_access_token({"user_id": seed_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"is_liked": None, "movie_id": test_movie.id},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "No reaction to add"

@pytest.mark.asyncio
async def test_like_no_change(client, seed_user_groups, seed_user, test_movie, db_session, jwt_manager):
    """
    Test the scenario where a user already has a reaction (like or dislike),
    then sends None as the new reaction,
    the response should return "No change" indicating no update was made.
    """
    token = jwt_manager.create_access_token({"user_id": seed_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"is_liked": True, "movie_id": test_movie.id},
        headers=headers
    )
    response = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/like",
        json={"is_liked": None, "movie_id": test_movie.id},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "No change"

@pytest.mark.asyncio
async def test_toggle_favorite_removes(client, seed_user_groups, seed_user, test_movie, db_session, jwt_manager):
    """
    Test the removal of a movie from the user's favorites.
    First, the movie is added to favorites,
    then a subsequent request removes it,
    expecting the response message "Removed from favorites".
    """
    token = jwt_manager.create_access_token({"user_id": seed_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/favorite",
        headers=headers
    )
    response = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/favorite",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Removed from favorites"

@pytest.mark.asyncio
async def test_rate_movie_update(client, seed_user_groups, seed_user, test_movie, db_session, jwt_manager):
    """
    Test updating a user's rating for a movie.
    Initially, the user sets a rating,
    then updates it with a different value,
    the response should contain the updated rating.
    """
    token = jwt_manager.create_access_token({"user_id": seed_user.id})
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/rate",
        json={"rating": 7, "movie_id": test_movie.id},
        headers=headers
    )
    response = await client.post(
        f"/api/v1/extra_functionality/movies/{test_movie.id}/rate",
        json={"rating": 8, "movie_id": test_movie.id},
        headers=headers
    )
    data = response.json()
    assert response.status_code == 200
    assert data["rating"] == 8

@pytest.mark.asyncio
async def test_get_average_rating_no_ratings(client, test_movie):
    """
    Test that when a movie has no ratings yet,
    a request for the average rating returns average_rating as None
    along with the message "No ratings yet".
    """
    response = await client.get(f"/api/v1/extra_functionality/movies/{test_movie.id}/average-rating")
    data = response.json()
    assert response.status_code == 200
    assert data["average_rating"] is None
    assert data["message"] == "No ratings yet"

