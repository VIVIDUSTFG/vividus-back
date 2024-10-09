from typing import List

from fastapi import HTTPException, status

from src.core.deps import SessionDep
from src.modules.dataset import schema, service
from src.modules.scores.controller import (get_all_scores, get_best_submission,
                                           get_best_submissions)
from src.modules.scores.model import ScoreStatus
from src.modules.submission.model import Submission, SubmissionStatus

# -- POST METHODS -- #


# async def create_dataset(session: SessionDep, dataset_in: schema.DatasetCreate) -> None:
#     title_check = await service.check_dataset(session, title=dataset_in.title)
#     if title_check:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail='Dataset already exists'
#         )
#     await service.create_dataset(session, dataset_in=dataset_in)


# -- GET METHODS -- #


async def get_dataset_details(session: SessionDep, dataset_accessor: str) -> schema.DatasetOut:
    dataset_record = await service.get_dataset_details(session, accessor=dataset_accessor)
    if not dataset_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Dataset not found'
        )
    return dataset_record


# TODO: Retrieve best model from submissions
async def get_all_datasets(session: SessionDep) -> List[schema.DatasetInfoListOut]:
    result = []
    datasets = await service.get_all_datasets(session)
    for dataset in datasets:
        item = dataset.model_dump()
        best_submission = await get_best_submission(session, dataset.id)
        if not best_submission:
            best_submission_title = None
            best_submission_accessor = None
        else:
            best_submission_title = best_submission.submission_title
            best_submission_accessor = best_submission.submission_accessor
        number_of_submissions = await service.count_dataset_submissions(session, dataset.id)
        result.append(schema.DatasetInfoListOut(**item, best_submission_title=best_submission_title,
                      best_submission_accessor=best_submission_accessor, number_of_submissions=number_of_submissions))
    return result


async def get_number_of_submissions(session: SessionDep) -> List[schema.NumberSubmissionsOut]:
    result = []
    datasets = await service.get_all_datasets(session)
    for dataset in datasets:
        number_of_submissions = await service.count_dataset_submissions(session, dataset_id=dataset.id)
        if number_of_submissions > 0:
            result.append(schema.NumberSubmissionsOut(
                dataset_title=dataset.title, number_of_submissions=number_of_submissions))
    return result


async def get_best_dataset_submission(session: SessionDep, dataset_id: int) -> schema.BestSubmissionOut:
    best_submission = await get_best_submission(session, dataset_id)
    return best_submission


async def get_dataset_submissions_metrics(session: SessionDep, dataset_id: int) -> List[schema.SubmissionMetricsOut]:
    result = []
    dataset_scores = await get_all_scores(session, dataset_id=dataset_id, submission_id=None, status=ScoreStatus.SUCCESS)
    for score in dataset_scores:
        score = score.model_dump()
        submission_title = await Submission.get_column_value(session, column="title", id=score['submission_id'], status=SubmissionStatus.PUBLISHED)
        if submission_title:
            result.append(schema.SubmissionMetricsOut(title=submission_title,
                                                      precision=score['precision'], recall=score['recall'], f1=score['f1'], aoc_roc=score['aoc_roc'], accuracy=score['accuracy'], aoc_pr=score['aoc_pr']))
    return result


async def get_dataset_submissions_leaderboard(session: SessionDep, dataset_id: int) -> List[schema.SubmissionLeaderboardOut]:
    leaderboard = await get_best_submissions(session, limit=None, dataset_id=dataset_id)
    return leaderboard


async def get_dataset_column(session: SessionDep, column: str, **kwargs):
    return await service.get_dataset_column(session, column, **kwargs)
# -- PATCH METHODS -- #


# async def update_dataset(session: SessionDep, dataset_id: int, dataset_in: schema.DatasetUpdate) -> None:
#     old_dataset = await service.get_dataset_details(session, id=dataset_id)
#     if not old_dataset:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='Dataset not found'
#         )
#     if dataset_in.title and dataset_in.title != old_dataset.title:
#         title_check = await service.check_dataset(session, title=dataset_in.title)
#         if title_check:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail='Dataset already exists'
#             )
#     await service.update_dataset(session, old_dataset, dataset_in)


# -- DELETE METHODS -- #


# async def delete_dataset(session: SessionDep, dataset_accessor: str) -> None:
#     dataset_check = await service.check_dataset(session, accessor=dataset_accessor)
#     if not dataset_check:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Dataset not found'
#         )
#     await service.delete_dataset(session, dataset_accessor=dataset_accessor)
