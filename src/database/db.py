from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.conf.config import app_config


try:
    # Create an asynchronous database engine
    async_engine = create_async_engine(
        app_config.DATABASE_URL,
        echo=True,
    )

    # Create an asynchronous session factory
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Base class for declarative class definitions
    Base = declarative_base()
except OperationalError as e:
    print(f"Error connecting to the database: {e}")
