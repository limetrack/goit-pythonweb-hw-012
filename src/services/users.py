from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repositories.users import UserRepository
from src.schemas.user import UserCreate


class UserService:
    """
    Service class for managing user-related operations.

    This class interacts with the `UserRepository` to handle business logic
    for user creation, retrieval, avatar updates, and password management.
    """

    def __init__(self, db: AsyncSession):
        """
        Initializes the UserService with a database session.

        Args:
            db (AsyncSession): The asynchronous database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user, generating a Gravatar avatar if available.

        Args:
            body (UserCreate): The user creation schema containing user details.

        Returns:
            User: The newly created user.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(f"Gravatar fetching error: {e}")

        return await self.repository.create_user(body, avatar)

    async def update_avatar_url(self, email: str, url: str):
        """
        Updates a user's avatar URL.

        Args:
            email (str): The user's email.
            url (str): The new avatar URL.

        Returns:
            User: The updated user with the new avatar.
        """
        return await self.repository.update_avatar_url(email, url)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieves a user by their email.

        Args:
            email (str): The email of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Marks a user's email as confirmed.

        Args:
            email (str): The email of the user.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_password(self, email: str, new_password: str):
        """
        Updates a user's password.

        Args:
            email (str): The user's email.
            new_password (str): The new hashed password.

        Returns:
            None
        """
        return await self.repository.update_password(email, new_password)
