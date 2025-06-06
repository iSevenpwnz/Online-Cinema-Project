import random
import uuid

import pytest
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from database import (
    MovieModel,
    GenreModel,
    StarModel,
    DirectorModel,
    CertificationModel,
)


@pytest.mark.asyncio
async def test_get_movies_empty_database(client):
    """
    Test that the `/movies/` endpoint returns a 404 error when the database is empty.
    """
    response = await client.get("/api/v1/theater/movies/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No movies found."}


@pytest.mark.asyncio
async def test_get_movies_default_parameters(client, seed_database):
    """
    Test the `/movies/` endpoint with default pagination parameters.
    """
    response = await client.get("/api/v1/theater/movies/")
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["movies"]) == 10
    assert response_data["total_pages"] > 0
    assert response_data["total_items"] > 0
    assert response_data["prev_page"] is None
    if response_data["total_pages"] > 1:
        assert response_data["next_page"] is not None
    expected_fields = {"id", "name", "year", "imdb", "price", "description"}
    for movie in response_data["movies"]:
        assert set(movie.keys()) == expected_fields


@pytest.mark.asyncio
async def test_get_movies_with_custom_parameters(client, seed_database):
    """
    Test the `/movies/` endpoint with custom pagination parameters.
    """
    page = 2
    per_page = 5
    response = await client.get(
        f"/api/v1/theater/movies/?page={page}&per_page={per_page}"
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["movies"]) == per_page
    assert response_data["total_pages"] > 0
    assert response_data["total_items"] > 0
    if page > 1:
        assert (
            response_data["prev_page"]
            == f"/theater/movies/?page={page - 1}&per_page={per_page}"
        )
    if page < response_data["total_pages"]:
        assert (
            response_data["next_page"]
            == f"/theater/movies/?page={page + 1}&per_page={per_page}"
        )
    else:
        assert response_data["next_page"] is None
    expected_fields = {"id", "name", "year", "imdb", "price", "description"}
    for movie in response_data["movies"]:
        assert set(movie.keys()) == expected_fields


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page, per_page, expected_detail",
    [
        (0, 10, "Input should be greater than or equal to 1"),
        (1, 0, "Input should be greater than or equal to 1"),
        (0, 0, "Input should be greater than or equal to 1"),
    ],
)
async def test_invalid_page_and_per_page(
    client, page, per_page, expected_detail
):
    """
    Test the `/movies/` endpoint with invalid `page` and `per_page` parameters.
    """
    response = await client.get(
        f"/api/v1/theater/movies/?page={page}&per_page={per_page}"
    )

    assert (
        response.status_code == 422
    ), f"Expected status code 422 for invalid parameters, but got {response.status_code}"

    response_data = response.json()

    assert (
        "detail" in response_data
    ), "Expected 'detail' in the response, but it was missing"

    assert any(
        expected_detail in error["msg"] for error in response_data["detail"]
    ), f"Expected error message '{expected_detail}' in the response details, but got {response_data['detail']}"


@pytest.mark.asyncio
async def test_per_page_maximum_allowed_value(client, seed_database):
    """
    Test the `/movies/` endpoint with the maximum allowed `per_page` value.
    """
    response = await client.get("/api/v1/theater/movies/?page=1&per_page=20")

    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"

    response_data = response.json()

    assert "movies" in response_data, "Response missing 'movies' field."
    assert (
        len(response_data["movies"]) <= 20
    ), f"Expected at most 20 movies, but got {len(response_data['movies'])}"


@pytest.mark.asyncio
async def test_page_exceeds_maximum(client, db_session, seed_database):
    """
    Test the `/movies/` endpoint with a page number that exceeds the maximum.
    """
    per_page = 10

    count_stmt = select(func.count(MovieModel.id))
    result = await db_session.execute(count_stmt)
    total_movies = result.scalar_one()

    max_page = (total_movies + per_page - 1) // per_page

    response = await client.get(
        f"/api/v1/theater/movies/?page={max_page + 1}&per_page={per_page}"
    )

    assert (
        response.status_code == 404
    ), f"Expected status code 404, but got {response.status_code}"
    response_data = response.json()

    assert "detail" in response_data, "Response missing 'detail' field."


@pytest.mark.asyncio
async def test_movies_sorted_by_id_desc(client, db_session, seed_database):
    """
    Test that movies are returned sorted by `id` in descending order
    and match the expected data from the database.
    """
    response = await client.get("/api/v1/theater/movies/?page=1&per_page=10")
    assert response.status_code == 200
    response_data = response.json()
    stmt = select(MovieModel).order_by(MovieModel.id.desc()).limit(10)
    result = await db_session.execute(stmt)
    expected_movies = result.scalars().all()
    expected_movie_ids = [movie.id for movie in expected_movies]
    returned_movie_ids = [movie["id"] for movie in response_data["movies"]]
    assert returned_movie_ids == expected_movie_ids


