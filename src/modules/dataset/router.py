# pylint: disable=W0613

from typing import List

from fastapi import APIRouter, status

from src.core.deps import SessionDep
from src.modules.dataset import controller, schema

router = APIRouter(tags=["Dataset"])


# -- POST ENDPOINTS -- #


# @router.post(
#     '',
#     status_code=status.HTTP_201_CREATED,
#     response_model=None
# )
# async def create_dataset(session: SessionDep, user: ModeDep, dataset_in: schema.DatasetCreate) -> None:
#     """
#     **Create a new Dataset**

#     _Requires MODERATOR role_

#     Accepts Dataset information and creates a new Dataset record in the database.
#     """
#     return await controller.create_dataset(session, dataset_in)


# -- GET ENDPOINTS -- #


@router.get(
    '/detail/{dataset_accessor}',
    status_code=status.HTTP_200_OK,
    response_model=schema.DatasetOut
)
async def get_dataset_details(session: SessionDep, dataset_accessor: str) -> schema.DatasetOut:
    """
    **Get detailed information about a specific Dataset**

    Fetches and returns detailed information about a specific Dataset identified by its title.
    """
    return await controller.get_dataset_details(session, dataset_accessor)


@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.DatasetInfoListOut]
)
async def get_all_datasets(session: SessionDep) -> List[schema.DatasetInfoListOut]:
    """
    **Retrieve a list of all datasets**

    Queries the database and returns a list of all Datasets.
    """
    return await controller.get_all_datasets(session)


@router.get(
    '/number-of-submissions',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.NumberSubmissionsOut]
)
async def get_number_of_submissions(session: SessionDep) -> List[schema.NumberSubmissionsOut]:
    """
    **Retrieve the number of submissions for each dataset**

    Queries the database and returns a list of all Datasets with the number of submissions.
    """
    return await controller.get_number_of_submissions(session)


@router.get(
    '/{dataset_id}/best-submission',
    status_code=status.HTTP_200_OK,
    response_model=schema.BestSubmissionOut
)
async def get_dataset_best_submission(session: SessionDep, dataset_id: int) -> schema.BestSubmissionOut:
    """
    **Retrieve the best submission for a dataset**

    Queries the database and returns the best submission for a dataset.
    """
    return await controller.get_best_dataset_submission(session, dataset_id)


@router.get(
    '/{dataset_id}/submissions-metrics',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.SubmissionMetricsOut]
)
async def get_dataset_submissions_metrics(session: SessionDep, dataset_id: int) -> List[schema.SubmissionMetricsOut]:
    """
    **Retrieve the metrics for all submissions for a dataset**

    Queries the database and returns the metrics for all submissions for a dataset.
    """
    return await controller.get_dataset_submissions_metrics(session, dataset_id)


@router.get(
    '/{dataset_id}/submissions-leaderboard',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.SubmissionLeaderboardOut]
)
async def get_dataset_submissions_leaderboard(session: SessionDep, dataset_id: int) -> List[schema.SubmissionLeaderboardOut]:
    """
    **Retrieve the leaderboard for all submissions for a dataset**

    Queries the database and returns the leaderboard for all submissions for a dataset.
    """
    return await controller.get_dataset_submissions_leaderboard(session, dataset_id)

# -- PATCH ENDPOINTS -- #


# @router.patch(
#     '/{dataset_id}',
#     status_code=status.HTTP_200_OK,
#     responses={
#         status.HTTP_200_OK: {"description": "Dataset updated successfully"},
#         status.HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
#         status.HTTP_409_CONFLICT: {"description": "Dataset already exists"},
#         status.HTTP_500_INTERNAL_SERVER_ERROR: {
#             "description": "Internal server error"}
#     },
#     response_model=schema.DatasetOptOut
# )
# async def update_dataset(session: SessionDep, user: ModeDep, dataset_id: int, dataset_in: schema.DatasetUpdate) -> schema.DatasetOptOut:
#     """
#     **Update an existing dataset**

#     _Requires MODERATOR role_

#     Accepts updated Dataset information and updates the corresponding Dataset
#     record in the database.
#     """
#     return await controller.update_dataset(session, dataset_id, dataset_in)


# -- DELETE ENDPOINTS -- #


# @router.delete(
#     '/{dataset_id}',
#     status_code=status.HTTP_200_OK,
#     responses={
#         status.HTTP_200_OK: {"description": "Dataset deleted successfully"},
#         status.HTTP_404_NOT_FOUND: {"description": "Dataset not found"},
#         status.HTTP_500_INTERNAL_SERVER_ERROR: {
#             "description": "Internal server error"}
#     },
#     response_model=None
# )
# async def delete_dataset(session: SessionDep, user: ModeDep, dataset_id: int) -> None:
#     """
#     **Delete a specific Dataset**

#     _Requires MODERATOR role_

#     Accepts a Dataset identification and deletes the corresponding Dataset record from the database.
#     """
#     return await controller.delete_dataset(session, dataset_id)


# @router.post(
#     '/{dataset_id}',
#     status_code=status.HTTP_201_CREATED,
#     responses={
#         status.HTTP_201_CREATED: {"description": "Scores Created Successfully"},
#         status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"},
#         status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"}
#     },
#     response_model=schema.DatasetScoresOut
# )
# async def create_scores(session: SessionDep, dataset_id: int, dataset_scores: schema.DatasetCreate) -> schema.DatasetOut:
#     """
#     **Create dataset scores for model**

#     Accepts model identification and scores information and creates the
#     corresponding dataset related record in the database.
#     """
#     return await controller.create_scores_controller(session, dataset_id, dataset_scores)
