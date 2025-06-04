import asyncio
import math
from typing import List, Dict, Tuple, cast, Any

import pandas as pd
from sqlalchemy import insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from tqdm import tqdm

from config import get_settings
from database import (
    CountryModel,
    GenreModel,
    ActorModel,
    MoviesGenresModel,
    ActorsMoviesModel,
    LanguageModel,
    MoviesLanguagesModel,
    MovieModel,
    UserGroupModel,
    UserGroupEnum,
)
from database import get_db_contextmanager

CHUNK_SIZE = 1000


class CSVDatabaseSeeder:
    """
    A class responsible for seeding the database from a CSV file using asynchronous SQLAlchemy.
    """

    def __init__(self, csv_file_path: str, db_session: AsyncSession) -> None:
        """
        Initializes the CSVDatabaseSeeder with the CSV file path and asynchronous database session.
        
        Args:
            csv_file_path: Path to the CSV file containing movie data.
        """
        self._csv_file_path = csv_file_path
        self._db_session = db_session

    async def is_db_populated(self) -> bool:
        """
        Determines whether the MovieModel table contains any records.
        
        Returns:
            True if at least one movie exists in the database; otherwise, False.
        """
        result = await self._db_session.execute(select(MovieModel).limit(1))
        first_movie = result.scalars().first()
        return first_movie is not None

    def _preprocess_csv(self) -> pd.DataFrame:
        """
        Cleans and normalizes the CSV file, removing duplicates and standardizing fields.
        
        Loads the CSV into a DataFrame, removes duplicate movie records, fills missing values in key columns with "Unknown", normalizes string fields (such as crew, genre, language, and status), converts date columns to `datetime.date`, and saves the cleaned data back to the original CSV file. Returns the cleaned DataFrame.
        """
        data = pd.read_csv(self._csv_file_path)
        data = data.drop_duplicates(subset=["names", "date_x"], keep="first")

        for col in ["crew", "genre", "country", "orig_lang", "status"]:
            data[col] = data[col].fillna("Unknown").astype(str)

        data["crew"] = (
            data["crew"]
            .str.replace(r"\s+", "", regex=True)
            .apply(
                lambda x: (
                    ",".join(sorted(set(x.split(","))))
                    if x != "Unknown"
                    else x
                )
            )
        )

        data["genre"] = data["genre"].str.replace("\u00a0", "", regex=True)
        data["date_x"] = data["date_x"].astype(str).str.strip()
        data["date_x"] = pd.to_datetime(
            data["date_x"], format="%Y-%m-%d", errors="raise"
        )
        data["date_x"] = data["date_x"].dt.date
        data["orig_lang"] = data["orig_lang"].str.replace(
            r"\s+", "", regex=True
        )
        data["status"] = data["status"].str.strip()

        print("Preprocessing CSV file...")
        data.to_csv(self._csv_file_path, index=False)
        print(f"CSV file saved to {self._csv_file_path}")
        return data

    async def _seed_user_groups(self) -> None:
        """
        Inserts default user groups into the database if none exist.
        
        Checks for existing user groups and, if absent, adds all groups defined in UserGroupEnum.
        """
        count_stmt = select(func.count(UserGroupModel.id))
        result = await self._db_session.execute(count_stmt)
        existing_groups = result.scalar()

        if existing_groups == 0:
            groups = [{"name": group.value} for group in UserGroupEnum]
            await self._db_session.execute(
                insert(UserGroupModel).values(groups)
            )
            await self._db_session.flush()

            print("User groups seeded successfully.")

    async def _get_or_create_bulk(
        self, model, items: List[str], unique_field: str
    ) -> Dict[str, object]:
        """
        Retrieves or creates model instances for a list of unique string items in bulk.
        
        For the specified model and unique field, fetches existing records matching the provided items. Any missing items are created in bulk and then retrieved. Returns a dictionary mapping each item string to its corresponding model instance.
        
        Args:
            model: The SQLAlchemy model class to query or insert into.
            items: List of unique string values to retrieve or create.
            unique_field: The model attribute that uniquely identifies each item.
        
        Returns:
            A dictionary mapping each item string to its model instance.
        """
        existing_dict: Dict[str, object] = {}

        if items:
            for i in range(0, len(items), CHUNK_SIZE):
                chunk = items[i : i + CHUNK_SIZE]
                result = await self._db_session.execute(
                    select(model).where(
                        getattr(model, unique_field).in_(chunk)
                    )
                )
                existing_in_chunk = result.scalars().all()
                for obj in existing_in_chunk:
                    key = getattr(obj, unique_field)
                    existing_dict[key] = obj

        new_items = [item for item in items if item not in existing_dict]
        new_records: list[Any] = [{unique_field: item} for item in new_items]

        if new_records:
            for i in range(0, len(new_records), CHUNK_SIZE):
                chunk = new_records[i : i + CHUNK_SIZE]
                await self._db_session.execute(insert(model).values(chunk))
                await self._db_session.flush()

            for i in range(0, len(new_items), CHUNK_SIZE):
                chunk = new_items[i : i + CHUNK_SIZE]
                result_new = await self._db_session.execute(
                    select(model).where(
                        getattr(model, unique_field).in_(chunk)
                    )
                )
                inserted_in_chunk = result_new.scalars().all()
                for obj in inserted_in_chunk:
                    key = getattr(obj, unique_field)
                    existing_dict[key] = obj

        return existing_dict

    async def _bulk_insert(
        self, table, data_list: List[Dict[str, int]]
    ) -> None:
        """
        Inserts a list of records into the specified table in chunks, showing progress.
        
        Args:
            table: The SQLAlchemy table or model to insert records into.
            data_list: List of dictionaries, each representing a row to insert.
        """
        total_records = len(data_list)
        if total_records == 0:
            return

        num_chunks = math.ceil(total_records / CHUNK_SIZE)
        table_name = getattr(table, "__tablename__", str(table))

        for chunk_index in tqdm(
            range(num_chunks), desc=f"Inserting into {table_name}"
        ):
            start = chunk_index * CHUNK_SIZE
            end = start + CHUNK_SIZE
            chunk = data_list[start:end]
            if chunk:
                await self._db_session.execute(insert(table).values(chunk))

        await self._db_session.flush()

    async def _prepare_reference_data(self, data: pd.DataFrame) -> Tuple[
        Dict[str, CountryModel],
        Dict[str, GenreModel],
        Dict[str, ActorModel],
        Dict[str, LanguageModel],
    ]:
        """
        Extracts unique countries, genres, actors, and languages from the DataFrame and ensures corresponding records exist in the database.
        
        Args:
            data: The preprocessed DataFrame containing movie information.
        
        Returns:
            A tuple of four dictionaries mapping string values to their respective model instances: (country_map, genre_map, actor_map, language_map).
        """
        countries = list(data["country"].unique())
        genres = {
            genre.strip()
            for genres_ in data["genre"].dropna()
            for genre in genres_.split(",")
            if genre.strip()
        }
        actors = {
            actor.strip()
            for crew in data["crew"].dropna()
            for actor in crew.split(",")
            if actor.strip()
        }
        languages = {
            lang.strip()
            for langs in data["orig_lang"].dropna()
            for lang in langs.split(",")
            if lang.strip()
        }

        country_map = await self._get_or_create_bulk(
            CountryModel, countries, "code"
        )
        genre_map = await self._get_or_create_bulk(
            GenreModel, list(genres), "name"
        )
        actor_map = await self._get_or_create_bulk(
            ActorModel, list(actors), "name"
        )
        language_map = await self._get_or_create_bulk(
            LanguageModel, list(languages), "name"
        )

        return (
            cast(Dict[str, CountryModel], country_map),
            cast(Dict[str, GenreModel], genre_map),
            cast(Dict[str, ActorModel], actor_map),
            cast(Dict[str, LanguageModel], language_map),
        )

    def _prepare_movies_data(
        self, data: pd.DataFrame, country_map: Dict[str, CountryModel]
    ) -> List[Dict[str, object]]:
        """
        Constructs a list of dictionaries representing movies for bulk insertion.
        
        Each dictionary contains the fields required for a MovieModel record, with country foreign keys resolved using the provided country map.
        """
        movies_data: List[Dict[str, object]] = []
        for _, row in tqdm(
            data.iterrows(), total=data.shape[0], desc="Processing movies"
        ):
            country = country_map[row["country"]]
            movie = {
                "name": row["names"],
                "date": row["date_x"],
                "score": float(row["score"]),
                "overview": row["overview"],
                "status": row["status"],
                "budget": float(row["budget_x"]),
                "revenue": float(row["revenue"]),
                "country_id": country.id,
            }
            movies_data.append(movie)
        return movies_data

    def _prepare_associations(
        self,
        data: pd.DataFrame,
        movie_ids: List[int],
        genre_map: Dict[str, GenreModel],
        actor_map: Dict[str, ActorModel],
        language_map: Dict[str, LanguageModel],
    ) -> Tuple[
        List[Dict[str, int]], List[Dict[str, int]], List[Dict[str, int]]
    ]:
        """
        Creates bulk association records linking movies to genres, actors, and languages.
        
        Given a DataFrame of movies, their corresponding database IDs, and mappings of genre, actor, and language names to model instances, generates lists of dictionaries representing many-to-many associations for bulk insertion.
        
        Args:
            data: DataFrame containing movie information.
            movie_ids: List of database IDs for the movies, matching the DataFrame row order.
            genre_map: Mapping from genre names to GenreModel instances.
            actor_map: Mapping from actor names to ActorModel instances.
            language_map: Mapping from language names to LanguageModel instances.
        
        Returns:
            A tuple of three lists:
                - movie_genres_data: Association records for movies and genres.
                - movie_actors_data: Association records for movies and actors.
                - movie_languages_data: Association records for movies and languages.
        """
        movie_genres_data: List[Dict[str, int]] = []
        movie_actors_data: List[Dict[str, int]] = []
        movie_languages_data: List[Dict[str, int]] = []

        for i, (_, row) in enumerate(
            tqdm(
                data.iterrows(),
                total=data.shape[0],
                desc="Processing associations",
            )
        ):
            movie_id = movie_ids[i]

            for genre_name in row["genre"].split(","):
                genre_name = genre_name.strip()
                if genre_name:
                    genre = genre_map[genre_name]
                    movie_genres_data.append(
                        {"movie_id": movie_id, "genre_id": genre.id}
                    )

            for actor_name in row["crew"].split(","):
                actor_name = actor_name.strip()
                if actor_name:
                    actor = actor_map[actor_name]
                    movie_actors_data.append(
                        {"movie_id": movie_id, "actor_id": actor.id}
                    )

            for lang_name in row["orig_lang"].split(","):
                lang_name = lang_name.strip()
                if lang_name:
                    language = language_map[lang_name]
                    movie_languages_data.append(
                        {"movie_id": movie_id, "language_id": language.id}
                    )

        return movie_genres_data, movie_actors_data, movie_languages_data

    async def seed(self) -> None:
        """
        Seeds the database with movie data and related associations from the CSV file.
        
        This method preprocesses the CSV data, ensures reference entities (countries, genres, actors, languages) exist, inserts movie records, and establishes many-to-many relationships between movies and genres, actors, and languages. Commits the transaction upon success or raises exceptions on failure.
        """
        try:
            if self._db_session.in_transaction():
                print("Rolling back existing transaction.")
                await self._db_session.rollback()

            await self._seed_user_groups()

            data = self._preprocess_csv()

            country_map, genre_map, actor_map, language_map = (
                await self._prepare_reference_data(data)
            )

            movies_data = self._prepare_movies_data(data, country_map)

            result = await self._db_session.execute(
                insert(MovieModel).returning(MovieModel.id), movies_data
            )
            movie_ids = list(result.scalars().all())

            movie_genres_data, movie_actors_data, movie_languages_data = (
                self._prepare_associations(
                    data, movie_ids, genre_map, actor_map, language_map
                )
            )

            await self._bulk_insert(MoviesGenresModel, movie_genres_data)
            await self._bulk_insert(ActorsMoviesModel, movie_actors_data)
            await self._bulk_insert(MoviesLanguagesModel, movie_languages_data)

            await self._db_session.commit()
            print("Seeding completed.")

        except SQLAlchemyError as e:
            print(f"An error occurred: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise


async def main() -> None:
    """
    Asynchronously initializes and runs the CSV-to-database seeding process.
    
    Checks if the movie database is already populated; if not, performs data seeding from the specified CSV file. Prints status messages indicating the outcome.
    """
    settings = get_settings()
    async with get_db_contextmanager() as db_session:
        seeder = CSVDatabaseSeeder(settings.PATH_TO_MOVIES_CSV, db_session)

        if not await seeder.is_db_populated():
            try:
                await seeder.seed()
                print("Database seeding completed successfully.")
            except Exception as e:
                print(f"Failed to seed the database: {e}")
        else:
            print("Database is already populated. Skipping seeding.")


if __name__ == "__main__":
    asyncio.run(main())
