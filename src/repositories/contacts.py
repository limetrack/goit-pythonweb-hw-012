from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, extract

from typing import List
from datetime import datetime, timedelta

from src.models.users import User
from src.models.contacts import Contact
from src.schemas.contact import ContactCreate


class ContactsRepository:
    """
    Repository for managing contacts in the src.database.

    Provides methods to retrieve, create, update, and delete contacts,
    as well as fetching upcoming birthdays.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        Args:
            session (AsyncSession): The asynchronous database session.
        """
        self.db = session

    async def get_contacts(
        self,
        user: User,
        skip: int = 0,
        limit: int = 10,
        name: str = None,
        email: str = None,
    ) -> List[Contact]:
        """
        Retrieves a list of contacts belonging to a specific user.

        Args:
            user (User): The user whose contacts are being retrieved.
            skip (int, optional): Number of records to skip (pagination). Defaults to 0.
            limit (int, optional): Maximum number of contacts to retrieve. Defaults to 10.
            name (str, optional): Filter contacts by name (first or last name). Defaults to None.
            email (str, optional): Filter contacts by email. Defaults to None.

        Returns:
            List[Contact]: A list of contacts matching the criteria.
        """
        stmt = select(Contact).filter_by(user_id=user.id).offset(skip).limit(limit)
        if name:
            stmt = stmt.filter(
                or_(
                    Contact.first_name.ilike(f"%{name}%"),
                    Contact.last_name.ilike(f"%{name}%"),
                )
            )
        if email:
            stmt = stmt.filter(Contact.email.ilike(f"%{email}%"))
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, id: int, user: User) -> Contact | None:
        """
        Retrieves a single contact by its ID.

        Args:
            id (int): The contact's ID.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).filter_by(id=id, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user: User) -> Contact:
        """
        Creates a new contact for a given user.

        Args:
            body (ContactCreate): The data for creating the contact.
            user (User): The user who owns the contact.

        Returns:
            Contact: The newly created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, id: int, body: ContactCreate, user: User
    ) -> Contact | None:
        """
        Updates an existing contact.

        Args:
            id (int): The contact's ID.
            body (ContactCreate): The updated contact data.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The updated contact if successful, otherwise None.
        """
        contact = await self.get_contact_by_id(id, user)
        if not contact:
            return None
        for key, value in body.dict().items():
            setattr(contact, key, value)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete_contact(self, id: int, user: User) -> Contact | None:
        """
        Deletes a contact by ID.

        Args:
            id (int): The contact's ID.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The deleted contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Retrieves contacts whose birthdays fall within the next 7 days.

        Args:
            user (User): The user whose contacts are being checked.

        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        today = datetime.today().date()
        today_month = today.month
        today_day = today.day

        next_week = today + timedelta(days=7)
        next_week_month = next_week.month
        next_week_day = next_week.day

        stmt = (
            select(Contact)
            .filter_by(user_id=user.id)
            .filter(
                and_(
                    and_(
                        extract("month", Contact.birthday) == today_month,
                        extract("day", Contact.birthday) >= today_day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == next_week_month,
                        extract("day", Contact.birthday) <= next_week_day,
                    ),
                )
            )
        )

        result = await self.db.execute(stmt)

        return result.scalars().all()
