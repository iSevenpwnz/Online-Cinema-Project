import random
import uuid
import datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func, insert
from sqlalchemy.orm import joinedload

from database.models.movies import (
    MovieModel,
    GenreModel,
    StarModel,
    DirectorModel,
    CertificationModel,

)
from database.models.orders import OrderStatusEnum, Order, OrderItem


class TestGenreEndpoints:
    """Test suite for genre-related API endpoints"""

    @pytest.mark.asyncio
    async def test_get_genres_with_counts(self, client, db_session, seed_database):
        """
        Test retrieving all genres with their movie counts.
        Should return 200 OK with list of genres containing id, name and movie_count
        when genres exist in database.
        """
        response = await client.get("/api/v1/theater/genres/")
        assert response.status_code == 200
        genres = response.json()
        assert isinstance(genres, list)
        assert all("id" in g and "name" in g and "movie_count" in g for g in genres)

    @pytest.mark.asyncio
    async def test_get_genres_empty_database(self, client, db_session):
        """
        Test retrieving genres when database is empty.
        Should return 404 Not Found when no genres exist.
        """
        response = await client.get("/api/v1/theater/genres/")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_genre_success(self, client, db_session):
        """
        Test successful genre creation.
        Should return 200 OK with created genre data when valid name provided.
        """
        genre_name = "Sci-Fi"
        response = await client.post("/api/v1/theater/genres/", params={"genre_name": genre_name})
        assert response.status_code == 200
        assert response.json()["name"] == genre_name

    @pytest.mark.asyncio
    async def test_create_genre_duplicate(self, client, db_session):
        """
        Test duplicate genre creation attempt.
        Should return 400 Bad Request when trying to create genre with existing name.
        """
        genre_name = "Comedy"
        await client.post("/api/v1/theater/genres/", params={"genre_name": genre_name})
        response = await client.post("/api/v1/theater/genres/", params={"genre_name": genre_name})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_genre_success(self, client, db_session, seed_database):
        """
        Test successful genre name update.
        Should return 200 OK with updated genre data when valid new name provided.
        """
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        new_name = "UpdatedName"
        response = await client.put(
            f"/api/v1/theater/genres/{genre.id}",
            params={"new_name": new_name}
        )
        assert response.status_code == 200
        assert response.json()["name"] == new_name

    @pytest.mark.asyncio
    async def test_update_genre_to_existing_name(self, client, db_session, seed_database):
        """
        Test updating genre to existing name.
        Should return 400 Bad Request when trying to rename genre to already existing name.
        """
        genres = (await db_session.execute(select(GenreModel).limit(2))).scalars().all()
        genre1, genre2 = genres
        response = await client.put(
            f"/api/v1/theater/genres/{genre1.id}",
            params={"new_name": genre2.name}
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_genre_success(self, client, db_session, seed_database):
        """
        Test successful genre deletion.
        Should return 204 No Content when deleting existing genre.
        """
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        response = await client.delete(f"/api/v1/theater/genres/{genre.id}")
        assert response.status_code in (200, 204)

    @pytest.mark.asyncio
    async def test_get_movies_by_genre_success(self, client, db_session, seed_database):
        """
        Test retrieving movies for specific genre.
        Should return 200 OK with movies list when genre exists and has movies.
        """
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        response = await client.get(f"/api/v1/theater/genres/{genre.id}/movies")
        assert response.status_code == 200
        assert "movies" in response.json()

    @pytest.mark.asyncio
    async def test_get_movies_by_nonexistent_genre(self, client):
        """
        Test retrieving movies for non-existent genre.
        Should return 404 Not Found when genre doesn't exist.
        """
        response = await client.get("/api/v1/theater/genres/99999/movies")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_movies_by_genre_empty(self, client, db_session):
        """
        Test retrieving movies for genre with no movies.
        Should return 404 Not Found or empty movies list when genre has no movies.
        """
        response = await client.post("/api/v1/theater/genres/", params={"genre_name": "EmptyGenre"})
        genre_id = response.json()["id"]
        response = await client.get(f"/api/v1/theater/genres/{genre_id}/movies")
        assert response.status_code == 404 or response.json().get("movies") == []


class TestStarEndpoints:
    """Test suite for star-related API endpoints"""

    @pytest.mark.asyncio
    async def test_create_star_success(self, client, db_session):
        """
        Test successful star creation.
        Should return 200 OK with created star data when valid name provided.
        """
        star_name = "Will Smith"
        response = await client.post("/api/v1/theater/stars/", params={"star_name": star_name})
        assert response.status_code == 200
        assert response.json()["name"] == star_name

    @pytest.mark.asyncio
    async def test_create_star_duplicate(self, client, db_session):
        """
        Test duplicate star creation attempt.
        Should return 400 Bad Request when trying to create star with existing name.
        """
        star_name = "Brad Pitt"
        await client.post("/api/v1/theater/stars/", params={"star_name": star_name})
        response = await client.post("/api/v1/theater/stars/", params={"star_name": star_name})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_stars_list(self, client, db_session, seed_database):
        """
        Test retrieving list of all stars.
        Should return 200 OK with list of stars when stars exist.
        """
        response = await client.get("/api/v1/theater/stars/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_stars_empty_database(self, client):
        """
        Test retrieving stars when database is empty.
        Should return 200 OK with empty list when no stars exist.
        """
        response = await client.get("/api/v1/theater/stars/")
        assert response.status_code == 200
        assert response.json() == [] or response.json() == {}

    @pytest.mark.asyncio
    async def test_get_star_detail(self, client, db_session, seed_database):
        """
        Test retrieving star details.
        Should return 200 OK with star details including movie information.
        """
        star = (await db_session.execute(select(StarModel).limit(1))).scalars().first()
        response = await client.get(f"/api/v1/theater/stars/{star.id}")
        assert response.status_code == 200
        assert "movie" in response.json()

    @pytest.mark.asyncio
    async def test_update_star_success(self, client, db_session, seed_database):
        """
        Test successful star name update.
        Should return 200 OK with updated star data when valid new name provided.
        """
        star = (await db_session.execute(select(StarModel).limit(1))).scalars().first()
        new_name = "Jackie Chan"
        response = await client.put(
            f"/api/v1/theater/stars/{star.id}",
            params={"new_name": new_name}
        )
        assert response.status_code == 200
        assert response.json()["name"] == new_name

    @pytest.mark.asyncio
    async def test_delete_star_success(self, client, db_session, seed_database):
        """
        Test successful star deletion.
        Should return 200 OK or 204 No Content when deleting existing star.
        """
        star = (await db_session.execute(select(StarModel).limit(1))).scalars().first()
        response = await client.delete(f"/api/v1/theater/stars/{star.id}")
        assert response.status_code in (200, 204)

    @pytest.mark.asyncio
    async def test_delete_star_not_found(self, client):
        """
        Test deleting non-existent star.
        Should return 404 Not Found or 422 Unprocessable Entity when star doesn't exist.
        """
        response = await client.delete("/api/v1/theater/stars/999999")
        assert response.status_code in (404, 422)


class TestMovieListing:
    """Test suite for movie listing and search functionality"""

    @pytest.mark.asyncio
    async def test_get_movies_empty_database(self, client):
        """
        Test retrieving movies when database is empty.
        Should return 404 Not Found when no movies exist.
        """
        response = await client.get("/api/v1/theater/movies/")
        assert response.status_code == 404
        assert response.json() == {"detail": "No movies found."}

    @pytest.mark.asyncio
    async def test_get_movies_default_pagination(self, client, seed_database):
        """
        Test retrieving movies with default pagination.
        Should return 200 OK with 10 movies per page and pagination metadata.
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

    @pytest.mark.asyncio
    async def test_get_movies_sorted_correctly(self, client, db_session, seed_database):
        """
        Test movies are returned in correct sort order.
        Should return movies sorted by ID in descending order.
        """
        response = await client.get("/api/v1/theater/movies/?page=1&per_page=10")
        assert response.status_code == 200
        response_data = response.json()
        stmt = select(MovieModel).order_by(MovieModel.id.desc()).limit(10)
        expected_movies = (await db_session.execute(stmt)).scalars().all()
        expected_movie_ids = [movie.id for movie in expected_movies]
        returned_movie_ids = [movie["id"] for movie in response_data["movies"]]
        assert returned_movie_ids == expected_movie_ids

    async def test_sorting(self, client, db_session):
        """Test different sorting options"""
        movies_data = [
            {
                "name": "Cheap",
                "price": 5,
                "year": 2020,
                "imdb": 7.0,
                "time": 120,
                "votes": 1000,
                "description": "Test",
                "certification_id": 1,
                "uuid": str(uuid.uuid4())
            },
            {
                "name": "Medium",
                "price": 10,
                "year": 2015,
                "imdb": 8.0,
                "time": 110,
                "votes": 2000,
                "description": "Test",
                "certification_id": 1,
                "uuid": str(uuid.uuid4())
            },
            {
                "name": "Expensive",
                "price": 15,
                "year": 2010,
                "imdb": 9.0,
                "time": 100,
                "votes": 3000,
                "description": "Test",
                "certification_id": 1,
                "uuid": str(uuid.uuid4())
            },
        ]

        for data in movies_data:
            movie = MovieModel(
                uuid=data["uuid"],
                name=data["name"],
                year=data["year"],
                time=data["time"],
                imdb=data["imdb"],
                votes=data["votes"],
                description=data["description"],
                price=data["price"],
                certification_id=data["certification_id"]
            )
            db_session.add(movie)
        await db_session.commit()

        response = await client.get("/api/v1/theater/movies/?sort_by=price")
        data = response.json()
        assert [float(m["price"]) for m in data["movies"]] == [5.0, 10.0, 15.0]

        response = await client.get("/api/v1/theater/movies/?sort_by=year")
        data = response.json()
        assert [m["year"] for m in data["movies"]] == [2010, 2015, 2020]

        response = await client.get("/api/v1/theater/movies/?sort_by=imdb")
        data = response.json()
        assert [m["imdb"] for m in data["movies"]] == [7.0, 8.0, 9.0]



    @pytest.mark.asyncio
    async def test_get_movies_custom_pagination(self, client, seed_database):
        """
        Test retrieving movies with custom pagination.
        Should return correct number of movies per page and proper pagination links.
        """
        page = 2
        page_size = 5
        response = await client.get(
            f"/api/v1/theater/movies/?page={page}&page_size={page_size}"
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["movies"]) == page_size
        assert response_data["total_pages"] > 0
        assert response_data["total_items"] > 0
        if page > 1:
            assert response_data["prev_page"] is not None
        if page < response_data["total_pages"]:
            assert response_data["next_page"] is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "page, page_size, expected_detail",
        [
            (0, 10, "Input should be greater than or equal to 1"),
            (1, 0, "Input should be greater than or equal to 1"),
            (0, 0, "Input should be greater than or equal to 1"),
        ],
    )
    async def test_get_movies_invalid_pagination(
            self, client, page, page_size, expected_detail
    ):
        """
        Test retrieving movies with invalid pagination parameters.
        Should return 422 Unprocessable Entity with validation errors.
        """
        response = await client.get(
            f"/api/v1/theater/movies/?page={page}&page_size={page_size}"
        )
        assert response.status_code == 422
        assert any(
            expected_detail in error["msg"] for error in response.json()["detail"]
        )

    @pytest.mark.asyncio
    async def test_get_movies_page_size_maximum(self, client, seed_database):
        """
        Test retrieving movies with maximum allowed page size.
        Should return no more than maximum allowed movies per page.
        """
        response = await client.get("/api/v1/theater/movies/?page=1&per_page=20")
        assert response.status_code == 200
        assert len(response.json()["movies"]) <= 20

    @pytest.mark.asyncio
    async def test_get_movies_page_exceeds_maximum(self, client, db_session, seed_database):
        """
        Test retrieving movies with page number exceeding maximum.
        Should return 404 Not Found when page number is too large.
        """
        per_page = 10
        total_movies = (await db_session.execute(select(func.count(MovieModel.id)))).scalar_one()
        max_page = (total_movies + per_page - 1) // per_page
        response = await client.get(
            f"/api/v1/theater/movies/?page={max_page + 1}&per_page={per_page}"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_movies_filter_and_search(self, client, db_session):
        """
        Test filtering and searching movies.
        Should return movies matching filter and search criteria.
        """
        certification = CertificationModel(id=1, name="PG")
        star = StarModel(name="Test Star")
        director = DirectorModel(name="Test Director")
        db_session.add_all([certification, star, director])
        await db_session.commit()

        movie = MovieModel(
            uuid=str(uuid.uuid4()),
            name="Test Movie",
            year=2023,
            time=120,
            imdb=8.0,
            votes=100,
            meta_score=85,
            gross=5000000,
            description="This is a test description",
            price=15.0,
            certification_id=certification.id,
            stars=[star],
            directors=[director],
        )
        db_session.add(movie)
        await db_session.commit()

        response = await client.get(
            "/api/v1/theater/movies/?filter_by=2023&search=Test&page=1&page_size=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["movies"]) > 0

        for m in data["movies"]:
            name_contains = "Test" in m.get("name", "")
            description_contains = "Test" in m.get("description", "")
            stars_contains = any("Test" in s.get("name", "") for s in m.get("stars", []))
            directors_contains = any("Test" in d.get("name", "") for d in m.get("directors", []))
            assert any([name_contains, description_contains, stars_contains, directors_contains])

    async def test_filter_by_imdb(self, client, db_session):
        """Test filtering by IMDB rating"""
        certification = CertificationModel(id=1, name="PG")
        star = StarModel(name="Test Star")
        director = DirectorModel(name="Test Director")
        db_session.add_all([certification, star, director])
        await db_session.commit()

        for rating in [6.0, 7.0, 8.0]:
            movie = MovieModel(
                uuid=str(uuid.uuid4()),
                name=f"Movie {rating}",
                year=2020,
                time=120,
                imdb=rating,
                votes=100,
                meta_score=85,
                gross=5000000,
                description="This is a test description",
                price=15.0,
                certification_id=certification.id,
                stars=[star],
                directors=[director],
            )
            db_session.add(movie)
        await db_session.commit()

        response = await client.get("/api/v1/theater/movies/?filter_by=7.5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["movies"]) == 1
        assert data["movies"][0]["imdb"] == 8.0

    async def test_filter_by_year(self, client, db_session):
        """Test filtering by year"""
        certification = CertificationModel(id=1, name="PG")
        star = StarModel(name="Test Star")
        director = DirectorModel(name="Test Director")
        db_session.add_all([certification, star, director])
        await db_session.commit()

        for year in [2010, 2015, 2020]:
            movie = MovieModel(
                uuid=str(uuid.uuid4()),
                name=f"Some Movie",
                year=year,
                time=120,
                imdb=8.3,
                votes=100,
                meta_score=85,
                gross=5000000,
                description="This is a test description",
                price=15.0,
                certification_id=certification.id,
                stars=[star],
                directors=[director],
            )
            db_session.add(movie)
        await db_session.commit()

        response = await client.get("/api/v1/theater/movies/?filter_by=2015")
        assert response.status_code == 200
        data = response.json()
        assert len(data["movies"]) == 1
        assert data["movies"][0]["year"] == 2015


class TestMovieCRUD:
    """Test suite for movie CRUD operations"""

    @pytest.mark.asyncio
    async def test_get_movie_by_id_success(self, client, db_session, seed_database):
        """
        Test retrieving movie by ID.
        Should return 200 OK with movie details when movie exists.
        """
        movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
        response = await client.get(f"/api/v1/theater/movies/{movie.id}/")
        assert response.status_code == 200
        assert response.json()["id"] == movie.id
        assert response.json()["name"] == movie.name

    @pytest.mark.asyncio
    async def test_get_movie_by_id_not_found(self, client):
        """
        Test retrieving non-existent movie by ID.
        Should return 404 Not Found when movie doesn't exist.
        """
        response = await client.get("/api/v1/theater/movies/999999/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Movie with the given ID was not found."}

    @pytest.mark.asyncio
    async def test_create_movie_success(self, client, db_session):
        """
        Test successful movie creation.
        Should return 201 Created with movie data when valid data provided.
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
            "price": "100.0",
            "certification_id": 1,
            "genres": ["Action", "Adventure"],
            "stars": ["John Doe", "Jane Doe"],
            "directors": ["Some Director"],
        }
        response = await client.post("/api/v1/theater/movies/", json=movie_data)

        assert response.status_code == 201
        assert response.json()["name"] == movie_data["name"]

    @pytest.mark.asyncio
    async def test_create_movie_duplicate(self, client, db_session, seed_database):
        """
        Test duplicate movie creation attempt.
        Should return 409 Conflict when trying to create movie with same name and year.
        """
        existing_movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
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
            "genres": ["Action"],
            "stars": ["Some Star"],
            "directors": ["Some Director"],
        }
        response = await client.post("/api/v1/theater/movies/", json=movie_data)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_movie_with_nonexistent_certification(self, client):
        """
        Test creating movie with non-existent certification.
        Should return 400 Bad Request when certification doesn't exist.
        """
        movie_data = {
            "uuid": str(uuid.uuid4()),
            "name": "Test Movie",
            "year": 2023,
            "time": 90,
            "imdb": 7.5,
            "votes": 100,
            "meta_score": 80,
            "gross": 1000,
            "description": "This is a test movie description.",
            "price": "10.00",
            "certification_id": 9999,
            "genres": ["Action"],
            "stars": ["Some Star"],
            "directors": ["Some Director"],
        }
        response = await client.post("/api/v1/theater/movies/", json=movie_data)
        assert response.status_code == 400
        assert "Certification ID" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_movie_success(self, client, db_session):
        """
        Test successful movie update.
        Should return 200 OK with updated movie data when valid updates provided.
        """
        certification = await db_session.get(CertificationModel, 1)
        if not certification:
            certification = CertificationModel(id=1, name="PG-13")
            db_session.add(certification)
            await db_session.commit()

        genre = GenreModel(name="Action")
        star = StarModel(name="John Doe")
        director = DirectorModel(name="Jane Director")
        db_session.add_all([genre, star, director])
        await db_session.commit()
        await db_session.refresh(genre)
        await db_session.refresh(star)
        await db_session.refresh(director)

        new_movie = MovieModel(

            uuid=str(uuid.uuid4()),
            name="Original Movie",
            year=2020,
            time=100,
            imdb=7.5,
            votes=1000,
            meta_score=80,
            gross=500000,
            description="Test movie description",
            price=Decimal("10.00"),
            certification_id=1,
            genres=[genre],
            stars=[star],
            directors=[director]
        )
        db_session.add(new_movie)
        await db_session.commit()
        await db_session.refresh(new_movie)

        update_data = {
            "name": "Updated Movie Name",
            "time": new_movie.time,
            "genres": ["Action"],
            "stars": ["John Doe"],
            "directors": ["Jane Director"]
        }

        response = await client.patch(f"/api/v1/theater/movies/{new_movie.id}/", json=update_data)

        assert response.status_code == 200

        data = response.json()
        assert data["name"] == update_data["name"]
        assert "Action" in data["genres"]
        assert "John Doe" in data["stars"]
        assert "Jane Director" in data["directors"]

    @pytest.mark.asyncio
    async def test_update_nonexistent_movie(self, client):
        """
        Test updating non-existent movie.
        Should return 404 Not Found when movie doesn't exist.
        """
        update_data = {"name": "New Name"}
        response = await client.patch("/api/v1/theater/movies/999999/", json=update_data)
        assert response.status_code == 404
        assert response.json() == {"detail": "Movie not found"}

    @pytest.mark.asyncio
    async def test_patch_movie_empty_payload(self, client, db_session, seed_database):
        """
        Test updating movie with empty payload.
        Should return 200 OK when no updates provided (no-op).
        """
        movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
        response = await client.patch(
            f"/api/v1/theater/movies/{movie.id}/",
            json={}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_movie_success(self, client, db_session, seed_database):
        """
        Test successful movie deletion.
        Should return 204 No Content when movie exists and has no paid orders.
        """
        movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
        response = await client.delete(f"/api/v1/theater/movies/{movie.id}/")
        assert response.status_code == 204
        deleted_movie = (await db_session.execute(
            select(MovieModel).where(MovieModel.id == movie.id)
        )).scalars().first()
        assert deleted_movie is None

    @pytest.mark.asyncio
    async def test_delete_movie_with_paid_orders(self, client, db_session):
        """
        Test deleting movie with paid orders.
        Should return 400 Bad Request when movie appears in paid orders.
        """
        movie = MovieModel(
            uuid=str(uuid.uuid4()),
            name="Test Movie Paid",
            year=2023,
            time=100,
            imdb=7,
            votes=100,
            meta_score=80,
            gross=1000,
            description="desc",
            price=10,
            certification_id=1
        )
        db_session.add(movie)
        await db_session.commit()


        order = Order(
            user_id=1,
            created_at=datetime.date.today(),
            status=OrderStatusEnum.PAID,
            total_amount=10,
        )
        db_session.add(order)
        await db_session.commit()

        order_item = OrderItem(order_id=order.id, movie_id=movie.id)
        db_session.add(order_item)
        await db_session.commit()

        response = await client.delete(f"/api/v1/theater/movies/{movie.id}/")
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Cannot delete movie - it appears in paid orders."
        }


        existing_movie = await db_session.get(MovieModel, movie.id)
        assert existing_movie is not None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_movie(self, client):
        """
        Test deleting non-existent movie.
        Should return 404 Not Found when movie doesn't exist.
        """
        response = await client.delete("/api/v1/theater/movies/999999/")
        assert response.status_code == 404
        assert response.json() == {"detail": "Movie with the given ID was not found."}


