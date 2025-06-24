import uuid as uuid_module

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models.base import Base
from database.models.movies import (
    GenreModel,
    StarModel,
    DirectorModel,
    CertificationModel,
    MovieModel,
    CertificationEnum,
)


@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def test_genre_model_creation(db_session):
    """
    Verifies the creation of a GenreModel
    """
    genre = GenreModel(name="Action")
    db_session.add(genre)
    db_session.commit()

    assert genre.id is not None, "Genre ID should not be None after commit."
    assert genre.name == "Action", "Genre name should match the input value."
    assert repr(genre) == "Genre('Action')", "Genre __repr__ output is incorrect."


def test_genre_unique_constraint(db_session):
    """
    Verifies the uniqueness of the GenreModel
    """
    genre1 = GenreModel(name="Comedy")
    db_session.add(genre1)
    db_session.commit()

    genre2 = GenreModel(name="Comedy")
    db_session.add(genre2)

    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    assert "unique" in str(excinfo.value).lower(), (
        "Expected a unique constraint, but got an error for duplicate genre names."
    )


def test_star_model_creation(db_session):
    """
    Verifies the creation of a StarModel
    """
    star = StarModel(name="Tom Hanks")
    db_session.add(star)
    db_session.commit()

    assert star.id is not None, "Star ID should not be None after commit."
    assert star.name == "Tom Hanks", "Star name should match the input value."
    assert repr(star) == "Star('Tom Hanks')", "Star __repr__ output is incorrect."


def test_star_unique_constraint(db_session):
    """
    Verifies the uniqueness of the StarModel
    """
    star1 = StarModel(name="Leonardo DiCaprio")
    db_session.add(star1)
    db_session.commit()

    star2 = StarModel(name="Leonardo DiCaprio")
    db_session.add(star2)

    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    assert "unique" in str(excinfo.value).lower(), (
        "Expected a unique constraint, but got an error for duplicate star names."
    )


def test_director_model_creation(db_session):
    """
    Verifies the creation of a DirectorModel
    """
    director = DirectorModel(name="Steven Spielberg")
    db_session.add(director)
    db_session.commit()

    assert director.id is not None, "Director ID should not be None after commit."
    assert director.name == "Steven Spielberg", "Director name should match the input value."
    assert repr(director) == "Director('Steven Spielberg')", "Director __repr__ output is incorrect."


def test_director_unique_constraint(db_session):
    """
    Verifies the uniqueness of the DirectorModel
    """
    director1 = DirectorModel(name="Christopher Nolan")
    db_session.add(director1)
    db_session.commit()

    director2 = DirectorModel(name="Christopher Nolan")
    db_session.add(director2)

    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    assert "unique" in str(excinfo.value).lower(), (
        "Expected a unique constraint, but got an error for duplicate director names."
    )


def test_certification_model_creation(db_session):
    """
    Verifies the creation of a CertificationModel with a specific enum value.
    """
    cert = CertificationModel(name=CertificationEnum.PARENTS_STRONGLY_CAUTIONED)
    db_session.add(cert)
    db_session.commit()

    assert cert.id is not None, "Certification ID should not be None after commit."
    assert cert.name == CertificationEnum.PARENTS_STRONGLY_CAUTIONED, "Certification name should match the input value."


def test_certification_unique_constraint(db_session):
    """
    Verifies the uniqueness of a CertificationModel
    """
    cert1 = CertificationModel(name=CertificationEnum.RESTRICTED)
    db_session.add(cert1)
    db_session.commit()

    cert2 = CertificationModel(name=CertificationEnum.RESTRICTED)
    db_session.add(cert2)

    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    assert "unique" in str(excinfo.value).lower(), (
        "Expected a unique constraint, but got an error for duplicate certifications."
    )


def test_movie_model_creation(db_session):
    """
    Verifies the creation of a MovieModel
    """
    cert = CertificationModel(name=CertificationEnum.PARENTAL_GUIDANCE_SUGGESTED)
    genre = GenreModel(name="Adventure")
    star = StarModel(name="Harrison Ford")
    director = DirectorModel(name="George Lucas")

    db_session.add_all([cert, genre, star, director])
    db_session.commit()

    movie = MovieModel(
        uuid=uuid_module.uuid4(),
        name="Indiana Jones",
        year=1981,
        time=115,
        imdb=8.4,
        votes=500000,
        meta_score=85,
        gross=389.9,
        description="An archeology professor races against time to find the Ark of the Covenant.",
        price=Decimal("19.99"),
        certification_id=cert.id,
        genres=[genre],
        stars=[star],
        directors=[director]
    )

    db_session.add(movie)
    db_session.commit()

    assert movie.id is not None, "Movie ID should not be None after commit."
    assert movie.name == "Indiana Jones", "Movie name should match the input value."
    assert movie.year == 1981, "Movie year should match the input value."
    assert movie.certification == cert, "Movie certification relationship is incorrect."
    assert genre in movie.genres, "Movie genres relationship is incorrect."
    assert star in movie.stars, "Movie stars relationship is incorrect."
    assert director in movie.directors, "Movie directors relationship is incorrect."
    assert repr(movie) == "<Movie(name='Indiana Jones', year='1981', time=115)>", "Movie __repr__ output is incorrect."


