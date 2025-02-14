from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.schemas.user import UserCreate


class UserRepository:
    """
    Repository for managing user operations in the src.database.

    Provides methods to retrieve, create, update user information,
    and confirm email addresses.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        Args:
            session (AsyncSession): The asynchronous database session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The user's ID.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieves a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieves a user by their email.

        Args:
            email (str): The email to search for.

        Returns:
            User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Creates a new user in the src.database.

        Args:
            body (UserCreate): The user data to be created.
            avatar (str, optional): The avatar URL for the user. Defaults to None.

        Returns:
            User: The newly created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Updates the user's avatar URL.

        Args:
            email (str): The email of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated user with the new avatar URL.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Marks the user's email as confirmed.

        Args:
            email (str): The email of the user to be confirmed.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_password(self, email: str, new_password: str) -> None:
        """
        Updates the user's password.

        Args:
            email (str): The email of the user whose password is being updated.
            new_password (str): The new hashed password.
        """
        user = await self.get_user_by_email(email)
        user.hashed_password = new_password
        await self.db.commit()
