from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

# from database.models.movies import MovieStatusEnum
from schemas.examples.movies import (
    country_schema_example,
    language_schema_example,
    genre_schema_example,
    actor_schema_example,
    movie_item_schema_example,
    movie_list_response_schema_example,
    movie_create_schema_example,
    movie_detail_schema_example,
    movie_update_schema_example,
)


class LanguageSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CountrySchema(BaseModel):
    id: int
    code: str
    name: Optional[str]

    model_config = {"from_attributes": True}


class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class StarSchema(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class CertificationSchema(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class DirectorSchema(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class MovieBaseSchema(BaseModel):
    name: str = Field(..., max_length=255)
    date: date
    year: int
    score: float = Field(..., ge=0, le=100)
    overview: str
    status: str
    budget: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    country: str
    model_config = {"from_attributes": True}

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        current_year = datetime.now().year
        if value.year > current_year + 1:
            raise ValueError(
                f"The year in 'date' cannot be greater than {current_year + 1}."
            )
        return value


class MovieDetailSchema(BaseModel):
    id: int
    uuid: str
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float]
    gross: Optional[float]
    description: str
    price: float
    certification_id: int
    certification: CertificationSchema
    genres: List[GenreSchema]
    stars: List[StarSchema]
    directors: List[DirectorSchema]
    model_config = {"from_attributes": True}


class MovieListItemSchema(BaseModel):
    id: int
    name: str
    year: int
    imdb: float
    price: float
    description: str
    model_config = {"from_attributes": True}


class MovieListResponseSchema(BaseModel):
    movies: List[MovieListItemSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int

    model_config = {"from_attributes": True}


class MovieCreateSchema(BaseModel):
    uuid: str
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: str
    price: float
    certification_id: int
    genres: List[str]
    stars: List[str]
    directors: List[str]
    model_config = {"from_attributes": True}

    @field_validator("genres", "stars", "directors", mode="before")
    @classmethod
    def normalize_list_fields(cls, value: List[str]) -> List[str]:
        return [item.title() for item in value]


class MovieUpdateSchema(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    time: Optional[int] = None
    imdb: Optional[float] = None
    votes: Optional[int] = None
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: Optional[str] = None
    price: Optional[float] = None
    certification_id: Optional[int] = None
    genres: Optional[List[str]] = None
    stars: Optional[List[str]] = None
    directors: Optional[List[str]] = None
    model_config = {"from_attributes": True}
