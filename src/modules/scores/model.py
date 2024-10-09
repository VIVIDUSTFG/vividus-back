from enum import StrEnum, auto
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, UniqueConstraint

from src.core.database.base_crud import Base


class ScoreStatus(StrEnum):
    IN_PROGRESS = auto()
    ERROR = auto()
    SUCCESS = auto()


class Score(Base, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dataset_id: int = Field(
        default=None, foreign_key="dataset.id", index=True, ondelete="CASCADE")
    submission_id: int = Field(
        default=None, foreign_key="submission.id", index=True, ondelete="CASCADE")

    status: ScoreStatus = Field(default=ScoreStatus.IN_PROGRESS)
    status_message: str | None = Field(default=None)
    precision: float | None = Field(default=None)
    accuracy: float | None = Field(default=None)
    recall: float | None = Field(default=None)
    f1: float | None = Field(default=None)
    aoc_roc: float | None = Field(default=None)
    aoc_pr: float | None = Field(default=None)

    __table_args__ = (UniqueConstraint(
        "dataset_id", "submission_id", name="uq_dataset_submission"),)
