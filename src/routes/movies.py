from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from database import get_db, MovieModel, movie_genres, UserModel
from database import CertificationModel, GenreModel, StarModel, DirectorModel
from database.models.orders import Order, OrderItem, OrderStatusEnum
# adding comment to push


from schemas.examples.movies import (
    movie_schema_example,
    movie_detail_schema_example,
)
from schemas.movies import (
    MovieDetailSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
    MovieListItemSchema ,
    MovieListResponseSchema,
    GenreWithCountSchema,
    GenreSchema,
    StarSchema,
    StarDetailSchema,
)

router = APIRouter()


@router.get(
    "/movies/",
    tags=["Movies"],
    response_model=MovieListResponseSchema,
    summary="Get a paginated list of movies, with search, filter, sort_by options",
    description=(
        "<h3>This endpoint retrieves a paginated list of movies from the database. </h3> "
        "<p>Clients can specify the `page` number and the number of items per page using `page_size`.</p>"
        "<p>The response includes details about the movies, total pages, and total items,</p>"
        "<p>along with links to the previous and next pages if applicable.</p>"
        "<h3>Also, if needed exists the possibility to:</h3>"
        "<p> - search for movies by title, description, stars, or director;</p>"
        "<p> - filter movies by year or imdb rating;</p>"
        "<p> - sort movies by  'price', 'year', 'imdb'. Default is 'price'.</p>"
    ),
    responses={
        200: {
            "description": "Succes!",
            "content": {
                "application/json": movie_schema_example
            }
        },
        404: {
            "description": "No movies found.",
            "content": {
                "application/json": {"example": {"detail": "No movies found."}}
            },
        }
    },
)
async def get_movie_list(
    db: AsyncSession = Depends(get_db),
    page: int = Query(
        1,
        ge=1,
        description="Page number for pagination, starting from 1."
    ),
    page_size: int = Query(
        10,
        ge=1,
        le=20,
        description="Number of items per page. Maximum is 20."
    ),
    sort_by: Optional[str] = Query(
        "id",
        description="Sort movies by a field. Options: 'price', 'year', 'imdb'. Default is 'price'."
    ),
    filter_by: Optional[str] = Query(
        None,
        description="Filter movies by year or imdb rating."
    ),
    search: Optional[str] = Query(
        None,
        description="Search movies by title, description, stars, or director."
    ),
) -> MovieListResponseSchema:
    """
    Fetch a paginated list of movies from the database (asynchronously).
    Movies can be:
        - filtered by year or imdb rating.
        - sorted by price, year, imdb rating (default == id)
        - searched by name, description, star or director.
    """
    stmt = select(MovieModel).options(
        joinedload(MovieModel.genres),
    )

    if filter_by:
        try:
            year = int(filter_by)
            stmt = stmt.where(MovieModel.year == year)
        except ValueError:
            stmt = stmt.where(MovieModel.imdb >= float(filter_by))

    if sort_by == "price":
        stmt = stmt.order_by(MovieModel.price)
    elif sort_by == "year":
        stmt = stmt.order_by(MovieModel.year)
    elif sort_by == "imdb":
        stmt = stmt.order_by(MovieModel.imdb)
    else:
        stmt = stmt.order_by(MovieModel.id.desc())

    if search:
        stmt = stmt.join(MovieModel.stars, isouter=True).join(MovieModel.directors, isouter=True)
        stmt = stmt.where(
            MovieModel.name.ilike(f"%{search}%") |
            MovieModel.description.ilike(f"%{search}%") |
            StarModel.name.ilike(f"%{search}%") |
            DirectorModel.name.ilike(f"%{search}%")
        )

    offset = (page - 1) * page_size

    count_stmt = select(func.count()).select_from(MovieModel)
    result_count = await db.execute(count_stmt)
    total_items = result_count.scalar() or 0

    if not total_items:
        raise HTTPException(status_code=404, detail="No movies found.")

    stmt = stmt.offset(offset).limit(page_size)
    result_movies = await db.execute(stmt)
    movies = result_movies.unique().scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    movie_list = [
        MovieListItemSchema(
            id=movie.id,
            name=movie.name,
            year=movie.year,
            imdb=movie.imdb,
            price=movie.price,
            genres=[genre.name for genre in movie.genres],
        )
        for movie in movies
    ]

    total_pages = (total_items + page_size - 1) // page_size

    return MovieListResponseSchema(
        movies=movie_list,
        prev_page=(
            f"/movies/?page={page - 1}&page_size={page_size}"
            if page > 1
            else None
        ),
        next_page=(
            f"/movies/?page={page + 1}&page_size={page_size}"
            if page < total_pages
            else None
        ),
        total_pages=total_pages,
        total_items=total_items,
    )


