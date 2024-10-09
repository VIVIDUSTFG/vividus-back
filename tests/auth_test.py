import httpx
import pytest
from fastapi import status


# -- LOGIN TESTS -- #


@pytest.mark.asyncio
async def test_login(async_client: httpx.AsyncClient):
    user_data = {
        "username": "testuser2",
        "email": "test2@user.com",
        "password": "password"
    }

    response = await async_client.post("/api/user", json=user_data)
    assert response.status_code == 201

    login = await async_client.post("/api/auth/login", data={
        "username": user_data['username'],
        "password": user_data['password']
    })
    assert login.status_code == 200
    assert 'access_token' in login.json()
    assert 'refresh_token' in login.json()
    assert login.json()['username'] == user_data['username']
    assert login.json()['role'] == 'user'


@pytest.mark.asyncio
async def test_login_bad_request(async_client: httpx.AsyncClient):
    user_data = {
        "username": "testuser2",
        "email": "test2@user.com",
        "password": "password"
    }

    response = await async_client.post("/api/user", json=user_data)
    assert response.status_code == 201

    login = await async_client.post("/api/auth/login", data={
        "username": "testuser3",
        "password": user_data['password']
    })
    assert login.status_code == 400


# -- REFRESH TOKEN TESTS -- #


@pytest.mark.asyncio
async def test_refresh_token(async_client: httpx.AsyncClient):
    user_data = {
        "username": "testuser2",
        "email": "test2@user.com",
        "password": "password"
    }

    response = await async_client.post("/api/user", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    login = await async_client.post("/api/auth/login", data={
        "username": user_data['username'],
        "password": user_data['password']
    })
    assert login.status_code == status.HTTP_200_OK
    assert 'access_token' in login.json()
    assert 'refresh_token' in login.json()
    assert login.json()['username'] == user_data['username']
    assert login.json()['role'] == 'user'

    refresh = await async_client.post("/api/auth/refresh", json=login.json()['refresh_token'])
    assert refresh.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_refresh_token_invalid(async_client: httpx.AsyncClient):
    user_data = {
        "username": "testuser2",
        "email": "test2@user.com",
        "password": "password"
    }

    response = await async_client.post("/api/user", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    login = await async_client.post("/api/auth/login", data={
        "username": user_data['username'],
        "password": user_data['password']
    })
    assert login.status_code == status.HTTP_200_OK
    assert 'access_token' in login.json()
    assert 'refresh_token' in login.json()
    assert login.json()['username'] == user_data['username']
    assert login.json()['role'] == 'user'

    refresh = await async_client.post("/api/auth/refresh", json="mock_token")
    assert refresh.status_code == status.HTTP_403_FORBIDDEN
