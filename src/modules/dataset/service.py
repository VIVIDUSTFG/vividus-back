from src.core.deps import SessionDep
from src.modules.dataset import model, schema
from src.modules.scores.model import Score, ScoreStatus
from src.modules.submission.model import Submission, SubmissionStatus

# -- UTILS SERVICES -- #


async def check_dataset(session: SessionDep, **kwargs) -> bool:
    return await model.Dataset.exists(session, **kwargs)


async def get_dataset_column(session: SessionDep, column: str, **kwargs):
    return await model.Dataset.get_column_value(session, column, **kwargs)


async def count_dataset_submissions(session: SessionDep, dataset_id: int) -> int:
    count = 0
    score_records = await Score.get_multi(
        session, dataset_id=dataset_id, status=ScoreStatus.SUCCESS)
    for score in score_records:
        submission = await Submission.exists(
            session, id=score.submission_id, status=SubmissionStatus.PUBLISHED)
        if submission:
            count += 1
    return count

# -- CREATE SERVICES -- #


# async def create_dataset(session: SessionDep, dataset_in: schema.DatasetCreate) -> model.Dataset | None:
#     return await model.Dataset.create(session, **dataset_in.model_dump())


# -- READ SERVICES -- #


async def get_dataset_details(session: SessionDep, **kwargs) -> model.Dataset | None:
    return await model.Dataset.get(session, **kwargs)


async def get_all_datasets(session: SessionDep) -> list[schema.DatasetOut]:
    result = await model.Dataset.get_multi(session)
    return result


# -- UPDATE SERVICES -- #


# async def update_dataset(session: SessionDep, old_dataset: model.Dataset, dataset_in: schema.DatasetUpdate) -> model.Dataset:
#     return await old_dataset.update(session, **dataset_in.model_dump(exclude_unset=True))


# -- DELETE SERVICES -- #


# async def delete_dataset(session: SessionDep, dataset_id: int) -> None:
#     await model.Dataset.delete(session, id=dataset_id)