@router.get(
    "/movies/{movie_id}/",
    tags=["Movies"],
    response_model=MovieDetailSchema,
    summary="Get movie details by ID",
    description=(
        "<h3>Fetch detailed information about a specific movie by its unique ID. "
        "This endpoint retrieves all available details for the movie, such as "
        "its name, genre, crew, budget, and revenue. If the movie with the given "
        "ID is not found, a 404 error will be returned.</h3>"
    ),
    responses={
        200: {
            "description": "Succes!",
            "content": {
                "application/json": movie_detail_schema_example
            }
        },
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Movie with the given ID was not found."
                    }
                }
            },
        }
    },
)
async def get_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
) -> MovieDetailSchema:
    """
    Get a movie detail by its ID.
    """
    stmt = (
        select(MovieModel)
        .options(
            joinedload(MovieModel.certification),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.stars),
            joinedload(MovieModel.directors),
        )
        .where(MovieModel.id == movie_id)
    )

    result = await db.execute(stmt)
    movie = result.scalars().first()

    if not movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )

    movie_dict = movie.__dict__.copy()

    movie_dict["genres"] = [genre.name for genre in movie.genres]
    movie_dict["stars"] = [star.name for star in movie.stars]
    movie_dict["directors"] = [director.name for director in movie.directors]

    if movie.certification:
        movie_dict["certification_id"] = movie.certification.id
    else:
        movie_dict["certification_id"] = None

    return MovieDetailSchema.model_validate(movie_dict)


@router.get(
    "/genres/",
    tags=["Genres"],
    summary="View a list of genres with the count of movies in each. Clicking on a genre shows all related movies.",
    description="Returns list of all genres with count of movies in each genre",
    responses={
        200: {
            "description": "Succes!",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 1, "name": "Comedy", "movie_count": 42},
                        {"id": 2, "name": "Drama", "movie_count": 35},
                        {"id": 3, "name": "Action", "movie_count": 28}
                    ]
                }
            },
        },
        404: {
            "description": "Genre not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "No genre found"
                    }
                }
            },
        },
    }
)
async def get_genres_with_counts(
        db: AsyncSession = Depends(get_db),
        search: Optional[str] = Query(None, description="Search genre by name")
):
    """
    Get a list of all genres with the count of movies in each genre.
    """
    stmt = select(
        GenreModel.id,
        GenreModel.name,
        func.count(movie_genres.c.movie_id).label("movie_count")
    ).join(
        movie_genres,
        GenreModel.id == movie_genres.c.genre_id,
        isouter=True
    ).group_by(GenreModel.id)

    if search:
        stmt = stmt.where(GenreModel.name.ilike(f"%{search}%"))

    result = await db.execute(stmt)
    genres_with_counts = result.all()

    if not genres_with_counts:
        raise HTTPException(
            status_code=404,
            detail="No genres matching your criteria"
        )

    return [
        GenreWithCountSchema(
            id=genre.id,
            name=genre.name,
            movie_count=genre.movie_count
        )
        for genre in genres_with_counts
    ]


