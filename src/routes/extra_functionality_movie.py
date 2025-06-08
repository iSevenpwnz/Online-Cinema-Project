from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import joinedload
from database import get_db
from database.models.movies import MovieModel, GenreModel
from schemas import (
    LikeDislikeSchema,
    MovieRatingSchema,
    MovieListResponseSchema,
    MovieListItemSchema,
)
from schemas.extra_functionality_movie import (
    MessageResponse,
    AverageRatingResponse,
    MovieRatingResponse,
)
from security.http import get_current_user
from database.models import MovieLike, MovieRating, FavoriteMovie
from typing import Optional, Any

router = APIRouter()


@router.post(
    "/movies/{movie_id}/like",
    response_model=MessageResponse,
    summary="Like or dislike a movie",
    description="Allows a user to like or dislike a movie. "
    "If the user already has a reaction, it "
    "will be updated or removed based on the new input.",
)
async def like_or_dislike_movie(
    movie_id: int,
    data: LikeDislikeSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> MessageResponse:
    result = await db.execute(
        select(MovieLike).where(
            MovieLike.user_id == user.id, MovieLike.movie_id == movie_id
        )
    )
    existing = result.scalars().first()

    if existing:
        if data.is_liked is None:
            return MessageResponse(message="No change")

        if existing.is_liked == data.is_liked:
            await db.delete(existing)
            await db.commit()
            return MessageResponse(message="Reaction removed")
        else:
            existing.is_liked = data.is_liked
            await db.commit()
            return MessageResponse(message="Reaction updated")
    else:
        if data.is_liked is None:
            return MessageResponse(message="No reaction to add")

        new_reaction = MovieLike(
            user_id=user.id, movie_id=movie_id, is_liked=data.is_liked
        )
        db.add(new_reaction)
        await db.commit()
        return MessageResponse(message="Reaction added")


@router.get(
    "/movies/{movie_id}/likes-stats",
    response_model=dict,
    summary="Get movie likes/dislikes statistics",
    description="Returns the count of likes and dislikes for a movie.",
)
async def get_movie_likes_stats(
    movie_id: int, db: AsyncSession = Depends(get_db)
) -> dict:
    """Get likes and dislikes statistics for a movie."""

    # Count likes
    likes_result = await db.execute(
        select(func.count(MovieLike.id)).where(
            MovieLike.movie_id == movie_id, MovieLike.is_liked
        )
    )
    likes_count = likes_result.scalar() or 0

    # Count dislikes
    dislikes_result = await db.execute(
        select(func.count(MovieLike.id)).where(
            MovieLike.movie_id == movie_id, ~MovieLike.is_liked
        )
    )
    dislikes_count = dislikes_result.scalar() or 0

    total_reactions = likes_count + dislikes_count
    like_percentage = (
        (likes_count / total_reactions * 100) if total_reactions > 0 else 0
    )

    return {
        "movie_id": movie_id,
        "likes": likes_count,
        "dislikes": dislikes_count,
        "total_reactions": total_reactions,
        "like_percentage": round(like_percentage, 1),
    }


@router.post(
    "/movies/{movie_id}/favorite",
    response_model=MessageResponse,
    summary="Toggle favorite status of a movie",
    description="Allows a user to add or remove a "
    "movie from their favorites.",
)
async def toggle_favorite(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> MessageResponse:
    result = await db.execute(
        select(FavoriteMovie).where(
            FavoriteMovie.user_id == user.id,
            FavoriteMovie.movie_id == movie_id,
        )
    )
    favorite = result.scalars().first()

    if favorite:
        await db.delete(favorite)
        await db.commit()
        return MessageResponse(message="Removed from favorites")
    else:
        new_fav = FavoriteMovie(user_id=user.id, movie_id=movie_id)
        db.add(new_fav)
        await db.commit()
        return MessageResponse(message="Added to favorites")


@router.get(
    "/movies/{movie_id}/is-favorite",
    response_model=dict,
    summary="Check if movie is in user's favorites",
    description="Returns whether the movie is in the current user's favorites.",
)
async def is_movie_favorite(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> dict:
    """Check if a movie is in the current user's favorites."""
    result = await db.execute(
        select(FavoriteMovie).where(
            FavoriteMovie.user_id == user.id,
            FavoriteMovie.movie_id == movie_id,
        )
    )
    favorite = result.scalars().first()

    return {
        "movie_id": movie_id,
        "is_favorite": favorite is not None,
        "message": "In favorites" if favorite else "Not in favorites",
    }


@router.post(
    "/movies/{movie_id}/rate",
    response_model=MovieRatingResponse,
    summary="Rate a movie",
    description="Allows a user to rate a movie. "
    "If the user has already rated the movie, "
    "the rating will be updated.",
)
async def rate_movie(
    movie_id: int,
    data: MovieRatingSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> MovieRatingResponse:
    result = await db.execute(
        select(MovieRating).where(
            MovieRating.user_id == user.id, MovieRating.movie_id == movie_id
        )
    )
    existing = result.scalars().first()

    if existing:
        existing.rating = data.rating
    else:
        rating = MovieRating(
            user_id=user.id, movie_id=movie_id, rating=data.rating
        )
        db.add(rating)

    await db.commit()
    return MovieRatingResponse(
        movie_id=movie_id, rating=data.rating, message="Success"
    )


@router.get(
    "/movies/{movie_id}/my-rating",
    response_model=MovieRatingResponse,
    summary="Get user's rating for a movie",
    description="Returns the current user's rating for a specific movie.",
)
async def get_user_rating(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> MovieRatingResponse:
    """Get the current user's rating for a specific movie."""
    result = await db.execute(
        select(MovieRating).where(
            MovieRating.user_id == user.id, MovieRating.movie_id == movie_id
        )
    )
    rating = result.scalars().first()

    if rating is None:
        return MovieRatingResponse(
            movie_id=movie_id, rating=0, message="No rating found"
        )

    return MovieRatingResponse(
        movie_id=movie_id, rating=rating.rating, message="Success"
    )


@router.get(
    "/movies/{movie_id}/average-rating",
    response_model=AverageRatingResponse,
    summary="Get average rating of a movie",
    description="Calculates and returns the average rating of a movie.",
)
async def get_average_rating(
    movie_id: int, db: AsyncSession = Depends(get_db)
) -> AverageRatingResponse:
    result = await db.execute(
        select(func.avg(MovieRating.rating)).where(
            MovieRating.movie_id == movie_id
        )
    )
    avg_rating = result.scalar()

    if avg_rating is None:
        return AverageRatingResponse(
            average_rating=None, message="No ratings yet"
        )

    return AverageRatingResponse(
        average_rating=round(avg_rating, 2), message="Success"
    )


@router.get(
    "/favorites",
    response_model=MovieListResponseSchema,
    summary="Get user's favorite movies",
    description="Retrieves a paginated list of user's favorite movies with search, filter, and sort capabilities.",
)
async def get_user_favorites(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(
        10, ge=1, le=20, description="Number of items per page"
    ),
    search: Optional[str] = Query(
        None, description="Search by movie name, description, or director"
    ),
    genre: Optional[str] = Query(None, description="Filter by genre name"),
    year_from: Optional[int] = Query(
        None, description="Filter by minimum year"
    ),
    year_to: Optional[int] = Query(None, description="Filter by maximum year"),
    sort_by: str = Query(
        "added_date",
        description="Sort by: name, year, imdb, price, added_date",
    ),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> MovieListResponseSchema:
    """
    Get user's favorite movies with search, filter, and sort functionality.

    Supports:
    - Pagination
    - Search by movie name, description, directors, or stars
    - Filter by genre and year range
    - Sort by various fields
    """

    # Base query for user's favorite movies
    query = (
        select(MovieModel)
        .join(FavoriteMovie, MovieModel.id == FavoriteMovie.movie_id)
        .where(FavoriteMovie.user_id == user.id)
        .options(
            joinedload(MovieModel.genres),
            joinedload(MovieModel.directors),
            joinedload(MovieModel.stars),
        )
    )

    # Apply search filter
    if search:
        from database.models.movies import DirectorModel, StarModel

        search_filter = or_(
            MovieModel.name.ilike(f"%{search}%"),
            MovieModel.description.ilike(f"%{search}%"),
            MovieModel.directors.any(DirectorModel.name.ilike(f"%{search}%")),
            MovieModel.stars.any(StarModel.name.ilike(f"%{search}%")),
        )
        query = query.where(search_filter)

    # Apply genre filter
    if genre:
        query = query.where(
            MovieModel.genres.any(GenreModel.name.ilike(f"%{genre}%"))
        )

    # Apply year filters
    if year_from:
        query = query.where(MovieModel.year >= year_from)
    if year_to:
        query = query.where(MovieModel.year <= year_to)

    # Apply sorting
    sort_column: Any = MovieModel.name  # default
    if sort_by == "year":
        sort_column = MovieModel.year
    elif sort_by == "imdb":
        sort_column = MovieModel.imdb
    elif sort_by == "price":
        sort_column = MovieModel.price
    elif sort_by == "added_date":
        # Sort by when movie was added to favorites
        # FavoriteMovie is already joined above, no need to join again
        sort_column = (
            FavoriteMovie.id
        )  # Assuming id represents order of addition

    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Count total items with same filters as main query
    count_query = (
        select(func.count(MovieModel.id))
        .join(FavoriteMovie, MovieModel.id == FavoriteMovie.movie_id)
        .where(FavoriteMovie.user_id == user.id)
    )

    # Apply same filters to count query
    if search:
        from database.models.movies import DirectorModel, StarModel

        search_filter_count = or_(
            MovieModel.name.ilike(f"%{search}%"),
            MovieModel.description.ilike(f"%{search}%"),
            MovieModel.directors.any(DirectorModel.name.ilike(f"%{search}%")),
            MovieModel.stars.any(StarModel.name.ilike(f"%{search}%")),
        )
        count_query = count_query.where(search_filter_count)

    if genre:
        count_query = count_query.where(
            MovieModel.genres.any(GenreModel.name.ilike(f"%{genre}%"))
        )

    if year_from:
        count_query = count_query.where(MovieModel.year >= year_from)
    if year_to:
        count_query = count_query.where(MovieModel.year <= year_to)

    total_result = await db.execute(count_query)
    total_items = total_result.scalar() or 0

    if total_items == 0:
        return MovieListResponseSchema(
            movies=[],
            prev_page=None,
            next_page=None,
            total_pages=0,
            total_items=0,
        )

    # Calculate pagination
    total_pages = (total_items + per_page - 1) // per_page
    offset = (page - 1) * per_page

    # Apply pagination
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(query)
    movies = result.scalars().unique().all()

    # Convert to response schema
    movie_items = [
        MovieListItemSchema(
            id=movie.id,
            name=movie.name,
            year=movie.year,
            imdb=movie.imdb,
            price=float(movie.price),
            description=movie.description,
        )
        for movie in movies
    ]

    # Generate pagination links
    base_url = "/extra_functionality/favorites"
    prev_page = None
    next_page = None

    if page > 1:
        prev_params = f"?page={page - 1}&per_page={per_page}"
        if search:
            prev_params += f"&search={search}"
        if genre:
            prev_params += f"&genre={genre}"
        if year_from:
            prev_params += f"&year_from={year_from}"
        if year_to:
            prev_params += f"&year_to={year_to}"
        prev_params += f"&sort_by={sort_by}&sort_order={sort_order}"
        prev_page = base_url + prev_params

    if page < total_pages:
        next_params = f"?page={page + 1}&per_page={per_page}"
        if search:
            next_params += f"&search={search}"
        if genre:
            next_params += f"&genre={genre}"
        if year_from:
            next_params += f"&year_from={year_from}"
        if year_to:
            next_params += f"&year_to={year_to}"
        next_params += f"&sort_by={sort_by}&sort_order={sort_order}"
        next_page = base_url + next_params

    return MovieListResponseSchema(
        movies=movie_items,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )
