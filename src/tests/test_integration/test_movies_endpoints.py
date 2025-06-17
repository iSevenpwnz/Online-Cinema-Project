import random
import uuid
import datetime
from copy import copy
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy import select, func, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import UserGroupModel, UserGroupEnum, UserModel
from database.models.movies import (
    MovieModel,
    GenreModel,
    StarModel,
    DirectorModel,
    CertificationModel, CertificationEnum,

)
from database.models.orders import OrderStatusEnum, Order, OrderItem


@pytest_asyncio.fixture
async def admin_user(db_session, client, jwt_manager):
    """Create a fake admin user"""

    admin_group = await db_session.scalar(
        select(UserGroupModel).where(UserGroupModel.name == UserGroupEnum.ADMIN)
    )
    if not admin_group:
        admin_group = UserGroupModel(name=UserGroupEnum.ADMIN)
        db_session.add(admin_group)
        await db_session.commit()
        await db_session.refresh(admin_group)

    admin = UserModel.create(
        email="admin@example.com",
        raw_password="AdminPassword123!",
        group_id=admin_group.id
    )
    admin.is_active = True
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    response = await client.post(
        "/api/v1/accounts/login/",
        json={"email": admin.email, "password": "AdminPassword123!"}
    )
    token = response.json()["access_token"]
    return admin, {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def movie_test(db_session):
    # Create certification if not exists
    cert = CertificationModel(name=CertificationEnum.GENERAL_AUDIENCE)
    genre = GenreModel(name="Action")
    star = StarModel(name="Star")
    director = DirectorModel(name="Director")
    db_session.add_all([cert, genre, star, director])
    await db_session.flush()

    movie_model = MovieModel(
        uuid=uuid.uuid4(),
        name="Bad IMDB",
        year=2023,
        time=120,
        imdb=8.0,
        votes=1000,
        meta_score=50,
        gross=100,
        description="Bad imdb. I didn't liked the movie. It's awfull",
        price=100,
        certification_id=cert.id,
        genres=[genre],
        stars=[star],
        directors=[director],
    )
    db_session.add(movie_model)
    await db_session.commit()
    await db_session.refresh(movie_model)

    movie_dict = {
        "uuid": str(uuid.uuid4()),
        "name": "Bad IMDB 2.0",
        "year": 2023,
        "time": 120,
        "imdb": 8.0,
        "votes": 1000,
        "meta_score": 50,
        "gross": 100,
        "description": "Bad imdb. I didn't liked the movie. It's awfull",
        "price": 100,
        "certification_id": 3,
        "genres": ["Action"],
        "stars": ["Star"],
        "directors": ["Director"]
    }
    return movie_model, movie_dict

class TestGenreEndpoints:
    """Test suite for genre-related API endpoints"""

    @pytest.mark.asyncio
    async def test_get_genres_with_counts(self, client, db_session, movie_test):
        """
        Test retrieving all genres with their movie counts.
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
        """
        response = await client.get("/api/v1/theater/genres/")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_genre_success(self, client, db_session, admin_user):
        """
        Test successful genre creation.
        """
        user, headers = admin_user
        genre_name = "Sci-Fi"
        response = await client.post(
            "/api/v1/theater/genres/",
            params={"genre_name": genre_name},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == genre_name

    @pytest.mark.asyncio
    async def test_create_genre_duplicate(self, client, db_session, admin_user):
        """
        Test duplicate genre creation attempt. Its not possible.
        """
        user, headers = admin_user
        genre_name = "Action"
        await client.post(
            "/api/v1/theater/genres/",
            params={"genre_name": genre_name},
            headers=headers
        )
        response = await client.post(
            "/api/v1/theater/genres/",
            params={"genre_name": genre_name},
            headers=headers
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_genre_trimmed_and_normalized(self, client, admin_user):
        """Whitespace should be trimmed in genre creation"""
        user, headers = admin_user
        response = await client.post(
            "/api/v1/theater/genres/",
            params={"genre_name": "  New Genre  "},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["name"].strip() == "New Genre"

    @pytest.mark.asyncio
    async def test_update_genre_success(self, client, db_session, movie_test, admin_user):
        """
        Test successful genre name update.
        """
        user, headers = admin_user
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        new_name = "UpdatedName"
        response = await client.put(
            f"/api/v1/theater/genres/{genre.id}",
            params={"new_name": new_name},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == new_name

    @pytest.mark.asyncio
    async def test_update_genre_to_existing_name(self, client, db_session, movie_test, admin_user):
        """
        Test updating genre to existing name.
        """
        user, headers = admin_user

        genres = (await db_session.execute(select(GenreModel).limit(2))).scalars().all()
        if len(genres) < 2:
            genre1 = GenreModel(name="Genre1")
            genre2 = GenreModel(name="Genre2")
            db_session.add_all([genre1, genre2])
            await db_session.commit()
            genres = (await db_session.execute(select(GenreModel).limit(2))).scalars().all()
        genre1, genre2 = genres

        response = await client.put(
            f"/api/v1/theater/genres/{genre1.id}",
            params={"new_name": genre2.name},
            headers=headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_genre_not_found(self, client, admin_user):
        """
        Should return 404 if genre not found
        """
        user, headers = admin_user
        response = await client.put(
            "/api/v1/theater/genres/999999",
            params={"new_name": "New Genre"},
            headers=headers
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Genre not found."

    @pytest.mark.asyncio
    async def test_delete_genre_success(self, client, db_session, movie_test, admin_user):
        """
        Test successful genre deletion.
        """
        user, headers = admin_user
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        response = await client.delete(f"/api/v1/theater/genres/{genre.id}", headers=headers)
        assert response.status_code in (200, 204)

    @pytest.mark.asyncio
    async def test_delete_genre_not_found(self, client, admin_user):
        """
        Should return 404 if genre not found
        """
        user, headers = admin_user
        response = await client.delete("/api/v1/theater/genres/999999", headers=headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "Genre not found."

    @pytest.mark.asyncio
    async def test_get_movies_by_genre_success(self, client, db_session, movie_test):
        """
        Test retrieving movies for specific genre.
        """
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        response = await client.get(f"/api/v1/theater/genres/{genre.id}/movies")
        assert response.status_code == 200
        assert "movies" in response.json()

    @pytest.mark.asyncio
    async def test_get_movies_by_nonexistent_genre(self, client):
        """
        Test retrieving movies for non-existent genre.
        """
        response = await client.get("/api/v1/theater/genres/99999/movies")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_movies_by_genre_empty(self, client, db_session):
        """
        Test retrieving movies for genre with no movies.
        """
        genre = GenreModel(name="EmptyGenre")
        db_session.add(genre)
        await db_session.commit()
        await db_session.refresh(genre)

        response = await client.get(f"/api/v1/theater/genres/{genre.id}/movies")

        assert response.status_code == 404 or response.json().get("movies") == []

    @pytest.mark.asyncio
    async def test_genres_search_filter(self, client, db_session):
        """
        Search genre by name
        """
        g = GenreModel(name="Superhero")
        db_session.add(g)
        await db_session.commit()
        resp = await client.get("/api/v1/theater/genres/?search=super")
        assert resp.status_code == 200
        assert any("Superhero" in genre["name"] for genre in resp.json())

    @pytest.mark.asyncio
    async def test_delete_genre_with_movies_linked(self, client, db_session, movie_test, admin_user):
        user, headers = admin_user
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        response = await client.delete(f"/api/v1/theater/genres/{genre.id}", headers=headers)
        assert response.status_code == 200


class TestStarEndpoints:
    """Test suite for star-related API endpoints"""

    @pytest.mark.asyncio
    async def test_create_star_success(self, client, db_session, admin_user):
        """
        Test successful star creation.
        """
        user, headers = admin_user
        star_name = "Will Smith"
        response = await client.post("/api/v1/theater/stars/", params={"star_name": star_name}, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == star_name

    @pytest.mark.asyncio
    async def test_create_star_duplicate(self, client, db_session, admin_user):
        """
        Test duplicate star creation attempt. It's not possible.
        """
        user, headers = admin_user
        star_name = "Star"
        await client.post(
            "/api/v1/theater/stars/",
            params={"star_name": star_name},
            headers=headers
        )
        response = await client.post(
            "/api/v1/theater/stars/",
            params={"star_name": star_name},
            headers=headers
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_star_trimmed_and_normalized(self, client, admin_user):
        """
        Whitespace should be trimmed in star creation
        """
        user, headers = admin_user
        response = await client.post(
            "/api/v1/theater/stars/",
            params={"star_name": "  Chris Hemsworth  "},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["name"].strip() == "Chris Hemsworth"

    @pytest.mark.asyncio
    async def test_get_stars_list(self, client, db_session, movie_test):
        """
        Test retrieving list of all stars.
        """
        response = await client.get("/api/v1/theater/stars/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_stars_empty_database(self, client):
        """
        Test retrieving stars when database is empty.
        """
        response = await client.get("/api/v1/theater/stars/")
        assert response.status_code == 200
        assert response.json() == [] or response.json() == {}

    @pytest.mark.asyncio
    async def test_get_star_detail(self, client, db_session, movie_test):
        """
        Test retrieving star details.
        """
        star = (await db_session.execute(select(StarModel).limit(1))).scalars().first()
        response = await client.get(f"/api/v1/theater/stars/{star.id}")
        assert response.status_code == 200
        assert "movie" in response.json()

    @pytest.mark.asyncio
    async def test_get_star_detail_not_found(self, client):
        """
        Should return 404 if star not found
        """
        response = await client.get("/api/v1/theater/stars/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Star not found."

    @pytest.mark.asyncio
    async def test_update_star_success(self, client, db_session, movie_test, admin_user):
        """
        Test successful star name update.
        """
        user, headers = admin_user
        star = (await db_session.execute(select(StarModel).limit(1))).scalars().first()
        new_name = "Jackie Chan"
        response = await client.put(
            f"/api/v1/theater/stars/{star.id}",
            params={"new_name": new_name},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == new_name

    @pytest.mark.asyncio
    async def test_update_star_to_existing_name(self, client, db_session, admin_user):
        user, headers = admin_user
        s1 = StarModel(name="StarA")
        s2 = StarModel(name="StarB")
        db_session.add_all([s1, s2])
        await db_session.commit()
        response = await client.put(
            f"/api/v1/theater/stars/{s1.id}",
            params={"new_name": s2.name},
            headers=headers
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_star_not_found(self, client, admin_user):
        """
        Should return 404 if star not found
        """
        user, headers = admin_user
        response = await client.put(
            "/api/v1/theater/stars/999999",
            params={"new_name": "New Star"},
            headers=headers
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Star not found."

    @pytest.mark.asyncio
    async def test_delete_star_success(self, client, db_session, movie_test, admin_user):
        """
        Test successful star deletion.
        """
        user, headers = admin_user
        star = (await db_session.execute(select(StarModel).limit(1))).scalars().first()
        response = await client.delete(f"/api/v1/theater/stars/{star.id}", headers=headers)
        assert response.status_code in (200, 204)

    @pytest.mark.asyncio
    async def test_delete_star_not_found(self, client, admin_user):
        """
        Test deleting non-existent star.
        """
        user, headers = admin_user
        response = await client.delete(
            "/api/v1/theater/stars/999999",
            headers=headers
        )
        assert response.status_code in (404, 422)


class TestMovieListing:
    """Test suite for movie listing and search functionality"""

    @pytest.mark.asyncio
    async def test_get_movies_empty_database(self, client):
        """
        Test retrieving movies when database is empty.
        """
        response = await client.get("/api/v1/theater/movies/")
        assert response.status_code == 404
        assert response.json() == {"detail": "No movies found."}

    @pytest.mark.asyncio
    async def test_get_movies_default_pagination(self, client, movie_test, db_session):
        """
        Test retrieving movies with default pagination.
        """
        for i in range(9):
            movie = MovieModel(
                name=f"Test Movie {i}",
                year=2020 + i,
                imdb=5.5,
                price=10.0,
                description="desc",
                certification_id=1,
                time=120,
                votes=1000,
                uuid=uuid.uuid4(),
            )
            db_session.add(movie)
        await db_session.commit()

        response = await client.get("/api/v1/theater/movies/")
        assert response.status_code == 200
        response_data = response.json()

        assert len(response_data["movies"]) == 10
        assert response_data["total_pages"] >= 1
        assert response_data["total_items"] >= 10

    @pytest.mark.asyncio
    async def test_get_movie_by_id_success(self, client, db_session, movie_test):
        movie, _ = movie_test
        movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
        response = await client.get(f"/api/v1/theater/movies/{movie.id}/")
        assert response.status_code == 200
        assert response.json()["id"] == movie.id

    @pytest.mark.asyncio
    async def test_get_movies_sorted_correctly(self, client, db_session, movie_test):
        """
        Test movies are returned in correct sort order.
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
                uuid=uuid.UUID(data["uuid"]),
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
    async def test_get_movies_custom_pagination(self, client, db_session):

        for i in range(8):
            movie = MovieModel(
                name=f"Test Movie {i}",
                year=2020 + i,
                imdb=7.0 + i,
                price=10.0,
                description="desc",
                certification_id=1,
                time=120,
                votes=1000,
                uuid=uuid.uuid4(),
            )
            db_session.add(movie)
        await db_session.commit()

        page = 2
        page_size = 5
        response = await client.get(
            f"/api/v1/theater/movies/?page={page}&page_size={page_size}"
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["movies"]) == 3

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
    async def test_get_movies_page_size_maximum(self, client, movie_test):
        """
        Test retrieving movies with maximum allowed page size.
        Should return no more than maximum allowed movies per page.
        """
        movie, _ = movie_test
        response = await client.get("/api/v1/theater/movies/?page=1&per_page=20")
        assert response.status_code == 200
        assert len(response.json()["movies"]) <= 20

    @pytest.mark.asyncio
    async def test_get_movies_page_exceeds_maximum(self, client, db_session, movie_test):
        """
        Test retrieving movies with page number exceeding maximum.
        Should return 404 Not Found when page number is too large.
        """
        movie, _ = movie_test
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
            uuid=uuid.uuid4(),
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
                uuid=uuid.uuid4(),
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
                uuid=uuid.uuid4(),
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

    @pytest.mark.asyncio
    async def test_get_movie_list_no_movies(self, client, db_session):
        """No movies in DB -> 404"""
        await db_session.execute(delete(MovieModel))
        await db_session.commit()
        response = await client.get("/api/v1/theater/movies/")
        assert response.status_code == 404
        assert response.json()["detail"] == "No movies found."

    @pytest.mark.asyncio
    async def test_get_movies_combined_filter_sort_search(self,client, db_session):
        response = await client.get(
            "/api/v1/theater/movies/?filter_by=2023&search=Test&sort_by=price"
        )
        assert response.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_get_movies_by_genre_pagination(self, client, db_session, movie_test):
        movie, _ = movie_test
        genre = (await db_session.execute(select(GenreModel).limit(1))).scalars().first()
        response = await client.get(f"/api/v1/theater/genres/{genre.id}/movies?page=2&page_size=1")
        assert response.status_code in (200, 404)


class TestMovieCRUD:
    """Test suite for movie CRUD operations"""

    @pytest.mark.asyncio
    async def test_get_movie_by_id_success(self, client, db_session, movie_test):
        """
        Test retrieving movie by ID.
        Should return 200 OK with movie details when movie exists.
        """
        movie, _ = movie_test
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
    async def test_create_movie_success(self, client, db_session, admin_user):
        """
        Test successful movie creation.
        Should return 201 Created with movie data when valid data provided.
        """
        user, headers = admin_user
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
        response = await client.post(
            "/api/v1/theater/movies/",
            json=movie_data,
            headers=headers
        )

        assert response.status_code == 201
        assert response.json()["name"] == movie_data["name"]

    @pytest.mark.asyncio
    async def test_create_movie_duplicate(self, client, db_session, movie_test, admin_user):
        """
        Test duplicate movie creation attempt.
        """
        user, headers = admin_user
        movie, _ = movie_test

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
            "stars": ["Star"],
            "directors": ["Director"],
        }
        response = await client.post(
            "/api/v1/theater/movies/",
            json=movie_data,
            headers=headers
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_movie_with_nonexistent_certification(self, client, admin_user, movie_test):
        """
        Test creating movie with non-existent certification.
        """
        user, headers = admin_user
        _, movie_data = movie_test
        movie_data["certification_id"] = 999
        response = await client.post(
            "/api/v1/theater/movies/",
            json=movie_data,
            headers=headers
        )

        assert response.status_code == 400
        assert "Certification ID" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_movie_success(self, client, db_session, admin_user, movie_test):
        """
        Test successful movie update.
        """
        user, headers = admin_user

        new_genre = GenreModel(name="New Genre")
        new_star = StarModel(name="New Star")
        new_director = DirectorModel(name="New Director")

        db_session.add_all([new_genre, new_star, new_director])
        await db_session.commit()

        new_movie, _ = movie_test
        update_data = {
            "name": "Updated Movie Name",
            "time": 120,
            "genres": ["New Genre"],
            "stars": ["New Star"],
            "directors": ["New Director"],
        }

        response = await client.patch(
            f"/api/v1/theater/movies/{new_movie.id}/",
            json=update_data,
            headers=headers
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == update_data["name"]
        assert "New Genre" in data["genres"]
        assert "New Star" in data["stars"]
        assert "New Director" in data["directors"]

    @pytest.mark.asyncio
    async def test_update_nonexistent_movie(self, client, admin_user):
        """
        Test updating non-existent movie.
        """
        user, headers = admin_user
        update_data = {"name": "New Name"}
        response = await client.patch(
            "/api/v1/theater/movies/999999/",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Movie not found"}

    @pytest.mark.asyncio
    async def test_update_movie_invalid_value(self, client, db_session, admin_user, movie_test):
        """PATCH with invalid value"""
        user, headers = admin_user
        movie_data, _ = movie_test
        db_session.add(movie_data)
        await db_session.commit()
        update_data = {"price": "not_a_number"}
        response = await client.patch(
            f"/api/v1/theater/movies/{movie_data.id}/",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 422
        error_msgs = [err["msg"] for err in response.json().get("detail", [])]
        assert any("valid decimal" in msg for msg in error_msgs)

    @pytest.mark.asyncio
    async def test_patch_movie_empty_payload(self, client, db_session, admin_user, movie_test):
        """
        Test updating movie with empty payload.
        """
        user, headers = admin_user
        movie, _ = movie_test
        movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
        response = await client.patch(
            f"/api/v1/theater/movies/{movie.id}/",
            json={},
            headers=headers,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_patch_movie_strip_fields(self, client, db_session, admin_user, movie_test):
        """
        Ensure genres/stars/directors are normalized and trimmed
        """
        user, headers = admin_user
        movie, _ = movie_test

        genre = GenreModel(name="Comedy")
        star = StarModel(name="Tom Hanks")
        director = DirectorModel(name="Steven Spielberg")

        db_session.add_all([genre, star, director])
        await db_session.commit()

        data = {
            "genres": ["  comedy  "],
            "stars": ["  tom hanks  "],
            "directors": ["  steven spielberg  "]
        }

        resp = await client.patch(
            f"/api/v1/theater/movies/{movie.id}/",
            json=data,
            headers=headers
        )

        assert resp.status_code == 200
        response_data = resp.json()

        assert "Comedy" in response_data["genres"]
        assert "Tom Hanks" in response_data["stars"]
        assert "Steven Spielberg" in response_data["directors"]

    @pytest.mark.asyncio
    async def test_delete_movie_success(self, client, db_session, admin_user, movie_test):
        """
        Test successful movie deletion.
        """
        user, headers = admin_user
        movie = (await db_session.execute(select(MovieModel).limit(1))).scalars().first()
        response = await client.delete(
            f"/api/v1/theater/movies/{movie.id}/",
            headers=headers
        )
        assert response.status_code == 204
        deleted_movie = (await db_session.execute(
            select(MovieModel).where(MovieModel.id == movie.id)
        )).scalars().first()
        assert deleted_movie is None

    @pytest.mark.asyncio
    async def test_delete_movie_with_paid_orders(self, client, db_session, admin_user, movie_test):
        """
        Test deleting movie with paid orders. It's not possible.
        """
        user, headers = admin_user
        movie_data, _ = movie_test
        db_session.add(movie_data)
        await db_session.commit()

        order = Order(
            user_id=1,
            created_at=datetime.date.today(),
            status=OrderStatusEnum.PAID,
            total_amount=movie_data.price,
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)

        order_item = OrderItem(
            order_id=order.id,
            movie_id=movie_data.id,
            price_at_order=movie_data.price,
        )
        db_session.add(order_item)
        await db_session.commit()

        response = await client.delete(
            f"/api/v1/theater/movies/{movie_data.id}/",
            headers=headers
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Cannot delete movie - it appears in paid orders."
        }

        existing_movie = await db_session.get(MovieModel, movie_data.id)
        assert existing_movie is not None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_movie(self, client, admin_user):
        """
        Test deleting non-existent movie.
        """
        user, header = admin_user
        response = await client.delete(
            "/api/v1/theater/movies/999999/",
            headers=header
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Movie with the given ID was not found."}


class TestMovieValidation:
    """Test suite for movie data validation"""

    @pytest.mark.asyncio
    async def test_create_movie_invalid_imdb(self, client, db_session, admin_user, movie_test):
        """
        Test creating movie with invalid IMDB rating.
        """
        user, header = admin_user

        _, movie_data = movie_test
        movie_data["imdb"] = 13.0
        response = await client.post(
            "/api/v1/theater/movies/",
            json=movie_data,
            headers=header
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_movie_invalid_time(self, client, db_session, admin_user, movie_test):
        """
        Test creating movie with invalid duration.
        """
        user, header = admin_user

        _, movie_data = movie_test
        movie_data["time"] = 5
        response = await client.post(
            "/api/v1/theater/movies/",
            json=movie_data,
            headers=header
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_movie_missing_required_fields(self, client, admin_user):
        """
        Test creating movie with missing required fields. It's not possible.
        """
        user, header = admin_user
        movie_data = {"name": "NoYear"}
        response = await client.post(
            "/api/v1/theater/movies/",
            json=movie_data,
            headers=header
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_patch_movie_forbidden_field(
            self,
            client,
            db_session,
            admin_user,
            movie_test,
    ):
        """
        Test updating forbidden movie field. You cannot add a new field to a movie.
        """
        user, header = admin_user
        movie, _ = movie_test

        db_session.add(movie)
        await db_session.commit()

        response = await client.patch(
            f"/api/v1/theater/movies/{movie.id}/",
            json={"forbidden": 123},
            headers=header,
        )
        assert response.status_code == 422