@router.get(
    "/genres/{genre_id}/movies",
    tags=["Genres"],
    response_model=MovieListResponseSchema,
    summary="Get movies by genre ID",
    responses={
        200: {
            "description": "List of movies in the genre",
            "content": {
                "application/json": {
                    "example": {
                        "movies": [movie_schema_example],
                        "prev_page": None,
                        "next_page": "/genres/1/movies?page=2",
                        "total_pages": 3,
                        "total_items": 25
                    }
                }
            }
        },
        404: {
            "description": "Genre not found or no movies in genre",
            "content": {
                "application/json": {
                    "example": {"detail": "Genre not found"}
                }
            }
        }
    }
)
async def get_movies_by_genre(
    genre_id: int = Path(..., description="ID of the genre"),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """
    Get paginated list of movies belonging to a specific genre.
    Returns 404 if genre doesn't exist or has no movies.
    """
    genre = await db.get(GenreModel, genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    stmt = (
        select(MovieModel)
        .options(joinedload(MovieModel.genres), joinedload(MovieModel.stars), joinedload(MovieModel.directors))
        .join(movie_genres, MovieModel.id == movie_genres.c.movie_id)
        .where(movie_genres.c.genre_id == genre_id)
        .order_by(MovieModel.id)
    )

    count_stmt = (
        select(func.count())
        .select_from(movie_genres)
        .where(movie_genres.c.genre_id == genre_id)
    )

    total_items = (await db.execute(count_stmt)).scalar() or 0

    if total_items == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No movies found in genre '{genre.name}'"
        )

    movies = (await db.execute(
        stmt.offset((page - 1) * page_size).limit(page_size)
    )).unique().scalars().all()

    total_pages = (total_items + page_size - 1) // page_size

    movie_list = [
        MovieListItemSchema(
            id=movie.id,
            name=movie.name,
            year=movie.year,
            imdb=movie.imdb,
            price=movie.price,
            genres=[genre.name for genre in movie.genres],
        )
        for movie in movies
    ]

    return MovieListResponseSchema(
        movies=movie_list,
        prev_page=(
            f"/genres/{genre_id}/movies?page={page - 1}&page_size={page_size}"
            if page > 1 else None
        ),
        next_page=(
            f"/genres/{genre_id}/movies?page={page + 1}&page_size={page_size}"
            if page < total_pages else None
        ),
        total_pages=total_pages,
        total_items=total_items
    )


@router.post(
    "/movies/",
    tags=["Movies"],
    response_model=MovieDetailSchema,
    summary="Add a new movie",
    description=(
            "<h3>This endpoint allows clients to add a new movie to the database. "
            "It accepts details such as name, year, time, and "
            "other attributes. The associated directors, genres and stars "
            "will be created or linked automatically.</h3>"
    ),
    responses={
        201: {
            "description": "Movie created successfully.",
            "content": {
                "application/json": {
                    "example": movie_detail_schema_example
                }
            }
        },
        400: {
            "description": "Invalid input.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid input data."}
                }
            },
        },
        409: {
            "description": "Movie already exists.",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie with these details already exists."}
                }
            }
        }
    },
    status_code=201
)
async def create_movie(
        movie_data: MovieCreateSchema,
        db: AsyncSession = Depends(get_db),
) -> MovieDetailSchema:
    """
    Create a new movie. For admin only.
    """
    existing_movie = await db.execute(
        select(MovieModel).where(
            MovieModel.name == movie_data.name,
            MovieModel.year == movie_data.year,
            MovieModel.time == movie_data.time
        )
    )
    if existing_movie.scalars().first():
        raise HTTPException(
            status_code=409,
            detail=f"Movie '{movie_data.name}' ({movie_data.year}) already exists"
        )

    try:
        genres = []
        for genre_name in movie_data.genres:
            genre = await db.scalar(select(GenreModel).where(GenreModel.name == genre_name))
            if not genre:
                genre = GenreModel(name=genre_name)
                db.add(genre)
                await db.flush()
            genres.append(genre)

        stars = []
        for star_name in movie_data.stars:
            star = await db.scalar(select(StarModel).where(StarModel.name == star_name))
            if not star:
                star = StarModel(name=star_name)
                db.add(star)
                await db.flush()
            stars.append(star)

        directors = []
        for director_name in movie_data.directors:
            director = await db.scalar(select(DirectorModel).where(DirectorModel.name == director_name))
            if not director:
                director = DirectorModel(name=director_name)
                db.add(director)
                await db.flush()
            directors.append(director)

        certification = await db.get(CertificationModel, movie_data.certification_id)
        if not certification:
            raise HTTPException(
                status_code=400,
                detail=f"Certification ID {movie_data.certification_id} not found"
            )

        movie = MovieModel(
            uuid=movie_data.uuid,
            name=movie_data.name,
            year=movie_data.year,
            time=movie_data.time,
            imdb=movie_data.imdb,
            votes=movie_data.votes,
            meta_score=movie_data.meta_score,
            gross=movie_data.gross,
            description=movie_data.description,
            price=movie_data.price,
            certification_id=movie_data.certification_id,
            genres=genres,
            stars=stars,
            directors=directors
        )

        db.add(movie)
        await db.commit()
        await db.refresh(movie, ["genres", "stars", "directors", "certification"])

        movie_dict = {
            "id": movie.id,
            "uuid": movie.uuid,
            "name": movie.name,
            "year": movie.year,
            "time": movie.time,
            "imdb": movie.imdb,
            "votes": movie.votes,
            "meta_score": movie.meta_score,
            "gross": movie.gross,
            "description": movie.description,
            "price": str(movie.price),
            "certification_id": movie.certification_id,
            "genres": [genre.name for genre in movie.genres],
            "stars": [star.name for star in movie.stars],
            "directors": [director.name for director in movie.directors],
        }

        return MovieDetailSchema.model_validate(movie_dict)

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error creating movie: {str(e)}"
        )


