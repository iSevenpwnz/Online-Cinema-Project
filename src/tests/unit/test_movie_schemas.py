import pytest
from decimal import Decimal
from pydantic import ValidationError
from datetime import datetime

from schemas.movies import (
    GenreSchema,
    StarSchema,
    DirectorSchema,
    MovieBaseSchema,
    MovieListItemSchema ,
    MovieListResponseSchema,
    MovieUpdateSchema
)



def test_genre_schema_valid():
    """
    GenreSchema creation
    """
    genre = GenreSchema(id=1, name="Action")
    assert genre.id == 1, "GenreSchema.id did not match expected value."
    assert genre.name == "Action", "GenreSchema.name did not match expected value."

def test_genre_schema_invalid_name_length():
    """
    GenreSchema validation (invalid name length)
    """
    long_name = "A" * 101
    with pytest.raises(ValidationError) as excinfo:
        GenreSchema(id=1, name=long_name)
    error_msg = str(excinfo.value)
    assert (
            "should have at most 100 characters" in error_msg or
            "100 characters" in error_msg
    ), (
        "Expected a validation error about max length for 'name', "
        f"but got: {error_msg}"
    )

def test_genre_schema_strip_whitespace():
    """
    GenreSchema validation (the whitespaces in the name should be deleted)
    """
    genre = GenreSchema(id=1, name="  Action  ")
    assert genre.name == "Action", (
        f"Expected whitespace to be stripped from 'name', got: '{genre.name}'"
    )

def test_star_schema_invalid_name_length():
    """
    StarSchema validation (invalid name length)
    """
    long_name = "A" * 101
    with pytest.raises(ValidationError) as excinfo:
        StarSchema(id=1, name=long_name)
    error_msg = str(excinfo.value)
    assert (
            "should have at most 100 characters" in error_msg or
            "100 characters" in error_msg
    ), (
        "Expected a validation error about max length for 'name', "
        f"but got: {error_msg}"
    )

def test_director_schema_strip_whitespace():
    """
    DirectorSchema validation (the whitespaces in the name should be deleted)
    """
    director = DirectorSchema(id=1, name="  Action  ")
    assert director.name == "Action", (
        f"Expected whitespace to be stripped from 'name', got: '{director.name}'"
    )

def make_valid_movie_data():
    """
    A valid movie base dictionary
    """
    return dict(
        uuid="123e4567-e89b-12d3-a456-426614174000",
        name="My Movie",
        year=2024,
        time=120,
        imdb=8.2,
        votes=1000,
        meta_score=88,
        gross=123.45,
        description="A very interesting movie about something.",
        price=Decimal("19.99"),
        certification_id=2,
        genres=["Action"],
        stars=["Brad Pitt"],
        directors=["James Cameron"]
    )

def test_movie_base_schema_valid():
    """
    MovieBaseSchema creating a valid object
    """
    data = make_valid_movie_data()
    movie = MovieBaseSchema(**data)
    assert movie.uuid == data["uuid"], "UUID does not match expected value."
    assert movie.genres[0] == "Action", "Genre name did not match."
    assert movie.stars[0] == "Brad Pitt", "Star name did not match."
    assert movie.directors[0] == "James Cameron", "Director name did not match."

def test_movie_base_schema_invalid_time():
    """
    MovieBaseSchema creating an invalid object
    """
    data = make_valid_movie_data()
    data["time"] = 10
    with pytest.raises(ValidationError) as excinfo:
        MovieBaseSchema(**data)
    error_msg = str(excinfo.value)
    assert (
        "greater than or equal to 15" in error_msg or
        "15" in error_msg
    ), (
        "Expected a validation error about 'time' being below the allowed minimum, "
        f"but got: {error_msg}"
    )

def test_movie_base_schema_invalid_imdb():
    """
    MovieBaseSchema creating an invalid object (invalid imdb)
    """
    data = make_valid_movie_data()

    data["imdb"] = 11
    with pytest.raises(ValidationError) as excinfo:
        MovieBaseSchema(**data)
    error_msg = str(excinfo.value)
    assert (
            "less than or equal to 10" in error_msg or
            "10" in error_msg
    ), (
        "Expected validation error about 'imdb' being above allowed maximum (10), "
        f"but got: {error_msg}"
    )

    data["imdb"] = 8.23
    with pytest.raises(ValidationError) as excinfo:
        MovieBaseSchema(**data)
    error_msg = str(excinfo.value)
    assert (
            "multiple of 0.1" in error_msg or
            "0.1" in error_msg
    ), (
        "Expected validation error about 'imdb' not being a multiple of 0.1, "
        f"but got: {error_msg}"
    )

