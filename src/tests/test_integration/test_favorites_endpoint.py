# import pytest
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession

# from database.models import (
#     MovieModel,
#     FavoriteMovie,
#     UserModel,
#     GenreModel,
# )
# from database.models.movies import CertificationEnum


# @pytest.mark.asyncio
# async def test_get_user_favorites_empty(
#     client: AsyncClient, authenticated_user
# ):
#     """Test getting favorites when user has no favorites."""
#     response = await client.get("/api/v1/extra_functionality/favorites")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["movies"] == []
#     assert data["total_items"] == 0
#     assert data["total_pages"] == 0


# @pytest.mark.asyncio
# async def test_get_user_favorites_with_movies(
#     client: AsyncClient, authenticated_user, db_session: AsyncSession
# ):
#     """Test getting favorites when user has favorite movies."""

#     # Create certification
#     cert = CertificationModel(name=CertificationEnum.GENERAL_AUDIENCE)
#     db_session.add(cert)
#     await db_session.flush()

#     # Create test movies
#     movie1 = MovieModel(
#         uuid="test-uuid-1",
#         name="Test Movie 1",
#         year=2020,
#         time=120,
#         imdb=8.5,
#         votes=1000,
#         description="Test description 1",
#         price=9.99,
#         certification_id=cert.id,
#     )
#     movie2 = MovieModel(
#         uuid="test-uuid-2",
#         name="Another Movie",
#         year=2021,
#         time=90,
#         imdb=7.5,
#         votes=500,
#         description="Test description 2",
#         price=12.99,
#         certification_id=cert.id,
#     )

#     db_session.add_all([movie1, movie2])
#     await db_session.flush()

#     # Add movies to favorites
#     fav1 = FavoriteMovie(user_id=authenticated_user.id, movie_id=movie1.id)
#     fav2 = FavoriteMovie(user_id=authenticated_user.id, movie_id=movie2.id)
#     db_session.add_all([fav1, fav2])
#     await db_session.commit()

#     # Test getting favorites
#     response = await client.get("/api/v1/extra_functionality/favorites")
#     assert response.status_code == 200
#     data = response.json()

#     assert len(data["movies"]) == 2
#     assert data["total_items"] == 2
#     assert data["total_pages"] == 1

#     # Check movie data
#     movie_names = [movie["name"] for movie in data["movies"]]
#     assert "Test Movie 1" in movie_names
#     assert "Another Movie" in movie_names


# @pytest.mark.asyncio
# async def test_get_user_favorites_with_search(
#     client: AsyncClient, authenticated_user, db_session: AsyncSession
# ):
#     """Test searching in favorite movies."""

#     # Create certification
#     cert = CertificationModel(name=CertificationEnum.GENERAL_AUDIENCE)
#     db_session.add(cert)
#     await db_session.flush()

#     # Create test movies
#     movie1 = MovieModel(
#         uuid="test-uuid-1",
#         name="Action Movie",
#         year=2020,
#         time=120,
#         imdb=8.5,
#         votes=1000,
#         description="Great action film",
#         price=9.99,
#         certification_id=cert.id,
#     )
#     movie2 = MovieModel(
#         uuid="test-uuid-2",
#         name="Comedy Film",
#         year=2021,
#         time=90,
#         imdb=7.5,
#         votes=500,
#         description="Funny comedy",
#         price=12.99,
#         certification_id=cert.id,
#     )

#     db_session.add_all([movie1, movie2])
#     await db_session.flush()

#     # Add movies to favorites
#     fav1 = FavoriteMovie(user_id=authenticated_user.id, movie_id=movie1.id)
#     fav2 = FavoriteMovie(user_id=authenticated_user.id, movie_id=movie2.id)
#     db_session.add_all([fav1, fav2])
#     await db_session.commit()

#     # Test search
#     response = await client.get(
#         "/api/v1/extra_functionality/favorites?search=Action"
#     )
#     assert response.status_code == 200
#     data = response.json()

#     assert len(data["movies"]) == 1
#     assert data["movies"][0]["name"] == "Action Movie"


# @pytest.mark.asyncio
# async def test_get_user_favorites_pagination(
#     client: AsyncClient, authenticated_user, db_session: AsyncSession
# ):
#     """Test pagination in favorites."""

#     # Create certification
#     cert = CertificationModel(name=CertificationEnum.GENERAL_AUDIENCE)
#     db_session.add(cert)
#     await db_session.flush()

#     # Create multiple test movies
#     movies = []
#     for i in range(5):
#         movie = MovieModel(
#             uuid=f"test-uuid-{i}",
#             name=f"Movie {i}",
#             year=2020 + i,
#             time=120,
#             imdb=8.0,
#             votes=1000,
#             description=f"Description {i}",
#             price=9.99,
#             certification_id=cert.id,
#         )
#         movies.append(movie)

#     db_session.add_all(movies)
#     await db_session.flush()

#     # Add all movies to favorites
#     favorites = []
#     for movie in movies:
#         fav = FavoriteMovie(user_id=authenticated_user.id, movie_id=movie.id)
#         favorites.append(fav)

#     db_session.add_all(favorites)
#     await db_session.commit()

#     # Test pagination - first page
#     response = await client.get(
#         "/api/v1/extra_functionality/favorites?page=1&per_page=3"
#     )
#     assert response.status_code == 200
#     data = response.json()

#     assert len(data["movies"]) == 3
#     assert data["total_items"] == 5
#     assert data["total_pages"] == 2
#     assert data["next_page"] is not None
#     assert data["prev_page"] is None

#     # Test pagination - second page
#     response = await client.get(
#         "/api/v1/extra_functionality/favorites?page=2&per_page=3"
#     )
#     assert response.status_code == 200
#     data = response.json()

#     assert len(data["movies"]) == 2
#     assert data["total_items"] == 5
#     assert data["total_pages"] == 2
#     assert data["next_page"] is None
#     assert data["prev_page"] is not None
