from pydantic import BaseModel

# -- POST SCHEMAS -- #


class DatasetCreate(BaseModel):
    title: str
    description: str


# -- GET SCHEMAS -- #


# class DatasetScoresOut(BaseModel):
#     submission_id: int
#     precision: float | None
#     # accuracy: float | None
#     recall: float | None
#     f1: float | None
#     aoc_roc: float | None
#     # aoc_pr: float | None


class DatasetOut(BaseModel):
    id: int
    title: str
    accessor: str
    description: str
    # submissions: List[DatasetScoresOut]


class DatasetInfoListOut(BaseModel):
    id: int
    title: str
    accessor: str
    description: str
    best_submission_title: str | None
    best_submission_accessor: str | None
    number_of_submissions: int


class NumberSubmissionsOut(BaseModel):
    dataset_title: str
    number_of_submissions: int


class BestSubmissionOut(BaseModel):
    submission_id: int
    submission_title: str
    submission_accessor: str


class SubmissionMetricsOut(BaseModel):
    title: str
    precision: float
    accuracy: float
    recall: float
    f1: float
    aoc_roc: float
    aoc_pr: float

# class DatasetOptOut(BaseModel):
#     id: int
#     title: str
#     accessor: str
#     description: str


class SubmissionLeaderboardOut(BaseModel):
    id: int
    title: str
    accessor: str
    precision: float
    accuracy: float
    recall: float
    f1: float
    aoc_roc: float
    aoc_pr: float
    resource_title: str
    resource_url: str
    repository_url: str
    weighted_mean: float


# -- PATCH SCHEMAS -- #


# class DatasetUpdate(BaseModel):
#     title: str | None = None
#     description: str | None = None