class TestMovieValidation:
    """Test suite for movie data validation"""

    @pytest.mark.asyncio
    async def test_create_movie_invalid_imdb(self, client, db_session):
        """
        Test creating movie with invalid IMDB rating.
        Should return 422 Unprocessable Entity when IMDB rating is invalid (>10).
        """
        certification = CertificationModel(id=3, name="12A")
        db_session.add(certification)
        await db_session.commit()

        movie_data = {
            "uuid": str(uuid.uuid4()),
            "name": "Bad IMDB",
            "year": 2023,
            "time": 120,
            "imdb": 13.0,
            "votes": 1000,
            "meta_score": 50,
            "gross": 100,
            "description": "Bad imdb",
            "price": 100,
            "certification_id": 3,
            "genres": [{"name": "Action"}],
            "stars": [{"name": "X"}],
            "directors": [{"name": "Y"}]
        }
        response = await client.post("/api/v1/theater/movies/", json=movie_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_movie_invalid_time(self, client, db_session):
        """
        Test creating movie with invalid duration.
        Should return 422 Unprocessable Entity when duration is too short.
        """
        certification = CertificationModel(id=4, name="15")
        db_session.add(certification)
        await db_session.commit()

        movie_data = {
            "uuid": str(uuid.uuid4()),
            "name": "Bad Duration",
            "year": 2023,
            "time": 5,
            "imdb": 8,
            "votes": 1000,
            "meta_score": 50,
            "gross": 100,
            "description": "Bad time",
            "price": 100,
            "certification_id": 4,
            "genres": [{"name": "Action"}],
            "stars": [{"name": "X"}],
            "directors": [{"name": "Y"}]
        }
        response = await client.post("/api/v1/theater/movies/", json=movie_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_movie_missing_required_fields(self, client):
        """
        Test creating movie with missing required fields.
        Should return 422 Unprocessable Entity when required fields are missing.
        """
        movie_data = {"name": "NoYear"}
        response = await client.post("/api/v1/theater/movies/", json=movie_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_patch_movie_forbidden_field(self, client, db_session, seed_database):
        """
        Test updating forbidden movie field.
        Should return 422 Unprocessable Entity when trying to update non-updatable field.
        """
        movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
        response = await client.patch(
            f"/api/v1/theater/movies/{movie.id}/",
            json={"forbidden": 123}
        )
        assert response.status_code == 422