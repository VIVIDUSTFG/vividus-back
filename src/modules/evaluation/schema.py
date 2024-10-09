from pydantic import BaseModel


class EvaluationCreate(BaseModel):
    dataset_accessor: str
    submission_accessor: str