def test_movie_unique_constraint(db_session):
    """
    Verifies the uniqueness of a MovieModel (by name, year, time)
    """
    cert = CertificationModel(name=CertificationEnum.PARENTAL_GUIDANCE_SUGGESTED)
    db_session.add(cert)
    db_session.commit()

    movie1 = MovieModel(
        uuid=uuid_module.uuid4(),
        name="Back to the Future",
        year=1985,
        time=116,
        imdb=8.5,
        votes=1000000,
        description="A teenager is sent back in time.",
        price=Decimal("14.99"),
        certification_id=cert.id
    )

    movie2 = MovieModel(
        uuid=uuid_module.uuid4(),
        name="Back to the Future",
        year=1985,
        time=116,
        imdb=8.5,
        votes=1000000,
        description="A teenager is sent back in time.",
        price=Decimal("14.99"),
        certification_id=cert.id
    )

    db_session.add(movie1)
    db_session.commit()
    db_session.add(movie2)

    with pytest.raises(Exception) as excinfo:
        db_session.commit()
    assert (
            "unique" in str(excinfo.value).lower()
            or "UNIQUE" in str(excinfo.value)
            or "constraint" in str(excinfo.value).lower()
    ), (
        "Expected a unique constraint violation error when adding two movies with identical name, year, and time."
    )


def test_movie_default_order_by():
    """
    Verifies that the default_order_by method returns the correct descending order( by movie id)
    """
    order_by = MovieModel.default_order_by()
    expected = [MovieModel.id.desc()]

    assert [str(x) for x in order_by] == [str(x) for x in expected], "Default order movie by id is incorrect."


def test_movie_genre_association(db_session):
    """
    Verifies the many-to-many association between MovieModel and GenreModel.
    """
    movie = MovieModel(
        uuid=uuid_module.uuid4(),
        name="The Matrix",
        year=1999,
        time=136,
        imdb=8.7,
        votes=1500000,
        description="A computer hacker learns about the true nature of reality.",
        price=Decimal("12.99"),
        certification_id=1
    )

    genre1 = GenreModel(name="Sci-Fi")
    genre2 = GenreModel(name="Action")

    movie.genres.extend([genre1, genre2])

    db_session.add_all([movie, genre1, genre2])
    db_session.commit()

    assert len(movie.genres) == 2, "Movie should be associated with two genres."
    assert movie in genre1.movies, "Genre1 should be linked with the movie."
    assert movie in genre2.movies, "Genre2 should be linked with the movie."


def test_movie_star_association(db_session):
    """
    Verifies the many-to-many association between MovieModel and StarModel.
    """
    movie = MovieModel(
        uuid=uuid_module.uuid4(),
        name="Inception",
        year=2010,
        time=148,
        imdb=8.8,
        votes=2000000,
        description="A thief who steals corporate secrets through dream-sharing technology.",
        price=Decimal("15.99"),
        certification_id=1
    )

    star1 = StarModel(name="Leonardo DiCaprio")
    star2 = StarModel(name="Joseph Gordon-Levitt")

    movie.stars.extend([star1, star2])

    db_session.add_all([movie, star1, star2])
    db_session.commit()

    assert len(movie.stars) == 2, "Movie should be associated with two stars."
    assert movie in star1.movies, "Star1 should be linked with the movie."
    assert movie in star2.movies, "Star2 should be linked with the movie."


def test_movie_director_association(db_session):
    """
    Verifies the many-to-many association between MovieModel and DirectorModel.
    """
    movie = MovieModel(
        uuid=uuid_module.uuid4(),
        name="The Dark Knight",
        year=2008,
        time=152,
        imdb=9.0,
        votes=2500000,
        description="When the menace known as the Joker wreaks havoc on Gotham City.",
        price=Decimal("17.99"),
        certification_id=1
    )

    director = DirectorModel(name="Christopher Nolan")

    movie.directors.append(director)

    db_session.add_all([movie, director])
    db_session.commit()

    assert len(movie.directors) == 1, "Movie should be linked with the movie."
    assert movie in director.movies, "Director should be linked with the movie."


def test_certification_enum_values():
    """
    Verifies the enum values of CertificationEnum.
    """
    assert CertificationEnum.GENERAL_AUDIENCE.value == "G", "CertificationEnum.GENERAL_AUDIENCE should be 'G'."
    assert CertificationEnum.PARENTAL_GUIDANCE_SUGGESTED.value == "PG", "CertificationEnum.PARENTAL_GUIDANCE_SUGGESTED should be 'PG'."
    assert CertificationEnum.PARENTS_STRONGLY_CAUTIONED.value == "PG-13", "CertificationEnum.PARENTS_STRONGLY_CAUTIONED should be 'PG-13'."
    assert CertificationEnum.RESTRICTED.value == "R", "CertificationEnum.RESTRICTED should be 'R'."
    assert CertificationEnum.ADULTS_ONLY.value == "NC-17", "CertificationEnum.ADULTS_ONLY should be 'NC-17'."