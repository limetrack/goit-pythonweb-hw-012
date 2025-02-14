from datetime import datetime, timedelta, UTC
from typing import Optional
import json
import uuid

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.dependencies.db import get_db
from src.dependencies.redis_cache import get_redis
from src.conf.config import app_config
from src.schemas.user import UserBase
from src.models.users import User, UserRole
from src.services.users import UserService


class Hash:
    """
    Utility class for password hashing and verification.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a password against its hashed version.

        Args:
            plain_password (str): The raw password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes a given password.

        Args:
            password (str): The raw password.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Creates an access token.

    Args:
        data (dict): The payload data to encode.
        expires_delta (Optional[int]): The expiration time in seconds.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(
            seconds=app_config.JWT_EXPIRATION_SECONDS
        )

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode, app_config.JWT_SECRET, algorithm=app_config.JWT_ALGORITHM
    )


def create_refresh_token(data: dict) -> str:
    """
    Creates a refresh token.

    Args:
        data (dict): The payload data to encode.

    Returns:
        str: The encoded JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=app_config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid.uuid4())})
    return jwt.encode(
        to_encode, app_config.JWT_SECRET, algorithm=app_config.JWT_ALGORITHM
    )


def verify_token(token: str, expected_type: str) -> Optional[dict]:
    """
    Verifies and decodes a JWT token.

    Args:
        token (str): The JWT token.
        expected_type (str): The expected type of token ("access" or "refresh").

    Returns:
        Optional[dict]: The decoded token payload if valid, else None.
    """
    payload = jwt.decode(
        token, app_config.JWT_SECRET, algorithms=[app_config.JWT_ALGORITHM]
    )
    if payload.get("type") != expected_type:
        return None
    return payload


def create_reset_token(email: str) -> str:
    """
    Creates a password reset token.

    Args:
        email (str): The user's email.

    Returns:
        str: The encoded JWT reset token.
    """
    expire = datetime.now(UTC) + timedelta(seconds=app_config.RESET_TOKEN_EXPIRY)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(
        to_encode, app_config.JWT_SECRET, algorithm=app_config.JWT_ALGORITHM
    )


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verifies a password reset token.

    Args:
        token (str): The JWT reset token.

    Returns:
        Optional[str]: The email if the token is valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token, app_config.JWT_SECRET, algorithms=[app_config.JWT_ALGORITHM]
        )
        return payload["sub"]
    except JWTError:
        return None


def create_email_token(data: dict) -> str:
    """
    Creates a token for email verification.

    Args:
        data (dict): The payload data.

    Returns:
        str: The encoded email verification token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    return jwt.encode(
        to_encode, app_config.JWT_SECRET, algorithm=app_config.JWT_ALGORITHM
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> User:
    """
    Retrieves the currently authenticated user.

    Uses Redis caching for performance optimization.

    Args:
        token (str): The JWT access token.
        db (AsyncSession): The database session.
        redis: The Redis client instance.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    try:
        payload = verify_token(token, "access")
        if payload is None:
            raise credentials_exception

        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Check Redis cache
    cached_user = await redis.get(f"user:{token}")
    if cached_user:
        user_data = json.loads(cached_user)
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            avatar=user_data.get("avatar"),
            confirmed=user_data["confirmed"],
            role=user_data["role"]
        )
        print("-------- user from cache --------")
        return user

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception

    user_schema = UserBase.model_validate(user)
    await redis.set(f"user:{token}", user_schema.model_dump_json())
    await redis.expire(f"user:{token}", 600)

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures the currently authenticated user is an admin.

    Args:
        current_user (User): The authenticated user.

    Returns:
        User: The authenticated admin user.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостатньо прав доступу")
    return current_user


def get_email_from_token(token: str) -> str:
    """
    Extracts an email from a verification token.

    Args:
        token (str): The email verification JWT token.

    Returns:
        str: The extracted email.

    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, app_config.JWT_SECRET, algorithms=[app_config.JWT_ALGORITHM]
        )
        return payload["sub"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )
