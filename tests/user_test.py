import httpx
import pytest
from fastapi import status

# -- CREATE TEST -- #

@pytest.mark.asyncio
async def test_create_user(async_client: httpx.AsyncClient):
    create_url = "/api/user"
    user_data = {
        "username": "testuser2",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_user_conflict(async_client: httpx.AsyncClient):
    create_url = "/api/user"
    user_data = {
        "username": "testuser2",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    user_data = {
        "username": "testuser2",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_user_invalid(async_client: httpx.AsyncClient):
    create_url = "/api/user"
    user_data = {
        "username": "testuser2",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# -- UPDATE TEST -- #


@pytest.mark.asyncio
async def test_update_user(async_client: httpx.AsyncClient, admin_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser2",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {admin_user}"}
    update_url = "/api/user/2"

    user_data = {
        "username": "testuser3",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_user_not_found(async_client: httpx.AsyncClient, admin_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser2",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {admin_user}"}
    update_url = "/api/user/3"

    user_data = {
        "username": "testuser3",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_change_user_role(async_client: httpx.AsyncClient, admin_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser2",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {admin_user}"}
    update_url = "/api/user/role/2"

    user_data = {
        "role": "admin"
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_change_user_role_not_found(async_client: httpx.AsyncClient, admin_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser2",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {admin_user}"}
    update_url = "/api/user/role/3"

    user_data = {
        "role": "admin"
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_change_user_role_forbidden(async_client: httpx.AsyncClient, authenticated_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser3",
        "email": "test3@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {authenticated_user}"}
    update_url = "/api/user/role/3"

    user_data = {
        "role": "admin"
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_change_user_active(async_client: httpx.AsyncClient, admin_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser3",
        "email": "test3@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {admin_user}"}
    update_url = "/api/user/active/2"

    user_data = {
        "is_active": False
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_change_user_active_not_found(async_client: httpx.AsyncClient, admin_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser3",
        "email": "test3@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {admin_user}"}
    update_url = "/api/user/active/4"

    user_data = {
        "is_active": False
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_change_user_active_forbidden(async_client: httpx.AsyncClient, authenticated_user: str):
    create_url = "/api/user"
    user_data = {
        "username": "testuser3",
        "email": "test3@user.com",
        "password": "password"
    }

    response = await async_client.post(create_url, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    headers = {"Authorization": f"Bearer {authenticated_user}"}
    update_url = "/api/user/active/4"

    user_data = {
        "is_active": False
    }

    response = await async_client.patch(update_url, json=user_data, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


# -- GET TEST -- #


@pytest.mark.asyncio
async def test_get_users(async_client: httpx.AsyncClient, admin_user: str):
    url = "/api/user"
    headers = {"Authorization": f"Bearer {admin_user}"}

    response = await async_client.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_users_forbidden(async_client: httpx.AsyncClient, authenticated_user: str):
    url = "/api/user"
    headers = {"Authorization": f"Bearer {authenticated_user}"}

    response = await async_client.get(url, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_user_details(async_client: httpx.AsyncClient, admin_user: str):
    url = "/api/user/admin"
    headers = {"Authorization": f"Bearer {admin_user}"}

    response = await async_client.get(url, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_user_details_not_found(async_client: httpx.AsyncClient, admin_user: str):
    url = "/api/user/1"
    headers = {"Authorization": f"Bearer {admin_user}"}

    response = await async_client.get(url, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
