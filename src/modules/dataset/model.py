from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship

from src.core.database.base_crud import Base
from src.modules.scores.model import Score

if TYPE_CHECKING:
    from src.modules.submission.model import Submission


class Dataset(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    accessor: str = Field(index=True)
    description: str

    submissions: List["Submission"] | None = Relationship(
        back_populates="datasets", link_model=Score)
