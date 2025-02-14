import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.models.users import User
from src.models.contacts import Contact
from src.repositories.contacts import ContactsRepository
from src.schemas.contact import ContactBase


@pytest.fixture
def contact_repository(mock_session):
    return ContactsRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        ContactBase(
            id=1,
            first_name="test",
            last_name="test",
            email="test@sample.com",
            phone="0500000000",
            birthday="2000-01-01",
            additional_info="",
            user=user,
        )
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "test"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1,
        first_name="test",
        last_name="test",
        email="test@sample.com",
        phone="0500000000",
        birthday="2000-01-01",
        additional_info="",
        user=user,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(id=1, user=user)

    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "test"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactBase(
        first_name="new",
        last_name="test",
        email="test@sample.com",
        phone="0500000000",
        birthday="2000-01-01",
        additional_info="",
    )

    result = await contact_repository.create_contact(body=contact_data, user=user)

    assert isinstance(result, Contact)
    assert result.first_name == "new"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    contact_data = ContactBase(
        first_name="updated",
        last_name="test",
        email="test@sample.com",
        phone="0500000000",
        birthday="2000-01-01",
        additional_info="",
    )
    existing_contact = Contact(
        id=1,
        first_name="old",
        last_name="test",
        email="test@sample.com",
        phone="0500000000",
        birthday="2000-01-01",
        additional_info="",
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(id=1, body=contact_data, user=user)

    assert result is not None
    assert result.first_name == "updated"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_delete_contact(contact_repository, mock_session, user):
    existing_contact = Contact(
        id=1,
        first_name="old",
        last_name="test",
        email="test@sample.com",
        phone="0500000000",
        birthday="2000-01-01",
        additional_info="",
        user=user,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.delete_contact(id=1, user=user)

    assert result is not None
    assert result.first_name == "old"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(contact_repository, mock_session, user):
    today = datetime.today().date()
    next_week = today + timedelta(days=6)

    contact_in_range = Contact(
        id=1,
        first_name="Kate",
        last_name="First",
        email="Kate@example.com",
        phone="1111111111",
        birthday=next_week,
        user_id=user.id,
    )

    contact_out_of_range = Contact(
        id=2,
        first_name="Alice",
        last_name="Second",
        email="Alice@example.com",
        phone="2222222222",
        birthday=today - timedelta(days=30),
        user_id=user.id,
    )

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact_in_range]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_upcoming_birthdays(user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Kate"
    assert contacts[0].birthday == next_week
