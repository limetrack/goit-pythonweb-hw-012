from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from src.database.db import Base


class Contact(Base):
    """
    Represents a contact entity in the src.database.

    Attributes:
        id (int): Primary key for the contact.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email address of the contact.
        phone (str): Phone number of the contact.
        birthday (date): Birthday of the contact.
        additional_info (str, optional): Additional information about the contact.
        user_id (int, optional): Foreign key referencing the associated user.
        user (User): Relationship with the User model.
    """

    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("email", "user_id", name="unique_contact_user"),)

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    additional_info = Column(String, nullable=True)

    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", back_populates="contacts")
