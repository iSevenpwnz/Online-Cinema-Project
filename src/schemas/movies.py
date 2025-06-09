from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator


from schemas.examples.movies import (
    genre_schema_example,
    star_schema_example,
    star_detail_schema_example,
    director_schema_example,
    director_detail_schema_example,
    certification_schema_example,
    movie_schema_example,
    movie_detail_schema_example,
    movie_create_schema_example,
    movie_update_schema_example
)


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "str_max_length": 100,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples":
                [genre_schema_example]

        }
    }


class GenreCreateSchema(BaseModel):
    name: str


class GenreWithCountSchema(GenreSchema):
    movie_count: int

    model_config = {
        "json_schema_extra": {
            "examples": [{
                **genre_schema_example,
                "movie_count": 42
            }]
        }
    }


class StarSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "str_max_length": 100,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                star_schema_example
            ]
        },
    }


class StarDetailSchema(StarSchema):
    movie: List[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                star_detail_schema_example
            ]
        },
    }


class StarCreateSchema(BaseModel):
    name: str


class DirectorSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "str_max_length": 100,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                director_schema_example
            ]
        },
    }


class DirectorDetailSchema(DirectorSchema):
    movie: List[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                director_detail_schema_example
            ]
        }
    }


class DirectorCreateSchema(BaseModel):
    name: str


class CertificationSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [
                certification_schema_example
            ]
        },
    }


class MovieBaseSchema(BaseModel):

    uuid: str = Field(..., max_length=100)
    name: str = Field(..., max_length=250)
    year: int = Field(...)
    time: int = Field(..., ge=15, le=150)
    imdb: float = Field(..., ge=0, le=10, multiple_of=0.1)
    votes: int = Field(..., ge=0)
    meta_score: Optional[float] = Field(None, ge=0, le=100)
    gross: Optional[float] = Field(None, ge=0)
    description: str = Field(..., min_length=10, max_length=2000)
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    certification_id: int = Field(..., gt=0)
    genres: List[str] = Field(..., min_length=1)
    stars: List[str] = Field(..., min_length=1)
    directors: List[str] = Field(..., min_length=1)

    model_config = {
        "from_attributes": True,
        "str_max_length": 250,
        "validate_assignment": True,
    }


class MovieDetailSchema(MovieBaseSchema):
    id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                movie_detail_schema_example
            ]
        }
    }


class MovieListItemSchema (BaseModel):

    id: int
    name: str = Field(..., max_length=250, min_length=1)
    year: int
    imdb: float = Field(..., ge=0, le=10)
    price: Decimal
    genres: List[str]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                movie_schema_example
            ]
        },
    }


class MovieListResponseSchema(BaseModel):
    movies: List[MovieListItemSchema]

    prev_page: Optional[str] = None
    next_page: Optional[str] = None

    total_pages: int = Field(..., ge=0)
    total_items: int = Field(..., ge=0)


class MovieCreateSchema(MovieBaseSchema):

    model_config = {
        "json_schema_extra": {
            "examples": [
                movie_create_schema_example
            ]
        }
    }


class MovieUpdateSchema(BaseModel):

    uuid: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=250, min_length=1)
    year: Optional[int] = Field(None, le=datetime.now().year)
    time: Optional[int] = Field(None, ge=1, le=150)
    imdb: Optional[float] = Field(None, ge=0, le=10)
    votes: Optional[int] = Field(None)
    meta_score: Optional[float] = Field(None)
    gross: Optional[float] = Field(None)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    certification_id: Optional[int] = None
    genres: Optional[List[str]] = None
    stars: Optional[List[str]] = None
    directors: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                movie_update_schema_example
            ]
        },
        "extra": "forbid",
        "from_attributes": True,
        "str_strip_whitespace": True,
        "validate_assignment": True
    }

    @field_validator("genres", "stars", "directors", mode="before")
    @classmethod
    def normalize_list_fields(cls, value: Union[List[int], List[str], None]) -> Union[List[int], List[str], None]:
        if value is None:
            return None
        if value and isinstance(value[0], str):
            return [item.strip().title() if isinstance(item, str) else str(item).strip().title()
                    for item in value]
        return value
