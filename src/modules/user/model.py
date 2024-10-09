from enum import StrEnum, auto
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from src.core.database.base_crud import Base

if TYPE_CHECKING:
    from src.modules.submission.model import Submission


class Role(StrEnum):
    ADMIN = auto()
    USER = auto()


class User(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: Role = Field(default=Role.USER)
    username: str = Field(unique=True, nullable=False)
    password: str
    email: EmailStr = Field(unique=True, nullable=False)
    is_active: bool = True

    submissions: List["Submission"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
