from typing import List

from fastapi import HTTPException, status

from src.core.deps import SessionDep
from src.modules.user import model, schema, service


async def create_user(session: SessionDep, user_in: schema.UserCreate) -> schema.UserOut:
    username_check = await service.check_user(session, username=user_in.username)
    if username_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    email_check = await service.check_user(session, email=user_in.email)
    if email_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    user_out = await service.create_user(session, user_in)
    if not user_out:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error creating the user"
        )
    return schema.UserOut(**user_out.model_dump())


async def update_user(session: SessionDep, user: model.User, user_id: int, user_in: schema.UserUpdate) -> schema.UserOut:
    if user.id != user_id and user.role != model.Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized"
        )
    old_user = await service.get_user_details(session, id=user_id)
    if old_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )

    if user_in.username and user_in.username != old_user.username:
        username_check = await service.check_user(session, username=user_in.username)
        if username_check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
    if user_in.email and user_in.email != old_user.email:
        email_check = await service.check_user(session, email=user_in.email)
        if email_check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
    user = await service.update_user(session, old_user, user_in)
    return schema.UserOut(**user.model_dump())


async def get_users(session: SessionDep) -> List[schema.UserOut]:
    return await service.get_users(session)


async def get_user_details(session: SessionDep, username: str) -> schema.UserOut:
    user = await service.get_user_details(session, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user


async def change_user_role(session: SessionDep, user_id: int, role: schema.UserChangeRole) -> schema.UserOut:
    old_user = await service.get_user_details(session, id=user_id)
    if old_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )
    user = await service.update_user(session, old_user, role)
    return schema.UserOut(**user.model_dump())


async def change_user_active(session: SessionDep, user_id: int, active: schema.UserChangeActive) -> schema.UserOut:
    old_user = await service.get_user_details(session, id=user_id)
    if old_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )
    user = await service.update_user(session, old_user, active)
    return schema.UserOut(**user.model_dump())
