from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from schemas import LikeDislikeSchema, MovieRatingSchema
from schemas.extra_functionality_movie import MessageResponse, AverageRatingResponse, MovieRatingResponse
from security.http import get_current_user
from database.models import MovieLike, MovieRating, FavoriteMovie

router = APIRouter()


@router.post("/movies/{movie_id}/like",
             response_model=MessageResponse,
             summary="Like or dislike a movie",
             description="Allows a user to like or dislike a movie. "
                         "If the user already has a reaction, it "
                         "will be updated or removed based on the new input.")
async def like_or_dislike_movie(
    movie_id: int,
    data: LikeDislikeSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> MessageResponse:
    result = await db.execute(
        select(MovieLike).where(
            MovieLike.user_id == user.id,
            MovieLike.movie_id == movie_id
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
            user_id=user.id,
            movie_id=movie_id,
            is_liked=data.is_liked
        )
        db.add(new_reaction)
        await db.commit()
        return MessageResponse(message="Reaction added")


@router.post("/movies/{movie_id}/favorite",
             response_model=MessageResponse,
             summary="Toggle favorite status of a movie",
             description="Allows a user to add or remove a "
                         "movie from their favorites.")
async def toggle_favorite(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> MessageResponse:
    result = await db.execute(
        select(FavoriteMovie).where(
            FavoriteMovie.user_id == user.id,
            FavoriteMovie.movie_id == movie_id
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


@router.post("/movies/{movie_id}/rate",
             response_model=MovieRatingResponse,
             summary="Rate a movie",
             description="Allows a user to rate a movie. "
                         "If the user has already rated the movie, "
                         "the rating will be updated.")
async def rate_movie(
    movie_id: int,
    data: MovieRatingSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
) -> MovieRatingResponse:
    result = await db.execute(
        select(MovieRating).where(
            MovieRating.user_id == user.id,
            MovieRating.movie_id == movie_id
        )
    )
    existing = result.scalars().first()

    if existing:
        existing.rating = data.rating
    else:
        rating = MovieRating(user_id=user.id, movie_id=movie_id, rating=data.rating)
        db.add(rating)

    await db.commit()
    return MovieRatingResponse(
        movie_id=movie_id,
        rating=data.rating,
    )


@router.get("/movies/{movie_id}/average-rating",
            response_model=AverageRatingResponse,
            summary="Get average rating of a movie",
            description="Calculates and returns the average rating of a movie.")
async def get_average_rating(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
) -> AverageRatingResponse:
    result = await db.execute(
        select(func.avg(MovieRating.rating)).where(
            MovieRating.movie_id == movie_id
        )
    )
    avg_rating = result.scalar()

    if avg_rating is None:
        return AverageRatingResponse(average_rating=None, message="No ratings yet")

    return AverageRatingResponse(average_rating=round(avg_rating, 2), message="Success")