def test_movie_base_schema_description_length():
    """
    MovieBaseSchema creating an invalid object (invalid description)
    """
    data = make_valid_movie_data()
    data["description"] = "short"
    with pytest.raises(ValidationError) as excinfo:
        MovieBaseSchema(**data)
    error_msg = str(excinfo.value)
    assert (
            "at least 10 characters" in error_msg or
            "10 characters" in error_msg
    ), (
        "Expected validation error about 'description' being too short, "
        f"but got: {error_msg}"
    )

def test_movie_base_schema_empty_genres():
    """
    MovieBaseSchema creating an invalid object (no genres)
    """
    data = make_valid_movie_data()
    data["genres"] = []
    with pytest.raises(ValidationError):
        MovieBaseSchema(**data)

def test_movie_update_schema_genres_title_case():
    """
    MovieUpdateSchema updating genres title case
    """
    data = {"genres": ["  drama", "THRILLER ", "action"]}
    schema = MovieUpdateSchema(**data)
    assert schema.genres == ["Drama", "Thriller", "Action"], (
        f"Expected genres to be normalized to ['Drama', 'Thriller', 'Action'], got: {schema.genres}"
    )

def test_movie_update_schema_genres_numbers():
    """
    MovieUpdateSchema updating genres using genres_names
    """
    data = {"genres": ["Action", "Drama", "Comedy"]}
    schema = MovieUpdateSchema(**data)
    assert schema.genres == ["Action", "Drama", "Comedy"]

def test_movie_update_schema_genres_none():
    """
    MovieUpdateSchema updating genres = None, meaning to not make changes
    """
    data = {}
    schema = MovieUpdateSchema(**data)
    assert schema.genres is None, (
        f"Expected genres to be None when not provided, got: {schema.genres}"
    )

def test_movie_update_schema_directors_mixed_types():
    """
    MovieUpdateSchema updating directors using ids, string
    """
    data = {"directors": [" james cameron ", 123, "QUENTIN tARANTINO"]}
    schema = MovieUpdateSchema(**data)
    assert schema.directors == ["James Cameron", "123", "Quentin Tarantino"], (
        f"Expected directors to be normalized to ['James Cameron', '123', 'Quentin Tarantino'], got: {schema.directors}"
    )

def test_movie_update_schema_forbid_extra_fields():
    """
    MovieUpdateSchema: extra fields are not allowed
    """
    with pytest.raises(ValidationError) as excinfo:
        MovieUpdateSchema(genres=[1, 2], unexpected_field=123)
    error_msg = str(excinfo.value)
    assert "extra fields not permitted" in error_msg or "unexpected_field" in error_msg, (
        f"Expected validation error about extra fields, but got: {error_msg}"
    )

def test_movie_list_paginated_schema_valid():
    """
    MovieListResponseSchema: pagination should be valid
    """
    schema = MovieListResponseSchema(
        movies=[
            MovieListItemSchema (
                id=1,
                name="Test",
                year=2023,
                imdb=8.8,
                price=Decimal(12.99),
                genres=["Comedy"],
            )
        ],
        prev_page=None,
        next_page=None,
        total_pages=1,
        total_items=1
    )
    assert schema.total_items == 1, "Expected total_items to be 1."
    assert schema.movies[0].genres[0] == "Comedy", (
        f"Expected first genre name to be 'Comedy', got: {schema.movies[0].genres[0]}"
    )


def test_movie_list_paginated_schema_zero_pages_allowed():
    """
    MovieListResponseSchema: total_pages=0 and total_items>=0 should be valid
    """
    schema = MovieListResponseSchema(
        movies=[], prev_page=None, next_page=None,
        total_pages=0, total_items=1
    )

    assert schema.total_pages == 0
    assert schema.total_items == 1
    assert schema.movies == []
    assert schema.prev_page is None
    assert schema.next_page is None
