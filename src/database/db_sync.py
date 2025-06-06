from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.dependencies import get_settings
from database.session_postgresql import sync_postgresql_engine

SessionLocal = sessionmaker(bind=sync_postgresql_engine)

settings = get_settings()

SQLITE_DATABASE_URL = f"sqlite:///{settings.PATH_TO_DB}"
sqlite_engine = create_engine(SQLITE_DATABASE_URL, echo=False)

SQLLiteSessionLocal = sessionmaker(bind=sqlite_engine)
