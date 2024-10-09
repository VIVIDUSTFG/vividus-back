from typing import List

from fastapi import HTTPException, status

from src.core.deps import SessionDep, UserDep
from src.modules.dataset.controller import get_dataset_column, get_dataset_details
from src.modules.scores.model import ScoreStatus
from src.modules.scores.service import delete_all_submission_scores
from src.modules.submission import model, schema, service
from src.modules.user.model import Role
from src.modules.scores import controller as scores_controller
from src.modules.dataset import controller as dataset_controller


# -- POST METHODS -- #


async def create_submission(session: SessionDep, user: UserDep, submission_in: schema.SubmissionCreate) -> None:
    title_check = await service.check_submission(session, title=submission_in.title)
    if title_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Submission already exists'
        )
    await service.create_model(session, user_id=user.id, submission_in=submission_in)


# -- GET METHODS -- #


async def get_submission_details(session: SessionDep, user: UserDep, submission_accessor: str) -> schema.SubmissionOut:
    submission_record = await service.get_submission_details(session, accessor=submission_accessor)
    if not submission_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    if (user.role != Role.ADMIN or user.id != submission_record.user_id) and submission_record.status != model.SubmissionStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized'
        )
    return submission_record


async def get_all_published_submissions(session: SessionDep) -> List[schema.SubmissionInfoListOut]:
    return await service.get_all_submissions(session, user_id=None, submission_status=model.SubmissionStatus.PUBLISHED)


async def get_all_pending_submissions(session: SessionDep) -> List[schema.SubmissionInfoListOut]:
    return await service.get_all_pending_submissions(session)


async def get_all_user_submissions(session: SessionDep, user: UserDep, user_id: int, submission_status: schema.SubmissionStatus | None) -> List[schema.SubmissionInfoListOut]:
    if user.id != user_id or user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized'
        )

    return await service.get_all_submissions(session, user_id=user_id, submission_status=submission_status)


async def get_submission_rank(session: SessionDep, submission_id: int) -> schema.SubmissionRankOut:
    submission = await service.get_submission_details(session, id=submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    if submission.status != model.SubmissionStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Submission not published'
        )
    count = await service.count_submissions(session, status=model.SubmissionStatus.PUBLISHED)
    rank = await scores_controller.get_submission_rank(session, submission_id=submission_id)
    return {"rank": rank, "total": count}


async def get_submission_scores(session: SessionDep, submission_id: int) -> schema.SubmissionScoreOut | None:
    submission = await service.check_submission(session, id=submission_id, status=model.SubmissionStatus.PUBLISHED)
    if not submission:
        return None
    scores = await scores_controller.get_submission_scores(session, submission_id=submission_id)
    if not scores:
        return None
    title = await service.get_submission_column(session, column="title", id=submission_id)
    scores["title"] = title
    return scores


async def get_submission_results(session: SessionDep, user: UserDep, submission_id: int) -> List[schema.SubmissionResultsOut]:
    submission_record = await service.get_submission_details(session, id=submission_id)
    if not submission_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    if (user.role != Role.ADMIN or user.id != submission_record.user_id) and submission_record.status != model.SubmissionStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized'
        )

    scores_record = await scores_controller.get_all_scores(session, dataset_id=None, submission_id=submission_id, status=ScoreStatus.SUCCESS)
    results = []
    for item in scores_record:
        item = item.model_dump()
        dataset_accessor = await get_dataset_column(session, column="accessor", id=item["dataset_id"])
        dataset = await get_dataset_details(session, dataset_accessor=dataset_accessor)
        rank = await scores_controller.get_submission_rank_for_dataset(session, submission_id=submission_id, dataset_id=item["dataset_id"])
        results.append(schema.SubmissionResultsOut(rank=rank,
                                                   dataset_title=dataset.title, dataset_accessor=dataset_accessor, **item))

    return results


async def get_submission_test_records(session: SessionDep, submission_id: int) -> List[schema.SubmissionTestRecordOut]:
    submission_check = await service.check_submission(session, id=submission_id)
    if not submission_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    dataset_records = await dataset_controller.get_all_datasets(session)
    result = []
    for item in dataset_records:

        score_status = {
            "status": None,
            "status_message": None
        }
        score_entry = await scores_controller.get_score_details_by_dataset_and_submission(session, dataset_id=item.id, submission_id=submission_id)
        if score_entry:
            score_status["status"] = score_entry.status
            score_status["status_message"] = score_entry.status_message

        result.append(schema.SubmissionTestRecordOut(dataset_id=item.id,
                                                     dataset_title=item.title, dataset_accessor=item.accessor, **score_status))

    return result


# -- PATCH METHODS -- #


async def update_submission(session: SessionDep, user: UserDep, submission_id: int, submission_in: schema.SubmissionUpdate) -> None:
    old_submission = await service.get_submission_details(session, id=submission_id)
    if not old_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    if user.id != old_submission.user_id and user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized'
        )
    if old_submission.status not in [model.SubmissionStatus.DRAFT, model.SubmissionStatus.REQUEST_FOR_CHANGES]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Submission cannot be updated'
        )
    if submission_in.title and submission_in.title != old_submission.title:
        title_check = await service.check_submission(session, title=submission_in.title)
        if title_check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Submission already exists'
            )
    await service.update_submission(session, old_submission=old_submission, submission_in=submission_in)


async def change_submission_status(session: SessionDep, submission_id: int, submission_status: schema.SubmissionChangeStatus) -> None:
    old_submission = await service.get_submission_details(session, id=submission_id)
    if not old_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    if old_submission.status in [model.SubmissionStatus.ACCEPTED, model.SubmissionStatus.PUBLISHED] and submission_status.status not in [model.SubmissionStatus.ACCEPTED, model.SubmissionStatus.PUBLISHED]:
        service.remove_repo(old_submission.accessor)
        delete_all_submission_scores(session, submission_id)
    await service.update_submission(session, old_submission=old_submission, submission_in=submission_status)


async def submit_entry(session: SessionDep, user: UserDep, submission_id: int) -> None:
    old_submission = await service.get_submission_details(session, id=submission_id)
    if not old_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    if user.id != old_submission.user_id and user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unauthorized'
        )
    if old_submission.status not in [model.SubmissionStatus.DRAFT, model.SubmissionStatus.REQUEST_FOR_CHANGES]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Submission cannot be submitted'
        )
    await service.update_submission(session, old_submission=old_submission, submission_in=schema.SubmissionReview(status=model.SubmissionStatus.IN_REVIEW, review_message=None))


async def review_submission(session: SessionDep, submission_id: int, submission_review: schema.SubmissionReview) -> None:
    old_submission = await service.get_submission_details(session, id=submission_id)
    if not old_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    if old_submission.status not in [model.SubmissionStatus.IN_REVIEW, model.SubmissionStatus.REQUEST_FOR_CHANGES, model.SubmissionStatus.ACCEPTED]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Theres no submission to be reviewed with that id'
        )

    if submission_review.status == model.SubmissionStatus.ACCEPTED:
        try:
            service.clone_repo(old_submission.accessor,
                               old_submission.repository_url)
        except:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Could not clone repository'
            )
    await service.update_submission(session, old_submission=old_submission, submission_in=submission_review)


# -- DELETE METHODS -- #


async def delete_submission(session: SessionDep, user: UserDep, submission_accessor: str) -> None:
    submission_check = await service.check_submission(session, accessor=submission_accessor, user_id=user.id)
    if not submission_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Submission not found'
        )
    service.remove_repo(submission_accessor)
    await service.delete_submission(session, submission_accessor=submission_accessor)
