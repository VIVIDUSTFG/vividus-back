from pydantic import BaseModel

from src.modules.scores.model import ScoreStatus

# -- POST SCHEMAS -- #


class ScoreCreate(BaseModel):
    dataset_id: int
    submission_id: int


# -- GET SCHEMAS -- #

class ScoreOut(BaseModel):
    id: int
    dataset_id: int
    submission_id: int
    status: str
    status_message: str | None
    precision: float | None
    accuracy: float | None
    recall: float | None
    f1: float | None
    aoc_roc: float | None
    aoc_pr: float | None


class GroupedSubmissionScoresOut(BaseModel):
    submission_id: int
    precision: float
    accuracy: float
    recall: float
    f1: float
    aoc_roc: float
    aoc_pr: float


class BestSubmissionsListOut(BaseModel):
    id: int
    title: str
    accessor: str
    resource_title: str
    resource_url: str
    weighted_mean: float


class BestSubmissionOut(BaseModel):
    submission_id: int
    submission_title: str
    submission_accessor: str


class SubmissionScoresOut(BaseModel):
    precision: float
    accuracy: float
    recall: float
    f1: float
    aoc_roc: float
    aoc_pr: float


# -- PATCH SCHEMAS -- #


class ScoreUpdate(BaseModel):
    status: ScoreStatus | None
    status_message: str | None
    precision: float | None = None
    accuracy: float | None = None
    recall: float | None = None
    f1: float | None = None
    aoc_roc: float | None = None
    aoc_pr: float | None = None
