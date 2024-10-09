from datetime import datetime, timedelta, timezone
from typing import Any, Union

import bcrypt
from jose import jwt

from src.core.config import settings


def create_access_token(
    subject: Union[str, Any],
    expires_delta: int = None,
) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(
            timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expires_delta = datetime.now(
            timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode = {"exp": expires_delta, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        settings.ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: int = None,
) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(
            timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expires_delta = datetime.now(
            timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    to_encode = {"exp": expires_delta, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET_KEY,
        settings.ALGORITHM,
    )
    return encoded_jwt


def get_hashed_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_byte_enc, hashed_password_byte_enc)
