# pylint: disable=W0613

from typing import List

from fastapi import APIRouter, Query, status

from src.core.deps import AdminDep, SessionDep, UserDep
from src.modules.submission import controller, schema

router = APIRouter(tags=['Submission'])

# Falta una función para lanzar los tests de un modelo (cola de tareas)


# -- POST ENDPOINTS -- #


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=None
)
async def create_submission(session: SessionDep, user: UserDep, model_in: schema.SubmissionCreate) -> None:
    """
    **Create a new Submission**

    _Requires User role_

    Accepts Submission data and creates a new Submission record in DRAFT status in the database.
    """
    await controller.create_submission(session, user, model_in)


# -- GET ENDPOINTS -- #


@router.get(
    '/model/{submission_accessor}',
    status_code=status.HTTP_200_OK,
    response_model=schema.SubmissionOut
)
async def get_submission_details(session: SessionDep, user: UserDep, submission_accessor: str) -> schema.SubmissionOut:
    """
    **Get detailed information about a specific Submission**

    Fetches and returns detailed information about a specific Submission identified by its accessor.
    """
    return await controller.get_submission_details(session, user, submission_accessor)


@router.get(
    '/published',
    status_code=status.HTTP_200_OK,
    response_model=List[schema.SubmissionInfoListOut]
)
async def get_all_published_submissions(session: SessionDep, user: UserDep) -> List[schema.SubmissionInfoListOut]:
    """
    **Retrieve a list of all published Submissions**

    _Requires USER role_

    Queries the database and returns a list of all Submissions that have PUBLISHED status.
    """
    return await controller.get_all_published_submissions(session)


@router.get(
    '/pending',
    status_code=status.HTTP_200_OK,
)
async def get_all_pending_submissions(session: SessionDep, user: AdminDep) -> List[schema.SubmissionInfoListOut]:
    """
    **Retrieve a list of the Submissions with in review, request for changes or accepted status**

    Queries the database and returns a list of all Submissions to be managed by Admin.
    """
    return await controller.get_all_pending_submissions(session)


@router.get(
    '/user/{user_id}',
    status_code=status.HTTP_200_OK,
)
async def get_all_user_submissions(session: SessionDep, user: UserDep, user_id: int, submission_status: schema.SubmissionStatus | None = Query(None)) -> List[schema.SubmissionInfoListOut]:
    """
    **Retrieve a list of the Submissions from the User specified**

    _Requires User role with the same ID as the User specified or Admin role_

    Queries the database and returns a list of all Submissions of the current logged user.
    """
    return await controller.get_all_user_submissions(session, user, user_id, submission_status)


@router.get(
    '/{submission_id}/rank',
    status_code=status.HTTP_200_OK,
)
async def get_submission_rank(session: SessionDep, submission_id: int) -> schema.SubmissionRankOut:
    """
    **Retrieve the rank of a specific Submission**

    Queries the database and returns the rank of a specific Submission.
    """
    return await controller.get_submission_rank(session, submission_id)


@router.get(
    '/{submission_id}/scores',
    status_code=status.HTTP_200_OK,
)
async def get_submission_scores(session: SessionDep, submission_id: int) -> schema.SubmissionScoreOut | None:
    """
    **Retrieve the metrics of a specific Submission**

    Queries the database and returns the metrics of a specific Submission.
    """
    return await controller.get_submission_scores(session, submission_id)


@router.get(
    '/{submission_id}/results',
    status_code=status.HTTP_200_OK,
)
async def get_submission_results(session: SessionDep, user: UserDep, submission_id: int) -> List[schema.SubmissionResultsOut]:
    """
    **Retrieve the results of a specific Submission**

    Queries the database and returns the results of a specific Submission.
    """
    return await controller.get_submission_results(session, user, submission_id)


@router.get(
    '/{submission_id}/test-records',
    status_code=status.HTTP_200_OK,
)
async def get_submission_test_records(session: SessionDep, admin: AdminDep, submission_id: int) -> List[schema.SubmissionTestRecordOut]:
    """
    **Retrieve the test records of a specific Submission**

    _Requires ADMIN role_

    Queries the database and returns the test records of a specific Submission.
    """
    return await controller.get_submission_test_records(session, submission_id)

# -- PATCH ENDPOINTS -- #


@router.patch(
    '/{submission_id}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=None
)
async def update_submission(session: SessionDep, user: UserDep, submission_id: int, submission_in: schema.SubmissionUpdate) -> None:
    """
    **Update an existing Submission**

    _Requires User role with the same ID as the Submission to patch or Admin role_

    Accepts updated Submission information and updates the corresponding Submission 
    record in the database.
    """
    await controller.update_submission(session, user, submission_id, submission_in)


@router.patch(
    '/{submission_id}/status',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=None
)
async def change_submission_status(session: SessionDep, user: AdminDep, submission_id: int, submission_status: schema.SubmissionChangeStatus) -> None:
    """
    **Change the status of a specific Submission**

    _Requires ADMIN role_

    Accepts updated Submission status information and updates the corresponding Submission record in the database.
    """
    await controller.change_submission_status(session, submission_id, submission_status)


@router.patch(
    '/{submission_id}/submit',
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_entry(session: SessionDep, user: UserDep, submission_id: int) -> None:
    """
    **Submit an entry for review**

    _Requires USER role with the same ID as the Submission to submit_

    Accepts an existing Submission in DRAFT or REQUEST_FOR_CHANGES status and submits it for review.
    """
    await controller.submit_entry(session, user, submission_id)


@router.patch(
    '/{submission_id}/review',
    status_code=status.HTTP_202_ACCEPTED,
)
async def review_submission(session: SessionDep, user: AdminDep, submission_id: int, submission_review: schema.SubmissionReview) -> None:
    """
    **Review a Submission**

    _Requires ADMIN role_

    Accepts a review message and updates the status of a specific Submission to be reviewed.
    """
    return await controller.review_submission(session, submission_id, submission_review)


# -- DELETE ENDPOINTS -- #


@router.delete(
    '/{submission_accessor}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def delete_model(session: SessionDep, user: UserDep, submission_accessor: str) -> None:
    """
    **Delete a Submission**

    _Requires USER role with the same ID as the Submission to delete_

    Deletes a Submission record from the database.
    """
    await controller.delete_submission(session, user, submission_accessor)
