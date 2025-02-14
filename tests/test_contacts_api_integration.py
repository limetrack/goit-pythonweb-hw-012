import pytest
from httpx import AsyncClient

test_contact = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "1234567890",
    "birthday": "2000-01-01T00:00:00",
    "additional_info": "Friend from school",
}


@pytest.mark.asyncio
async def test_create_contact(client: AsyncClient, get_existing_token):
    response = client.post(
        "/contacts/",
        json=test_contact,
        headers={"Authorization": f"Bearer {get_existing_token}"},
    )

    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_contacts(client: AsyncClient, get_existing_token):
    response = client.get(
        "/contacts",
        params={"skip": 0, "limit": 10},
        headers={"Authorization": f"Bearer {get_existing_token}"},
    )

    assert response.status_code == 200, response.json()
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "first_name" in data[0]
        assert "last_name" in data[0]


@pytest.mark.asyncio
async def test_get_contact_by_id(client: AsyncClient, get_existing_token):
    response = client.get(
        "/contacts/1", headers={"Authorization": f"Bearer {get_existing_token}"}
    )

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_contact_not_found(client: AsyncClient, get_existing_token):
    response = client.get(
        "/contacts/999", headers={"Authorization": f"Bearer {get_existing_token}"}
    )

    assert response.status_code == 404, response.json()
    assert response.json()["detail"] == "Contact not found"


@pytest.mark.asyncio
async def test_update_contact(client: AsyncClient, get_existing_token):
    response = client.put(
        "/contacts/1",
        json={
            "first_name": "Updated",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "birthday": "2000-01-01T00:00:00",
            "additional_info": "Updated info",
        },
        headers={"Authorization": f"Bearer {get_existing_token}"},
    )

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["additional_info"] == "Updated info"


@pytest.mark.asyncio
async def test_update_contact_not_found(client: AsyncClient, get_existing_token):
    response = client.put(
        "/contacts/999",
        json={
            "first_name": "Updated",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "birthday": "2000-01-01T00:00:00",
            "additional_info": "Updated info",
        },
        headers={"Authorization": f"Bearer {get_existing_token}"},
    )

    assert response.status_code == 404, response.json()
    assert response.json()["detail"] == "Contact not found"


@pytest.mark.asyncio
async def test_delete_contact(client: AsyncClient, get_existing_token):
    response = client.delete(
        "/contacts/1", headers={"Authorization": f"Bearer {get_existing_token}"}
    )

    assert response.status_code == 200, response.json()
    assert response.json()["detail"] == "Contact deleted successfully"


@pytest.mark.asyncio
async def test_delete_contact_not_found(client: AsyncClient, get_existing_token):
    response = client.delete(
        "/contacts/999", headers={"Authorization": f"Bearer {get_existing_token}"}
    )

    assert response.status_code == 404, response.json()
    assert response.json()["detail"] == "Contact not found"
