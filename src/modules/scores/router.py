# pylint: disable=W0613

from typing import List

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from src.core.deps import SessionDep, UserDep
from src.modules.scores import controller, schema

router = APIRouter(tags=["Score"])


# -- POST ENDPOINTS -- #


# @router.post(
#     '',
#     status_code=status.HTTP_201_CREATED,
#     response_model=None
# )
# async def create_score(session: SessionDep, user: ModeDep, score_in: schema.ScoreCreate) -> None:
#     """
#     **Create a new Score**

#     _Requires MODERATOR role_

#     Accepts Score information and creates a new Score record in the database.
#     """
#     await controller.create_score(session, score_in)


# -- GET ENDPOINTS -- #


# @router.get(
#     '/{score_id}',
#     status_code=status.HTTP_200_OK,
#     response_model=schema.ScoreOut
# )
# async def get_score(session: SessionDep, user: ModeDep, score_id: int) -> schema.ScoreOut:
#     """
#     **Get a specific Score**

#     _Requires MODERATOR role_

#     Accepts a Score ID and returns the corresponding Score record from the database.
#     """
#     return await controller.get_score_details(session, score_id)


@router.get(
    '',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.ScoreOut]
)
async def get_all_scores(session: SessionDep, user: UserDep, dataset_id: int | None = None, model_id: int | None = None, status: int | None = None) -> List[schema.ScoreOut]:
    """
    **Get all Scores**

    _Requires MODERATOR role_

    Returns a list of all Score records in the database.
    """
    return await controller.get_all_scores(session, dataset_id, model_id, status)


@router.get(
    '/best-submissions',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.BestSubmissionsListOut]
)
async def get_best_submissions(session: SessionDep, limit: int = 5) -> List[schema.BestSubmissionsListOut]:
    """
    **Get the best submissions**

    _Requires MODERATOR role_

    Returns a list of the best submissions based on their scores.
    """
    return await controller.get_best_submissions(session, limit, dataset_id=None)


@router.get(
    '/events/{submission_id}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def get_submission_events(submission_id: int) -> StreamingResponse:
    """
    **Get Submission Events**

    Streams the events of a submission.
    """
    return controller.get_submission_events(submission_id)

# -- PATCH ENDPOINTS -- #


# @router.patch(
#     '/{score_id}',
#     status_code=status.HTTP_200_OK,
#     response_model=None
# )
# async def update_score(session: SessionDep, user: ModeDep, score_id: int, score_in: schema.ScoreUpdate) -> None:
#     """
#     **Update an existing Score**

#     _Requires MODERATOR role_

#     Accepts updated Score information and updates the corresponding Score
#     record in the database.
#     """
#     await controller.update_score(session, score_id, score_in)


# -- DELETE ENDPOINTS -- #


# @router.delete(
#     '/{score_id}',
#     status_code=status.HTTP_200_OK,
#     response_model=None
# )
# async def delete_score(session: SessionDep, user: ModeDep, score_id: int) -> None:
#     """
#     **Delete an existing Score**

#     _Requires MODERATOR role_

#     Accepts a Score ID and deletes the corresponding Score record from the database.
#     """
#     await controller.delete_score(session, score_id)