@router.patch(
    "/movies/{movie_id}/",
    tags=["Movies"],
    response_model=MovieDetailSchema,
    summary="Update a movie by ID",
    description=(
            "<h3>Update details of a specific movie by its ID.</h3>"
            "<p>Partial updates are supported. Only provided fields will be updated.</p>"
            "<p>Genres, stars, directors will be created (if don't exist).</p>"
    ),
    responses={
        200: {
            "description": "Movie updated successfully",
            "content": {
                "application/json": {
                    "example": movie_detail_schema_example
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid input data"}
                }
            }
        },
        404: {
            "description": "Movie not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Movie not found"}
                }
            }
        }
    }
)
async def update_movie(
        movie_id: int = Path(..., description="ID of the movie to update", gt=0),
        movie_data: MovieUpdateSchema = Body(...),
        db: AsyncSession = Depends(get_db),
) -> MovieDetailSchema:
    """
    Update(full and partial) movie details by ID with automatic handling of related entities.
    For admin only.
    """
    stmt = (
        select(MovieModel)
        .options(
            selectinload(MovieModel.genres),
            selectinload(MovieModel.stars),
            selectinload(MovieModel.directors),
            selectinload(MovieModel.certification),
        )
        .where(MovieModel.id == movie_id)
    )
    result = await db.execute(stmt)
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    try:
        update_data = movie_data.model_dump(exclude_unset=True)

        if "genres" in update_data:
            genres = []
            for genre_name in update_data["genres"]:
                genre = await db.scalar(select(GenreModel).where(GenreModel.name == genre_name))
                if not genre:
                    genre = GenreModel(name=genre_name)
                    db.add(genre)
                    await db.flush()
                genres.append(genre)
            movie.genres = genres

        if "stars" in update_data:
            stars = []
            for star_name in update_data["stars"]:
                star = await db.scalar(select(StarModel).where(StarModel.name == star_name))
                if not star:
                    star = StarModel(name=star_name)
                    db.add(star)
                    await db.flush()
                stars.append(star)
            movie.stars = stars

        if "directors" in update_data:
            directors = []
            for director_name in update_data["directors"]:
                director = await db.scalar(select(DirectorModel).where(DirectorModel.name == director_name))
                if not director:
                    director = DirectorModel(name=director_name)
                    db.add(director)
                    await db.flush()
                directors.append(director)
            movie.directors = directors

        for field, value in update_data.items():
            if field not in ['genres', 'stars', 'directors'] and value is not None:
                setattr(movie, field, value)

        await db.commit()
        await db.refresh(movie, ["genres", "stars", "directors", "certification"])

        movie_dict = MovieDetailSchema(
            id=movie.id,
            uuid=movie.uuid,
            name=movie.name,
            year=movie.year,
            time=movie.time,
            imdb=movie.imdb,
            votes=movie.votes,
            meta_score=movie.meta_score,
            gross=movie.gross,
            description=movie.description,
            price=movie.price,
            certification_id=movie.certification_id,
            genres=[genre.name for genre in movie.genres],
            stars=[star.name for star in movie.stars],
            directors=[director.name for director in movie.directors],
        )

        return movie_dict

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database integrity error: {str(e)}"
        )
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value: {str(e)}"
        )