@pytest.mark.asyncio
async def test_movie_list_with_pagination(client, db_session, seed_database):
    """
    Test the `/movies/` endpoint with pagination parameters.

    Verifies the following:
    - The response status code is 200.
    - Total items and total pages match the expected values from the database.
    - The movies returned match the expected movies for the given page and per_page.
    - The `prev_page` and `next_page` links are correct.
    """
    page = 2
    per_page = 5
    offset = (page - 1) * per_page
    response = await client.get(
        f"/api/v1/theater/movies/?page={page}&per_page={per_page}"
    )
    assert response.status_code == 200
    response_data = response.json()
    count_stmt = select(func.count(MovieModel.id))
    count_result = await db_session.execute(count_stmt)
    total_items = count_result.scalar_one()
    total_pages = (total_items + per_page - 1) // per_page
    assert response_data["total_items"] == total_items
    assert response_data["total_pages"] == total_pages
    stmt = (
        select(MovieModel)
        .order_by(MovieModel.id.desc())
        .offset(offset)
        .limit(per_page)
    )
    result = await db_session.execute(stmt)
    expected_movies = result.scalars().all()
    expected_movie_ids = [movie.id for movie in expected_movies]
    returned_movie_ids = [movie["id"] for movie in response_data["movies"]]
    assert expected_movie_ids == returned_movie_ids
    expected_prev_page = (
        f"/theater/movies/?page={page - 1}&per_page={per_page}"
        if page > 1
        else None
    )
    expected_next_page = (
        f"/theater/movies/?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None
    )
    assert response_data["prev_page"] == expected_prev_page
    assert response_data["next_page"] == expected_next_page


@pytest.mark.asyncio
async def test_movies_fields_match_schema(client, db_session, seed_database):
    """
    Test that each movie in the response matches the fields defined in `MovieListItemSchema`.
    """
    response = await client.get("/api/v1/theater/movies/?page=1&per_page=10")
    assert response.status_code == 200
    response_data = response.json()
    assert "movies" in response_data
    expected_fields = {"id", "name", "year", "imdb", "price", "description"}
    for movie in response_data["movies"]:
        assert set(movie.keys()) == expected_fields


@pytest.mark.asyncio
async def test_get_movie_by_id_not_found(client):
    """
    Test that the `/movies/{movie_id}` endpoint returns a 404 error
    when a movie with the given ID does not exist.
    """
    movie_id = 1
    response = await client.get(f"/api/v1/theater/movies/{movie_id}/")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Movie with the given ID was not found."
    }


@pytest.mark.asyncio
async def test_get_movie_by_id_valid(client, db_session, seed_database):
    """
    Test that the `/movies/{movie_id}` endpoint returns the correct movie details
    when a valid movie ID is provided.

    Verifies the following:
    - The movie exists in the database.
    - The response status code is 200.
    - The movie's `id` and `name` in the response match the expected values from the database.
    """
    stmt_min = select(MovieModel.id).order_by(MovieModel.id.asc()).limit(1)
    result_min = await db_session.execute(stmt_min)
    min_id = result_min.scalars().first()
    stmt_max = select(MovieModel.id).order_by(MovieModel.id.desc()).limit(1)
    result_max = await db_session.execute(stmt_max)
    max_id = result_max.scalars().first()
    random_id = random.randint(min_id, max_id)
    stmt_movie = select(MovieModel).where(MovieModel.id == random_id)
    result_movie = await db_session.execute(stmt_movie)
    expected_movie = result_movie.scalars().first()
    assert expected_movie is not None
    response = await client.get(f"/api/v1/theater/movies/{random_id}/")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == expected_movie.id
    assert response_data["name"] == expected_movie.name
    # Можна додати перевірки для інших полів, якщо треба


@pytest.mark.asyncio
async def test_get_movie_by_id_fields_match_database(
    client, db_session, seed_database
):
    """
    Test that the `/movies/{movie_id}` endpoint returns all fields matching the database data.
    """
    stmt = (
        select(MovieModel)
        .options(
            joinedload(MovieModel.certification),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.stars),
            joinedload(MovieModel.directors),
        )
        .limit(1)
    )
    result = await db_session.execute(stmt)
    random_movie = result.scalars().first()
    assert random_movie is not None
    response = await client.get(f"/api/v1/theater/movies/{random_movie.id}/")
    assert response.status_code == 200
    response_data = response.json()
    expected_fields = {
        "id",
        "uuid",
        "name",
        "year",
        "time",
        "imdb",
        "votes",
        "meta_score",
        "gross",
        "description",
        "price",
        "certification_id",
        "certification",
        "genres",
        "stars",
        "directors",
    }
    assert set(response_data.keys()) == expected_fields
    assert response_data["id"] == random_movie.id
    assert response_data["name"] == random_movie.name
    assert response_data["uuid"] == random_movie.uuid
    assert response_data["year"] == random_movie.year
    assert response_data["time"] == random_movie.time
    assert response_data["imdb"] == random_movie.imdb
    assert response_data["votes"] == random_movie.votes
    assert response_data["description"] == random_movie.description
    assert response_data["price"] == float(random_movie.price)
    assert response_data["certification_id"] == random_movie.certification_id
    # genres, stars, directors, certification — можна перевірити як списки/словник


