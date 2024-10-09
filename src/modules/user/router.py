# pylint: disable=W0613

from typing import List

from fastapi import APIRouter, status

from src.core.deps import AdminDep, SessionDep, UserDep
from src.modules.user import controller, schema

router = APIRouter(tags=["User"])


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=None
)
async def create_user(session: SessionDep, user_in: schema.UserCreate) -> schema.UserOut:
    """
    **Create a new User**

    Accepts User information and creates a new User record in the database.
    """
    return await controller.create_user(session, user_in)


@router.patch(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def update_user(session: SessionDep, user: UserDep, user_id: int, user_in: schema.UserUpdate) -> schema.UserOut:
    """
    **Update an existing User**

    _Requires LOGGED IN user or ADMINISTRATOR role_

    Accepts updated User information and updates the corresponding User 
    record in the database.
    """
    return await controller.update_user(session, user, user_id, user_in)


@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.UserOut]
)
async def get_users(session: SessionDep, user: AdminDep) -> List[schema.UserOut]:
    """
    **Retrieve a list of all Users**

    _Requires ADMINISTRATOR role_

    Queries the database and returns a list of Users.
    """
    return await controller.get_users(session)


@router.get(
    '/{username}',
    status_code=status.HTTP_200_OK,
    response_model=schema.UserOut
)
async def get_user_details(session: SessionDep, username: str) -> schema.UserOut:
    """
    **Get detailed information about a specific User**

    Fetches and return detailed information about a specific User identified by their username.
    """
    return await controller.get_user_details(session, username)


@router.patch(
    '/role/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def change_user_role(session: SessionDep, user: AdminDep, user_id: int, role: schema.UserChangeRole) -> None:
    """
    **Change the role of a specific User**

    _Requires ADMINISTRATOR role_

    Accepts updated User role information and updates the correspoding User record in the database.
    """
    return await controller.change_user_role(session, user_id, role)


@router.patch(
    '/active/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def change_user_active(session: SessionDep, user: AdminDep, user_id: int, active: schema.UserChangeActive) -> None:
    """
    **Change the active status of a specific User**

    _Requires ADMINISTRATOR role_

    Accepts updated User active status information and updates the corresponding User record in the database.
    """
    return await controller.change_user_active(session, user_id, active)
