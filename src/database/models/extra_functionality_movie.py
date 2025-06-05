from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class MovieLike(Base):
    __tablename__ = "movie_likes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    is_liked = Column(Boolean, nullable=False)  # True — like, False — dislike

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="user_movie_like_unique"),)


class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)

    user = relationship("User", back_populates="favorite_movies")
    movie = relationship("Movie", back_populates="favorited_by")

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_favorite"),)


class MovieRating(Base):
    __tablename__ = "movie_ratings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    rating = Column(Integer, nullable=False)

    user = relationship("User", back_populates="movie_ratings")
    movie = relationship("Movie", back_populates="movie_ratings")

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="user_movie_rating_unique"),)