@router.delete(
    "/movies/{movie_id}/",
    tags=["Movies"],
    summary="Delete a movie by ID",
    description=(
            "<h3>Delete a specific movie from the database by its unique ID.</h3>"
            "<p>If the movie exists and has no paid orders, it will be deleted.</p>"
            "<p>If the movie does not exist, a 404 error will be returned.</p>"
            "<p>If the movie has paid orders, a 400 error will be returned.</p>"
    ),
    responses={
        204: {"description": "Movie deleted successfully."},
        400: {
            "description": "Movie has paid orders and cannot be deleted.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cannot delete movie - it appears in paid orders."
                    }
                }
            },
        },
        404: {
            "description": "Movie not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Movie with the given ID was not found."
                    }
                }
            },
        },
    },
    status_code=204,
)
async def delete_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific movie by its ID if it has no paid orders. For admin only.
    """
    movie = await db.get(MovieModel, movie_id)

    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie with the given ID was not found."
        )

    paid_order_exists = await db.execute(
        select(OrderItem.id)
        .join(Order)
        .where(
            OrderItem.movie_id == movie_id,
            Order.status == OrderStatusEnum.PAID
        )
        .limit(1)
    )
    if paid_order_exists.scalar():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete movie - it appears in paid orders."
        )

    await db.delete(movie)
    await db.commit()

    return {"detail": "Movie deleted successfully."}


@router.post(
    "/genres/",
    tags=["Genres"],
    response_model=GenreSchema
)
async def create_genre(
        genre_name: str,
        db: AsyncSession = Depends(get_db),
):
    """
    Create a new genre. For admin only.
    """
    existing_genre = await db.execute(
        select(GenreModel).where(GenreModel.name == genre_name)
    )
    if existing_genre.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists."
        )

    new_genre = GenreModel(name=genre_name)
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)

    return new_genre


@router.put(
    "/genres/{genre_id}",
    tags=["Genres"],
    response_model=GenreSchema
)
async def update_genre(
        genre_id: int,
        new_name: str,
        db: AsyncSession = Depends(get_db),
):
    """
    Update genre name. For admin only.
    """
    genre = await db.get(GenreModel, genre_id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found."
        )

    existing_genre = await db.execute(
        select(GenreModel)
        .where(GenreModel.name == new_name)
        .where(GenreModel.id != genre_id)
    )
    if existing_genre.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists."
        )

    genre.name = new_name
    await db.commit()
    await db.refresh(genre)

    return genre


@router.delete(
    "/genres/{genre_id}",
    tags=["Genres"],
)
async def delete_genre(
        genre_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Delete a genre by ID. For admin only.
    """
    genre = await db.get(GenreModel, genre_id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found."
        )

    await db.delete(genre)
    await db.commit()


@router.post(
    "/stars/",
    tags=["Stars"],
    response_model=StarSchema
)
async def create_star(
        star_name: str,
        db: AsyncSession = Depends(get_db),
):
    """
    Create a new star. For admin only.
    """
    existing_star = await db.execute(
        select(StarModel).where(StarModel.name == star_name)
    )
    if existing_star.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Star with this name already exists."
        )

    new_star = StarModel(name=star_name)
    db.add(new_star)
    await db.commit()
    await db.refresh(new_star)

    return new_star


@router.get(
    "/stars/",
    tags=["Stars"],
    response_model=List[StarSchema]
)
async def get_stars_list(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
):
    """
    View list of stars.
    """
    result = await db.execute(
        select(StarModel)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get(
    "/stars/{star_id}",
    tags=["Stars"],
    response_model=StarDetailSchema
)
async def get_star_detail(
        star_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Get specific star by ID with movie list.
    """
    stmt = select(StarModel).options(joinedload(StarModel.movies)).where(StarModel.id == star_id)
    result = await db.execute(stmt)
    star = result.scalars().first()
    if not star:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Star not found."
        )

    movie_titles = [movie.name for movie in star.movies] if star.movies else []

    return {
        **StarSchema.from_orm(star).dict(),
        "movie": movie_titles
    }


@router.put(
    "/stars/{star_id}",
    tags=["Stars"],
    response_model=StarSchema
)
async def update_star(
        star_id: int,
        new_name: str,
        db: AsyncSession = Depends(get_db),
):
    """
    Update star name. For admin only.
    """
    star = await db.get(StarModel, star_id)
    if not star:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Star not found."
        )

    existing_star = await db.execute(
        select(StarModel)
        .where(StarModel.name == new_name)
        .where(StarModel.id != star_id)
    )
    if existing_star.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Star with this name already exists."
        )

    star.name = new_name
    await db.commit()
    await db.refresh(star)

    return star


@router.delete(
    "/stars/{star_id}",
    tags=["Stars"],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_star(
        star_id: int,
        db: AsyncSession = Depends(get_db),
):
    """
    Delete a star by ID. For admin only.
    """
    star = await db.get(StarModel, star_id)
    if not star:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Star not found."
        )

    await db.delete(star)
    await db.commit()
