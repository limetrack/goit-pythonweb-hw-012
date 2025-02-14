import pytest
from unittest.mock import Mock
from sqlalchemy import select

from src.models.users import User
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "testsecond",
    "email": "testsecond@gmail.com",
    "password": "1234567890",
    "role": "USER",
}


@pytest.mark.asyncio
async def test_register_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = client.post("api/auth/register", json=user_data)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "testsecond@gmail.com"
    assert data["username"] == "testsecond"
    assert "hashed_password" not in data
    assert "avatar" in data


@pytest.mark.asyncio
async def test_register_existing_user(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = client.post(
        "api/auth/register",
        json=user_data,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Користувач з таким email вже існує"


@pytest.mark.asyncio
async def test_login_user(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        data={
            "username": user_data.get("username"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_login_invalid_user(client):
    response = client.post(
        "api/auth/login", data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неправильний логін або пароль"


@pytest.mark.asyncio
async def test_confirm_email(client, get_token):
    response = client.get(f"api/auth/confirmed_email/{get_token}")
    assert response.status_code in [200, 400]
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_request_email_verification(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    
    response = client.post("api/auth/request_email", json={"email": "testsecond@gmail.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "Ваша електронна пошта вже підтверджена"


@pytest.mark.asyncio
async def test_request_email_for_non_existing_user(client):
    response = client.post(
        "api/auth/request_email", json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_forgot_password(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    
    response = client.post(
        "api/auth/forgot_password", json={"email": "testsecond@gmail.com"}
    )
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Password reset email sent. Please check your inbox."
    )


@pytest.mark.asyncio
async def test_forgot_password_for_non_existing_user(client):
    response = client.post(
        "api/auth/forgot_password", json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_reset_password(client, get_reset_token):
    response = client.post(
        "api/auth/reset_password",
        json={"token": get_reset_token, "new_password": "newpassword"},
    )
    assert response.status_code == 200, response.json()
    assert response.json()["message"] == "Password successfully reset"


@pytest.mark.asyncio
async def test_refresh_token(client, get_refresh_token):
    response = client.post(f"/api/auth/refresh?refresh_token={get_refresh_token}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
