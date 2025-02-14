from src.database.db import AsyncSessionLocal


async def get_db():
    """
    Provides an asynchronous database session.

    This function is used as a dependency for database operations.
    It ensures that a new session is created and properly closed after use.

    Yields:
        AsyncSession: An instance of an asynchronous SQLAlchemy session.
    """
    async with AsyncSessionLocal() as session:
        yield session
