# pylint: disable=W0613

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError

from src.core.config import settings
from src.core.deps import SessionDep, UserDep
from src.core.utils.security import create_access_token, create_refresh_token
from src.modules.auth import controller
from src.modules.auth.schema import LoginSchema, TokenPayload, TokenSchema
from src.modules.user.model import User
from src.modules.user.schema import UserOut

router = APIRouter(tags=["Auth"])


@router.post('/login', response_model=LoginSchema)
async def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()) -> LoginSchema:
    user = await controller.login_controller(session, form_data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {"id": user.id, "username": user.username, "role": user.role, "access_token": access_token, "refresh_token": refresh_token}


@router.post('/test-token', response_model=UserOut)
async def test_token(user: UserDep) -> UserOut:
    return user.model_dump()


@router.post('/refresh', summary="Refresh token", response_model=TokenSchema)
async def refresh_token_generator(session: SessionDep, refresh_token: str = Body(...)) -> TokenSchema:
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[
                settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user = await User.get(session, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token for user",
        )
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
    }
