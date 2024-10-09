from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from src.core.database.base_crud import Base

if TYPE_CHECKING:
    from src.modules.user.model import User


class RefreshToken(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    refresh_token: str
    expires_at: datetime
    used: bool = False
    user_id: int = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="refresh_tokens")

    @classmethod
    def is_valid(self):
        return self.expires_at > datetime.now(timezone.utc) and not self.used
