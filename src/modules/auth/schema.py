from datetime import datetime

from pydantic import BaseModel


class LoginSchema(BaseModel):
    id: int
    username: str
    role: str
    access_token: str
    refresh_token: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: int = None
    exp: int = None


class UserAuth(BaseModel):
    username: str
    password: str


class RefreshTokenBody(BaseModel):
    refresh_token: str


class UserIsMaster(BaseModel):
    id: int
    is_master: bool


class RefreshTokenCreate(BaseModel):
    user_id: int
    refresh_token: str
    expires_at: datetime
    used: bool = False