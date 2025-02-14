from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from src.schemas.user import (
    UserBase,
    UserCreate,
    Token,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from src.schemas.email import RequestEmail
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_email_from_token,
    verify_reset_token,
    Hash,
)
from src.services.users import UserService
from src.services.email import send_email, send_reset_email
from src.dependencies.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    - Checks if the email or username already exists.
    - Hashes the password before storing it.
    - Sends a confirmation email.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )

    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_email,
        new_user.email,
        new_user.username,
        str(request.base_url),
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access & refresh tokens.

    - Validates username and password.
    - Checks if the user's email is confirmed.
    - Generates and returns JWT tokens.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)

    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a user's email using a verification token.
    """
    email = get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email confirmation request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}

    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Перевірте свою електронну пошту для підтвердження"}


@router.post("/forgot_password")
async def forgot_password(
    request: Request,
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Send password reset email.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    background_tasks.add_task(
        send_reset_email, user.email, user.username, request.base_url
    )
    return {"message": "Password reset email sent. Please check your inbox."}


@router.post("/reset_password")
async def reset_password(
    body: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    """
    Reset a user's password using a token.
    """
    email = verify_reset_token(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = Hash().get_password_hash(body.new_password)
    await user_service.update_password(email, hashed_password)
    return {"message": "Password successfully reset"}


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh the access token using a valid refresh token.
    """
    try:
        payload = verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        new_access_token = create_access_token({"sub": payload["sub"]})
        new_refresh_token = create_refresh_token({"sub": payload["sub"]})
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
