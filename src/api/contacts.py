from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.models.users import User
from src.schemas.contact import ContactCreate, ContactResponse
from src.services.contacts import ContactsService
from src.services.auth import get_current_user
from src.dependencies.db import get_db

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def get_contacts_route(
    skip: str = Query(0),
    limit: str = Query(10),
    name: str = Query(None),
    email: str = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts.

    - Allows filtering by name and email.
    - Supports pagination with `skip` and `limit` parameters.
    """
    service = ContactsService(db)
    contacts = await service.get_contacts(
        user=user, skip=skip, limit=limit, name=name, email=email
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_route(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a single contact by ID.

    - Returns a 404 error if the contact is not found.
    """
    service = ContactsService(db)
    contact = await service.get_contact_by_id(contact_id, user)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_route(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact.
    """
    service = ContactsService(db)
    created_contact = await service.create_contact(contact, user)
    return created_contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact_route(
    contact_id: int,
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing contact.

    - Returns a 404 error if the contact is not found.
    """
    service = ContactsService(db)
    updated_contact = await service.update_contact(contact_id, contact, user)
    if not updated_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return updated_contact


@router.delete("/{contact_id}", response_model=dict)
async def delete_contact_route(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a contact by ID.

    - Returns a 404 error if the contact is not found.
    """
    service = ContactsService(db)
    deleted_contact = await service.delete_contact(contact_id, user)
    if not deleted_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return {"detail": "Contact deleted successfully"}


@router.get("/upcoming_birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays_route(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Retrieve contacts with upcoming birthdays.
    """
    service = ContactsService(db)
    contacts = await service.get_upcoming_birthdays(user)
    return contacts
