import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings, get_accounts_email_notificator, get_s3_storage_client
from database import (
    reset_database,
    get_db_contextmanager,
    UserGroupEnum,
    UserGroupModel
)
from database.populate import CSVDatabaseSeeder
from main import app
from security.interfaces import JWTAuthManagerInterface
from security.token_manager import JWTAuthManager
from storages import S3StorageClient
from tests.doubles.fakes.storage import FakeS3Storage
from tests.doubles.stubs.emails import StubEmailSender


def pytest_configure(config):
    """
    Registers custom pytest markers for test categorization.
    
    Adds "e2e" for end-to-end tests, "order" for specifying test execution order, and "unit" for unit tests to the pytest configuration.
    """
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "order: Specify the order of test execution"
    )
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_db(request):
    """
    Resets the SQLite database before each test unless the test is marked as end-to-end.
    
    Skips the reset for tests marked with 'e2e' to preserve database state across end-to-end tests.
    """
    if "e2e" in request.keywords:
        yield
    else:
        await reset_database()
        yield


@pytest_asyncio.fixture(scope="session")
async def reset_db_once_for_e2e(request):
    """
    Resets the database once before running end-to-end tests.
    
    This session-scoped fixture ensures the database is initialized to a clean state prior to executing E2E tests.
    """
    await reset_database()


@pytest_asyncio.fixture(scope="session")
async def settings():
    """
    Provides application settings for tests.
    
    Returns:
        The application settings object as obtained from get_settings().
    """
    return get_settings()


@pytest_asyncio.fixture(scope="function")
async def email_sender_stub():
    """
    Provides a stub email sender for testing.
    
    Yields an instance of StubEmailSender to simulate email sending in tests.
    """
    return StubEmailSender()


@pytest_asyncio.fixture(scope="function")
async def s3_storage_fake():
    """
    Provides a fake S3 storage client for testing.
    
    Returns:
        An instance of FakeS3Storage to simulate S3 interactions during tests.
    """
    return FakeS3Storage()


@pytest_asyncio.fixture(scope="session")
async def s3_client(settings):
    """
    Provides a session-scoped S3 storage client configured with application settings.
    
    Returns:
        An instance of S3StorageClient initialized with endpoint, credentials, and bucket name from the application settings.
    """
    return S3StorageClient(
        endpoint_url=settings.S3_STORAGE_ENDPOINT,
        access_key=settings.S3_STORAGE_ACCESS_KEY,
        secret_key=settings.S3_STORAGE_SECRET_KEY,
        bucket_name=settings.S3_BUCKET_NAME
    )


@pytest_asyncio.fixture(scope="function")
async def client(email_sender_stub, s3_storage_fake):
    """
    Provides an asynchronous HTTP client for testing the FastAPI application.
    
    Overrides the application's email sender and S3 storage dependencies with test doubles for the duration of each test. Yields an `AsyncClient` instance configured to interact with the test app.
    """
    app.dependency_overrides[get_accounts_email_notificator] = lambda: email_sender_stub
    app.dependency_overrides[get_s3_storage_client] = lambda: s3_storage_fake

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def e2e_client():
    """
    Provides an asynchronous HTTP client for end-to-end tests.
    
    Yields:
        An AsyncClient instance configured to interact with the FastAPI application for the duration of the test session.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Yields an asynchronous database session for use in tests.
    
    Ensures that each test receives a fresh session, which is properly closed after the test completes.
    """
    async with get_db_contextmanager() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def e2e_db_session():
    """
    Yields a session-scoped asynchronous database session for end-to-end tests.
    
    The same database session is shared across all E2E tests in the session, which may result in shared state if tests are run concurrently.
    """
    async with get_db_contextmanager() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def jwt_manager() -> JWTAuthManagerInterface:
    """
    Provides an asynchronous fixture that returns a JWT authentication manager configured with application secret keys and signing algorithm.
    """
    settings = get_settings()
    return JWTAuthManager(
        secret_key_access=settings.SECRET_KEY_ACCESS,
        secret_key_refresh=settings.SECRET_KEY_REFRESH,
        algorithm=settings.JWT_SIGNING_ALGORITHM
    )


@pytest_asyncio.fixture(scope="function")
async def seed_user_groups(db_session: AsyncSession):
    """
    Seeds the UserGroupModel table with all user groups defined in UserGroupEnum.
    
    Inserts each user group into the database and commits the transaction, then yields
    the asynchronous database session for use in tests.
    """
    groups = [{"name": group.value} for group in UserGroupEnum]
    await db_session.execute(insert(UserGroupModel).values(groups))
    await db_session.commit()
    yield db_session


@pytest_asyncio.fixture(scope="function")
async def seed_database(db_session):
    """
    Seeds the database with test data from a CSV file if the database is empty.
    
    Initializes a `CSVDatabaseSeeder` using the CSV file path from settings and the provided database session. If the database is not already populated, it loads data from the CSV file before yielding the session for use in tests.
    """
    settings = get_settings()
    seeder = CSVDatabaseSeeder(csv_file_path=settings.PATH_TO_MOVIES_CSV, db_session=db_session)

    if not await seeder.is_db_populated():
        await seeder.seed()

    yield db_session
