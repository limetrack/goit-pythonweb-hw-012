from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token, create_reset_token
from src.conf.config import app_config

# Configuration for FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=app_config.MAIL_USERNAME,
    MAIL_PASSWORD=app_config.MAIL_PASSWORD,
    MAIL_FROM=app_config.MAIL_FROM,
    MAIL_PORT=app_config.MAIL_PORT,
    MAIL_SERVER=app_config.MAIL_SERVER,
    MAIL_FROM_NAME=app_config.MAIL_FROM_NAME,
    MAIL_STARTTLS=app_config.MAIL_STARTTLS,
    MAIL_SSL_TLS=app_config.MAIL_SSL_TLS,
    USE_CREDENTIALS=app_config.USE_CREDENTIALS,
    VALIDATE_CERTS=app_config.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email confirmation message to a user.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The recipient's username.
        host (str): The base URL of the application.

    Raises:
        ConnectionErrors: If an error occurs while sending the email.
    """
    try:
        token_verification = create_email_token({"sub": email})

        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(f"Email sending failed: {err}")


async def send_reset_email(email: str, username: str, host: str):
    """
    Sends a password reset email to a user.

    Args:
        email (str): The recipient's email address.
        username (str): The recipient's username.
        host (str): The base URL of the application.

    Raises:
        ConnectionErrors: If an error occurs while sending the email.
    """
    try:
        reset_token = create_reset_token(email)

        message = MessageSchema(
            subject="Password Reset Request",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": reset_token,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="password_reset.html")
    except ConnectionErrors as err:
        print(f"Password reset email sending failed: {err}")
