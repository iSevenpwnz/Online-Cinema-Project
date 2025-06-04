from logging.config import fileConfig

from alembic import context

from database.models import movies, accounts # noqa: F401
from database.models.base import Base
from database.session_postgresql import sync_postgresql_engine


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Executes database migrations in offline mode using the synchronous PostgreSQL engine.
    
    Configures the Alembic context with the database connection and target metadata, enabling comparison of column types and server defaults. Runs all pending migrations within a transaction context.
    """
    connectable = sync_postgresql_engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online() -> None:
    """
    Executes database migrations in online mode using a live PostgreSQL connection.
    
    Establishes a connection with the synchronous PostgreSQL engine, configures the Alembic context for migration operations, and applies all pending migrations within a transaction.
    """
    connectable = sync_postgresql_engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
