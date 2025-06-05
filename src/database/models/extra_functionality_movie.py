from sqlalchemy import Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .movies import MovieModel
from .accounts import UserModel
from database.models.base import Base


class MovieLike(Base):
    __tablename__ = "movie_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    is_liked: Mapped[bool] = mapped_column(Boolean, nullable=False)  # True — like, False — dislike

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="user_movie_like_unique"),)


class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="favorite_movies")
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="favorited_by")

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_favorite"),)


class MovieRating(Base):
    __tablename__ = "movie_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="movie_ratings")
    movie: Mapped["MovieModel"] = relationship("MovieModel", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="user_movie_rating_unique"),
    )

