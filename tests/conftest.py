import asyncio
import os

import httpx
import pytest_asyncio
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database.base_crud import Base
from src.core.deps import get_db
from src.modules.user.model import User
from src.server import app

env_path = find_dotenv(filename='.env.test')
load_dotenv(env_path)
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')


@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncEngine:
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def connection(engine: AsyncEngine):
    async with engine.connect() as conn:
        trans = await conn.begin()
        yield conn
        await trans.rollback()


@pytest_asyncio.fixture(scope="function")
async def session(connection):
    AsyncSessionLocal = sessionmaker(
        bind=connection, class_=AsyncSession, expire_on_commit=False
    )
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def override_get_db(session):
    async def _override_get_db():
        yield session
    return _override_get_db


@pytest_asyncio.fixture(scope="function")
async def async_client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    async with httpx.AsyncClient(app=app, base_url="http://localhost:8080") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope='function')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def authenticated_user(async_client):
    user_data = {
        "username": "testuser",
        "email": "test@user.com",
        "password": "password"
    }

    response = await async_client.post("/api/user", json=user_data)
    assert response.status_code == 201

    login = await async_client.post("/api/auth/login", data={
        "username": user_data['username'],
        "password": user_data['password']
    })
    assert login.status_code == 200

    token = login.json()['access_token']
    return token


@pytest_asyncio.fixture(scope="function")
async def admin_user(async_client, session):
    user_data = {
        "username": "admin",
        "email": "admin@user.com",
        "password": "password",
    }

    response = await async_client.post("/api/user", json=user_data)
    assert response.status_code == 201

    stmt = select(User).where(User.username == user_data['username'])
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    assert user is not None

    user.role = "admin"
    await session.commit()

    login = await async_client.post("/api/auth/login", data={
        "username": user_data['username'],
        "password": user_data['password']
    })
    assert login.status_code == 200

    token = login.json()['access_token']
    return token
