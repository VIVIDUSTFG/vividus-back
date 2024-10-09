from typing import List, Optional

from pydantic import BaseModel

from src.modules.scores.model import ScoreStatus
from src.modules.submission.model import SubmissionModality, SubmissionStatus

# -- POST SCHEMAS -- #

class SubmissionCreate(BaseModel):
    title: str
    authors: str
    description: str
    repository_url: str
    resource_title: str
    resource_url: str
    modality: SubmissionModality


# -- GET SCHEMAS -- #

class SubmissionOptOut(BaseModel):
    id: int
    title: str
    accessor: str
    status: SubmissionStatus
    modality: SubmissionModality
    description: str
    user_id: int
    review_message: str | None


class SubmissionUserOut(BaseModel):
    id: int
    username: str


class SubmissionDatasetOut(BaseModel):
    id: int
    title: str
    accessor: str


class SubmissionScoreOut(BaseModel):
    title: str
    precision: float | None
    accuracy: float | None
    recall: float | None
    f1: float | None
    aoc_roc: float | None
    aoc_pr: float | None


class SubmissionOut(BaseModel):
    id: int
    title: str
    accessor: str
    authors: str
    status: SubmissionStatus
    description: str
    repository_url: str
    resource_title: str
    resource_url: str

    modality: SubmissionModality

    review_message: str | None

    user: SubmissionUserOut
    datasets: List[SubmissionDatasetOut]


class SubmissionInfoListOut(BaseModel):
    id: int
    title: str
    accessor: str
    authors: str
    status: SubmissionStatus
    modality: SubmissionModality
    description: str
    repository_url: str
    resource_title: str
    resource_url: str
    review_message: str | None

    user: SubmissionUserOut


# class SubmissionScoreListOut(SubmissionInfoListOut):
#     score: SubmissionScoreOut


class SubmissionRankOut(BaseModel):
    rank: int | None
    total: int | None


class SubmissionResultsOut(BaseModel):
    rank: int
    dataset_title: str
    dataset_accessor: str
    f1: float
    recall: float
    precision: float
    accuracy: float
    aoc_roc: float
    aoc_pr: float


class SubmissionTestRecordOut(BaseModel):
    dataset_id: int
    dataset_title: str
    dataset_accessor: str
    status: ScoreStatus | None
    status_message: str | None

# -- PATCH SCHEMAS -- #


class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    modality: Optional[SubmissionModality] = None
    description: Optional[str] = None
    repository_url: Optional[str] = None
    resource_title: Optional[str] = None
    resource_url: Optional[str] = None


class SubmissionChangeStatus(BaseModel):
    status: SubmissionStatus


class SubmissionReview(BaseModel):
    review_message: str | None
    status: SubmissionStatus
