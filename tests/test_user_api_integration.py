import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, get_existing_token):
    response = client.get(
        "api/users/me", headers={"Authorization": f"Bearer {get_existing_token}"}
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    assert "username" in data
    assert "email" in data


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(client: AsyncClient):
    response = client.get("api/users/me")
    assert response.status_code == 401, response.json()
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio(loop_scope="function")
async def test_update_avatar_admin(client: AsyncClient, get_admin_token):
    fake_image = BytesIO(b"fake image data")
    fake_image.name = "fake_avatar.jpg"

    with patch(
        "src.services.upload_file.UploadFileService",
        new=AsyncMock(),
    ):
        files = {"file": ("fake_avatar.jpg", fake_image, "image/jpeg")}
        response = client.patch(
            "api/users/avatar",
            headers={"Authorization": f"Bearer {get_admin_token}"},
            files=files,
        )

    assert response.status_code == 200, response.json()
    data = response.json()
    assert "avatar" in data


@pytest.mark.asyncio
async def test_update_avatar_non_admin(client: AsyncClient, get_existing_token):
    fake_image = BytesIO(b"fake image data")
    fake_image.name = "fake_avatar.jpg"

    with patch(
        "src.services.upload_file.UploadFileService",
        new=AsyncMock(),
    ):
        files = {"file": ("fake_avatar.jpg", fake_image, "image/jpeg")}
        response = client.patch(
            "api/users/avatar",
            headers={"Authorization": f"Bearer {get_existing_token}"},
            files=files,
        )

    assert response.status_code == 403, response.json()
    assert response.json()["detail"] == "Недостатньо прав доступу"
