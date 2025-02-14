import pytest
from unittest.mock import AsyncMock, MagicMock

from src.models.users import User
from src.repositories.users import UserRepository
from src.schemas.user import UserCreate


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        avatar="https://example.com/avatar.jpg",
        confirmed=False,
        role="USER",
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(1)

    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_username("testuser")

    assert user is not None
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="hashedpassword",
        role="USER",
    )

    avatar_url = "https://example.com/avatar.jpg"

    result = await user_repository.create_user(user_data, avatar=avatar_url)

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.avatar == avatar_url
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    new_avatar_url = "https://example.com/new-avatar.jpg"
    updated_user = await user_repository.update_avatar_url(
        "test@example.com", new_avatar_url
    )

    assert updated_user is not None
    assert updated_user.avatar == new_avatar_url
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(test_user)


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.confirmed_email("test@example.com")

    assert test_user.confirmed is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_password(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    new_password = "new_hashed_password"
    await user_repository.update_password("test@example.com", new_password)

    assert test_user.hashed_password == new_password
    mock_session.commit.assert_awaited_once()
