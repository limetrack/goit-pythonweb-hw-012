from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

from src.models.users import UserRole


class UserBase(BaseModel):
    """
    Base schema for user data.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        avatar (Optional[str]): The avatar URL of the user. Defaults to None.
        confirmed (bool): Indicates if the user's email is confirmed. Defaults to False.
        role (UserRole): The role of the user (e.g., USER or ADMIN).
    """

    id: int
    username: str
    email: EmailStr
    avatar: Optional[str] = None
    confirmed: bool = False
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        username (str): The username for the new user.
        email (EmailStr): The email address of the new user.
        password (str): The password for the new user.
        role (UserRole): The role of the new user (e.g., USER or ADMIN).
    """

    username: str
    email: EmailStr
    password: str
    role: UserRole


class Token(BaseModel):
    """
    Schema for authentication tokens.

    Attributes:
        access_token (str): The JWT access token.
        refresh_token (str): The refresh token.
        token_type (str): The type of the token (usually "Bearer").
    """

    access_token: str
    refresh_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    """
    Schema for requesting a password reset.

    Attributes:
        email (EmailStr): The email address associated with the user account.
    """

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """
    Schema for confirming a password reset.

    Attributes:
        token (str): The reset token provided in the password reset request.
        new_password (str): The new password to be set for the user.
    """

    token: str
    new_password: str
