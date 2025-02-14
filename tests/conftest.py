import asyncio

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.models.users import User
from src.models.contacts import Contact
from src.database.db import Base
from src.dependencies.db import get_db
from src.dependencies.redis_cache import get_redis
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    Hash,
)

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "testuser",
    "email": "testuser@gmail.com",
    "password": "1234567890",
    "role": "USER",
}

test_admin_user = {
    "username": "testadmin",
    "email": "testadmin@gmail.com",
    "password": "1234567890",
    "role": "ADMIN",
}


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = Hash().get_password_hash(test_user["password"])
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                avatar="<https://twitter.com/gravatar>",
                role="USER",
            )
            admin_user = User(
                username=test_admin_user["username"],
                email=test_admin_user["email"],
                hashed_password=hash_password,
                confirmed=True,
                avatar="<https://twitter.com/gravatar>",
                role="ADMIN",
            )
            session.add(current_user)
            session.add(admin_user)
            await session.commit()

    asyncio.run(init_models())


class FakeRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value):
        self.store[key] = value

    async def expire(self, key, time):
        pass


@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    def fake_redis():
        return FakeRedis()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = fake_redis

    yield TestClient(app)


@pytest.fixture()
async def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock()
    redis_mock.expire = AsyncMock()
    return redis_mock


@pytest.fixture()
def get_existing_token():
    token = create_access_token(data={"sub": "testuser"})
    return token


@pytest.fixture()
def get_token():
    token = create_access_token(data={"sub": "testsecond"})
    return token


@pytest.fixture()
def get_refresh_token():
    token = create_refresh_token(data={"sub": "testsecond"})
    return token


@pytest.fixture()
def get_reset_token():
    token = create_reset_token(email="testsecond@gmail.com")
    return token


@pytest_asyncio.fixture()
async def get_admin_token():
    token = create_access_token(data={"sub": "testadmin", "role": "ADMIN"})
    return token


@pytest.fixture(autouse=True)
def mock_cloudinary_upload():
    with patch("cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {
            "public_id": "mocked_public_id",
            "secure_url": "https://mocked.cloudinary.com/image.jpg",
        }
        yield mock_upload
