from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.repositories.contacts import ContactsRepository
from src.schemas.contact import ContactCreate
from src.models.users import User


def _handle_integrity_error(e: IntegrityError):
    """
    Handles database integrity errors, specifically unique constraint violations.

    Args:
        e (IntegrityError): The exception instance.

    Raises:
        HTTPException: A 409 Conflict error if a duplicate contact exists.
        HTTPException: A 400 Bad Request error for other integrity issues.
    """
    if "unique_contact_user" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Контакт з такою назвою вже існує.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Помилка цілісності даних.",
        )


class ContactsService:
    """
    Service class for managing contacts.

    This class acts as an intermediary between the API layer and the repository,
    handling business logic and error handling.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the ContactsService.

        Args:
            db (AsyncSession): The asynchronous database session.
        """
        self.repository = ContactsRepository(db)

    async def get_contacts(
        self, user: User, skip: str, limit: str, name: str, email: str
    ):
        """
        Retrieves a list of contacts for a specific user with optional filters.

        Args:
            user (User): The authenticated user.
            skip (str): Number of records to skip for pagination.
            limit (str): Maximum number of contacts to return.
            name (str, optional): Name filter for contacts.
            email (str, optional): Email filter for contacts.

        Returns:
            List[Contact]: A list of contacts matching the criteria.
        """
        return await self.repository.get_contacts(user, skip, limit, name, email)

    async def get_contact_by_id(self, id: int, user: User):
        """
        Retrieves a contact by its ID.

        Args:
            id (int): The contact's ID.
            user (User): The authenticated user.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        return await self.repository.get_contact_by_id(id, user)

    async def create_contact(self, body: ContactCreate, user: User):
        """
        Creates a new contact for a user.

        Args:
            body (ContactCreate): The contact data.
            user (User): The authenticated user.

        Returns:
            Contact: The created contact.

        Raises:
            HTTPException: If a contact with the same name already exists.
        """
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def update_contact(self, id: int, contact: ContactCreate, user: User):
        """
        Updates an existing contact.

        Args:
            id (int): The contact's ID.
            contact (ContactCreate): The updated contact data.
            user (User): The authenticated user.

        Returns:
            Contact | None: The updated contact if successful, otherwise None.

        Raises:
            HTTPException: If a contact with the same name already exists.
        """
        try:
            return await self.repository.update_contact(id, contact, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def delete_contact(self, id: int, user: User):
        """
        Deletes a contact by its ID.

        Args:
            id (int): The contact's ID.
            user (User): The authenticated user.

        Returns:
            Contact | None: The deleted contact if found, otherwise None.
        """
        return await self.repository.delete_contact(id, user)

    async def get_upcoming_birthdays(self, user: User):
        """
        Retrieves contacts with upcoming birthdays within the next 7 days.

        Args:
            user (User): The authenticated user.

        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        return await self.repository.get_upcoming_birthdays(user)
