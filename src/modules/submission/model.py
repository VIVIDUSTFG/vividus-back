from enum import StrEnum, auto
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from src.core.database.base_crud import Base
from src.modules.scores.model import Score

if TYPE_CHECKING:
    from src.modules.dataset.model import Dataset
    from src.modules.user.model import User


class SubmissionStatus(StrEnum):
    DRAFT = auto()
    IN_REVIEW = auto()
    REQUEST_FOR_CHANGES = auto()
    ACCEPTED = auto()
    REJECTED = auto()
    PUBLISHED = auto()


class SubmissionModality(StrEnum):
    RGB_ONLY = auto()
    RGB_AND_AUDIO = auto()


class Submission(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    accessor: str
    authors: str
    status: SubmissionStatus = Field(default=SubmissionStatus.DRAFT)
    description: str
    repository_url: str
    resource_title: str
    resource_url: str

    modality: SubmissionModality

    review_message: str | None = Field(default=None)

    user_id: int = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="submissions")

    datasets: List["Dataset"] | None = Relationship(
        back_populates="submissions", link_model=Score)
