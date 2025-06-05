from datetime import date

import pytest
from httpx import AsyncClient



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
    # Створюємо країну
    country = CountryModel(code="USA", name="United States")
    db_session.add(country)
    await db_session.flush()

    # Створюємо жанр
    genre = GenreModel(name="Test Genre")
    db_session.add(genre)
    await db_session.flush()

    # Створюємо актора
    actor = ActorModel(name="Test Actor")
    db_session.add(actor)
    await db_session.flush()

    # Створюємо мову
    language = LanguageModel(name="English")
    db_session.add(language)
    await db_session.flush()

    # Створюємо фільм із залежностями
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
async def test_like_dislike_functionality(client: AsyncClient, seed_user_groups, seed_user, test_movie):
    """ Tests the like/dislike functionality for a movie.
    step 1: Add a like,
    step 2: Update to dislike,
    step 3: Remove the reaction by clicking dislike again. """
    response_add = await client.post(
        f"/movies/{test_movie.id}/like",
        json={"is_liked": True},
        headers={"Authorization": f"Bearer fake-token-for-{seed_user.id}"}
    )
    assert response_add.status_code == 200
    assert response_add.json()["message"] == "Reaction added"


    response_update = await client.post(
        f"/movies/{test_movie.id}/like",
        json={"is_liked": False},
        headers={"Authorization": f"Bearer fake-token-for-{seed_user.id}"}
    )
    assert response_update.status_code == 200
    assert response_update.json()["message"] == "Reaction updated"

    response_remove = await client.post(
        f"/movies/{test_movie.id}/like",
        json={"is_liked": False},
        headers={"Authorization": f"Bearer fake-token-for-{seed_user.id}"}
    )
    assert response_remove.status_code == 200
    assert response_remove.json()["message"] == "Reaction removed"


@pytest.mark.asyncio
async def test_toggle_favorite(client: AsyncClient, seed_user_groups, seed_user, test_movie):
    response = await client.post(
        f"/movies/{test_movie.id}/favorite",
        headers={"Authorization": f"Bearer fake-token-for-{seed_user.id}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Added to favorites"


@pytest.mark.asyncio
async def test_rate_movie(client: AsyncClient, seed_user_groups, seed_user, test_movie):
    response = await client.post(
        f"/movies/{test_movie.id}/rate",
        json={"rating": 9},
        headers={"Authorization": f"Bearer fake-token-for-{seed_user.id}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Rating saved"


@pytest.mark.asyncio
async def test_get_average_rating(client: AsyncClient, test_movie):
    response = await client.get(f"/movies/{test_movie.id}/average-rating")
    assert response.status_code == 200
    assert "average_rating" in response.json()
