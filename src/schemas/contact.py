from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date


class ContactBase(BaseModel):
    """
    Base schema for contact data.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (EmailStr): The email address of the contact.
        phone (str): The phone number of the contact.
        birthday (datetime): The birthday of the contact.
        additional_info (Optional[str]): Additional details about the contact.
    """

    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: datetime
    additional_info: Optional[str] = None

    @field_validator("first_name", "last_name")
    def validate_name(cls, value: str):
        """
        Validates that first and last names contain only alphabetic characters.

        Args:
            value (str): The name to validate.

        Returns:
            str: The validated name.

        Raises:
            ValueError: If the name contains non-alphabetic characters.
        """
        if not value.isalpha():
            raise ValueError("Name fields must contain only alphabetic characters.")
        return value

    @field_validator("phone")
    def validate_phone(cls, value: str):
        """
        Validates the phone number format.

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.

        Raises:
            ValueError: If the phone number is not 10 or 11 digits long.
        """
        if not value.isdigit() or len(value) not in (10, 11):
            raise ValueError("Phone number must contain 10 or 11 digits.")
        return value

    @field_validator("birthday")
    def validate_birthday(cls, value: datetime):
        """
        Validates that the birthday is a past date.

        Args:
            value (datetime): The birthday date.

        Returns:
            datetime: The validated birthday.

        Raises:
            ValueError: If the birthday is in the future.
        """
        if value.date() >= date.today():
            raise ValueError("Birthday must be a date in the past.")
        return value


class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.

    Inherits from:
        ContactBase
    """

    pass


class ContactResponse(ContactBase):
    """
    Schema for returning contact data in responses.

    Attributes:
        id (int): The unique identifier of the contact.

    Config:
        orm_mode (bool): Enables compatibility with ORM src.models.
    """

    id: int

    class Config:
        orm_mode = True
