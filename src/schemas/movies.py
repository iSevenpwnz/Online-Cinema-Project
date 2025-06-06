from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator, HttpUrl

# Спрощення прикладів
from schemas.examples.movies import genre_schema_example, star_schema_example, star_detail_schema_example, director_schema_example, director_detail_schema_example, certification_schema_example, movie_schema_example, movie_detail_schema_example, movie_create_schema_example, movie_update_schema_example

class GenreSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "orm_mode": True,
        "anystr_strip_whitespace": True,
        "max_anystr_length": 100,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [genre_schema_example]
        },
    }

class StarSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "orm_mode": True,
        "anystr_strip_whitespace": True,
        "max_anystr_length": 100,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [star_schema_example]
        },
    }

class StarDetailSchema(StarSchema):
    movie: List[str]

    model_config = {
        "json_schema_extra": {
            "examples": [star_detail_schema_example]
        },
    }

class DirectorSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "orm_mode": True,
        "anystr_strip_whitespace": True,
        "max_anystr_length": 100,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [director_schema_example]
        },
    }

class DirectorDetailSchema(DirectorSchema):
    movie: List[str]

    model_config = {
        "json_schema_extra": {
            "examples": [director_detail_schema_example]
        }
    }

class CertificationSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "orm_mode": True,
        "anystr_strip_whitespace": True,
        "validate_assignment": True,
        "json_schema_extra": {
            "examples": [certification_schema_example]
        },
    }

class MovieBaseSchema(BaseModel):
    uuid: str = Field(..., max_length=100)
    name: str = Field(..., max_length=250)
    year: int = Field(..., max_length=4)
    time: int = Field(..., ge=15, le=150)
    imdb: float = Field(..., ge=0, le=10, decimal_places=1)
    votes: int = Field(..., ge=0)
    meta_score: Optional[float] = Field(None, ge=0, le=100)
    gross: Optional[float] = Field(None, ge=0)
    description: str = Field(..., min_length=10, max_length=2000)
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    certification_id: int = Field(..., gt=0)
    genres: List[int] = Field(..., min_length=1)
    stars: List[int] = Field(..., min_length=1)
    directors: List[int] = Field(..., min_length=1)

    model_config = {
        "orm_mode": True,
        "max_anystr_length": 250,
        "validate_assignment": True,
        "from_attributes": True,
    }

class MovieDetailSchema(MovieBaseSchema):
    id: int
    uuid: str
    certification: CertificationSchema
    genres: List[GenreSchema] = Field(..., min_length=1)
    stars: List[StarSchema] = Field(..., min_length=1)
    directors: List[DirectorSchema] = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [movie_detail_schema_example]
        }
    }

class MovieListSchema(BaseModel):
    id: int
    name: str = Field(..., max_length=250, min_length=1)
    year: int
    imdb: float = Field(..., ge=0, le=10, decimal_places=1)
    price: Decimal
    genres: List[GenreSchema]
    prev_page: Optional[HttpUrl] = None
    next_page: Optional[HttpUrl] = None
    total_pages: int = Field(..., ge=1)
    total_items: int = Field(..., ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [movie_schema_example]
        },
    }

class MovieCreateSchema(MovieBaseSchema):
    model_config = {
        "json_schema_extra": {
            "examples": [movie_create_schema_example]
        }
    }

    @field_validator("genres", mode="before")
    @classmethod
    def normalize_list_fields(cls, value: List[str]) -> List[str]:
        return [item.title() for item in value]

class MovieUpdateSchema(BaseModel):
    uuid: Optional[str] = Field(None, max_length=100)
    name: Optional[str] = Field(None, max_length=250, min_length=1)
    year: Optional[int] = Field(None, le=datetime.now().year)
    time: Optional[int] = Field(None, ge=1, le=150)
    imdb: Optional[float] = Field(None, ge=0, le=10)
    votes: Optional[int] = None
    meta_score: Optional[float] = None
    gross: Optional[float] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    certification_id: Optional[int] = None
    genres: Optional[Union[List[int], List[str]]] = None
    stars: Optional[Union[List[int], List[str]]] = None
    directors: Optional[Union[List[int], List[str]]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [movie_update_schema_example]
        },
        "extra": "forbid",
        "orm_mode": True,
        "anystr_strip_whitespace": True,
        "validate_assignment": True
    }

    @field_validator("genres", "stars", "directors", mode="before")
    @classmethod
    def normalize_list_fields(cls, value: Union[List[int], List[str], None]) -> Union[List[int], List[str], None]:
        if value is None:
            return None
        if isinstance(value[0], str):
            return [item.strip().title() for item in value]
        return value
