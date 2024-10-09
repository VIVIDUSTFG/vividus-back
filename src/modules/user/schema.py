from typing import Optional

from pydantic import BaseModel, EmailStr

from src.modules.user.model import Role


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role
    is_active: bool


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None


class UserChangeRole(BaseModel):
    role: Role


class UserChangeActive(BaseModel):
    is_active: bool