@pytest.mark.asyncio
async def test_create_movie_and_related_models(client, db_session):
    """
    Test that a new movie is created successfully and related models
    (genres, stars) are created if they do not exist.
    """
    certification = CertificationModel(id=1, name="PG")
    db_session.add(certification)
    await db_session.commit()
    movie_data = {
        "uuid": str(uuid.uuid4()),
        "name": "New Movie",
        "year": 2025,
        "time": 90,
        "imdb": 7.0,
        "votes": 1000,
        "meta_score": 80.0,
        "gross": 1000000.0,
        "description": "An amazing movie.",
        "price": 100.0,
        "certification_id": 1,
        "genres": ["Action", "Adventure"],
        "stars": ["John Doe", "Jane Doe"],
        "directors": ["Some Director"],
    }
    response = await client.post("/api/v1/theater/movies/", json=movie_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == movie_data["name"]
    assert response_data["year"] == movie_data["year"]
    for genre_name in movie_data["genres"]:
        stmt = select(GenreModel).where(GenreModel.name == genre_name)
        result = await db_session.execute(stmt)
        genre = result.scalars().first()
        assert genre is not None
    for star_name in movie_data["stars"]:
        stmt = select(StarModel).where(StarModel.name == star_name)
        result = await db_session.execute(stmt)
        star = result.scalars().first()
        assert star is not None
    for director_name in movie_data["directors"]:
        stmt = select(DirectorModel).where(DirectorModel.name == director_name)
        result = await db_session.execute(stmt)
        director = result.scalars().first()
        assert director is not None


@pytest.mark.asyncio
async def test_create_movie_duplicate_error(client, db_session, seed_database):
    """
    Test that trying to create a movie with the same name and date as an existing movie
    results in a 409 conflict error.
    """
    stmt = select(MovieModel).limit(1)
    result = await db_session.execute(stmt)
    existing_movie = result.scalars().first()
    assert existing_movie is not None
    movie_data = {
        "uuid": str(uuid.uuid4()),
        "name": existing_movie.name,
        "year": existing_movie.year,
        "time": existing_movie.time,
        "imdb": existing_movie.imdb,
        "votes": existing_movie.votes,
        "meta_score": existing_movie.meta_score,
        "gross": existing_movie.gross,
        "description": "Duplicate movie test.",
        "price": float(existing_movie.price),
        "certification_id": existing_movie.certification_id,
        "genres": ["Drama"],
        "stars": ["New Actor"],
        "directors": ["New Director"],
    }
    response = await client.post("/api/v1/theater/movies/", json=movie_data)
    assert response.status_code == 409
    expected_detail = f"A movie with the name '{movie_data['name']}', release year '{movie_data['year']}', and release time '{movie_data['time']}' already exists."
    assert response.json()["detail"] == expected_detail


@pytest.mark.asyncio
async def test_delete_movie_success(client, db_session, seed_database):
    """
    Test the `/movies/{movie_id}/` endpoint for successful movie deletion.
    """
    stmt = select(MovieModel).limit(1)
    result = await db_session.execute(stmt)
    movie = result.scalars().first()
    assert movie is not None
    movie_id = movie.id
    response = await client.delete(f"/api/v1/theater/movies/{movie_id}/")
    assert response.status_code == 204
    stmt_check = select(MovieModel).where(MovieModel.id == movie_id)
    result_check = await db_session.execute(stmt_check)
    deleted_movie = result_check.scalars().first()
    assert deleted_movie is None


@pytest.mark.asyncio
async def test_delete_movie_not_found(client):
    """
    Test the `/movies/{movie_id}/` endpoint with a non-existent movie ID.
    """
    non_existent_id = 99999
    response = await client.delete(
        f"/api/v1/theater/movies/{non_existent_id}/"
    )
    assert response.status_code == 404
    assert (
        response.json()["detail"] == "Movie with the given ID was not found."
    )


@pytest.mark.asyncio
async def test_update_movie_success(client, db_session, seed_database):
    """
    Test the `/movies/{movie_id}/` endpoint for successfully updating a movie's details.
    """
    stmt = select(MovieModel).limit(1)
    result = await db_session.execute(stmt)
    movie = result.scalars().first()
    assert movie is not None
    movie_id = movie.id
    update_data = {"name": "Updated Movie Name"}
    response = await client.patch(
        f"/api/v1/theater/movies/{movie_id}/", json=update_data
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Movie updated successfully."
    await db_session.rollback()
    stmt_check = select(MovieModel).where(MovieModel.id == movie_id)
    result_check = await db_session.execute(stmt_check)
    updated_movie = result_check.scalars().first()
    assert updated_movie.name == update_data["name"]


@pytest.mark.asyncio
async def test_update_movie_not_found(client):
    """
    Test the `/movies/{movie_id}/` endpoint with a non-existent movie ID.
    """
    non_existent_id = 99999
    update_data = {"name": "Non-existent Movie", "description": "No desc."}
    response = await client.patch(
        f"/api/v1/theater/movies/{non_existent_id}/", json=update_data
    )
    assert response.status_code == 404
    assert (
        response.json()["detail"] == "Movie with the given ID was not found."
    )
