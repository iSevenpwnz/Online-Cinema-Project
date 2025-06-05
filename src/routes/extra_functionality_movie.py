

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.extra_functionality_movie import LikeDislikeSchema, FavoriteSchema, RatingSchema
from security import get_current_user
from database.models import MovieLike, MovieFavorite, MovieRating, MovieModel

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.post("/movies/{movie_id}/like")
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


@router.post("/favorite")
def add_favorite(data: FavoriteSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    fav = db.query(MovieFavorite).filter_by(user_id=user.id, movie_id=data.movie_id).first()
    if fav:
        raise HTTPException(400, "Already in favorites")
    db.add(MovieFavorite(user_id=user.id, movie_id=data.movie_id))
    db.commit()
    return {"message": "Added to favorites"}

@router.delete("/favorite/{movie_id}")
def remove_favorite(movie_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    fav = db.query(MovieFavorite).filter_by(user_id=user.id, movie_id=movie_id).first()
    if not fav:
        raise HTTPException(404, "Not in favorites")
    db.delete(fav)
    db.commit()
    return {"message": "Removed from favorites"}

@router.post("/rate")
def rate_movie(data: RatingSchema, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rating = db.query(MovieRating).filter_by(user_id=user.id, movie_id=data.movie_id).first()
    if rating:
        rating.rating = data.rating
    else:
        db.add(MovieRating(user_id=user.id, movie_id=data.movie_id, rating=data.rating))
    db.commit()
    return {"message": "Rating saved"}
