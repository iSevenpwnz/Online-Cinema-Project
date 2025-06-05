from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import LikeDislikeSchema, MovieRatingSchema
from schemas.extra_functionality_movie import MessageResponse, AverageRatingResponse
from security.http import get_current_user
from database.models import MovieLike, MovieRating, FavoriteMovie

router = APIRouter()


@router.post("/movies/{movie_id}/like",
             response_model=MessageResponse,
             summary="Like or dislike a movie"
             )
def like_or_dislike_movie(
    movie_id: int,
    data: LikeDislikeSchema,  # data.is_liked = True / False
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    existing = db.query(MovieLike).filter_by(
        user_id=user.id,
        movie_id=movie_id
    ).first()

    if existing:
        if existing.is_liked == data.is_liked:
            db.delete(existing)
            db.commit()
            return {"message": "Reaction removed"}
        else:
            existing.is_liked = data.is_liked
            db.commit()
            return {"message": "Reaction updated"}
    else:
        new_reaction = MovieLike(
            user_id=user.id,
            movie_id=movie_id,
            is_liked=data.is_liked
        )
        db.add(new_reaction)
        db.commit()
        return {"message": "Reaction added"}


@router.post("/movies/{movie_id}/favorite",
             response_model=MessageResponse,
             summary="Toggle favorite status of a movie"
             )
def toggle_favorite(
    movie_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    favorite = db.query(FavoriteMovie).filter_by(
        user_id=user.id,
        movie_id=movie_id
    ).first()

    if favorite:
        db.delete(favorite)
        db.commit()
        return {"message": "Removed from favorites"}
    else:
        new_fav = FavoriteMovie(user_id=user.id, movie_id=movie_id)
        db.add(new_fav)
        db.commit()
        return {"message": "Added to favorites"}


@router.post("/movies/{movie_id}/rate",
             response_model=AverageRatingResponse,
             summary="Rate a movie"
             )
def rate_movie(
    movie_id: int,
    data: MovieRatingSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    existing = db.query(MovieRating).filter_by(user_id=user.id, movie_id=movie_id).first()

    if existing:
        existing.rating = data.rating
    else:
        rating = MovieRating(user_id=user.id, movie_id=movie_id, rating=data.rating)
        db.add(rating)
    db.commit()
    return {"message": "Rating saved"}


@router.get("/movies/{movie_id}/average-rating")
def get_average_rating(
    movie_id: int,
    db: Session = Depends(get_db)
):
    from sqlalchemy import func

    avg_rating = db.query(func.avg(MovieRating.rating))\
                   .filter_by(movie_id=movie_id)\
                   .scalar()

    if avg_rating is None:
        return {"average_rating": None, "message": "No ratings yet"}
    return {"average_rating": round(avg_rating, 2)}
