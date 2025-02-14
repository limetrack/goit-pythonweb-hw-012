from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, Enum as SqlEnum, func
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship

from src.database.db import Base


class UserRole(str, Enum):
    """
    Enum representing user roles.

    Attributes:
        USER (str): Regular user role.
        ADMIN (str): Administrator role.
    """

    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    """
    Represents a user entity in the src.database.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password for authentication.
        created_at (datetime): Timestamp of user account creation.
        avatar (str, optional): URL or path to the user's avatar.
        confirmed (bool): Indicates if the user's email is confirmed.
        role (UserRole): Role of the user (default: USER).
        contacts (relationship): Relationship to the Contact model.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    contacts = relationship("Contact", back_populates="user", cascade="all, delete")
