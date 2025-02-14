from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import app_config
from src.dependencies.db import get_db
from src.schemas.user import UserBase
from src.models.users import User
from src.services.auth import get_current_user, get_current_admin_user
from src.services.users import UserService
from src.services.upload_file import UploadFileService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=UserBase, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user.

    - Limited to 10 requests per minute.
    """
    return user


@router.patch("/avatar", response_model=UserBase)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of an authenticated admin user.

    - The uploaded file is stored and its URL is updated in the user's profile.
    """
    avatar_url = UploadFileService(
        app_config.CLD_NAME, app_config.CLD_API_KEY, app_config.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
