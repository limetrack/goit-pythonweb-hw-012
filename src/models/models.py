from src.database.db import Base, async_engine

from src.models.contacts import Contact
from src.models.users import User

Base.metadata.create_all(bind=async_engine)
