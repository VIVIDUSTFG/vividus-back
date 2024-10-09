import os
import shutil
from typing import List

from git import Repo

from src.core.config import settings
from src.core.deps import SessionDep
from src.modules.submission import model, schema

# -- UTILS SERVICES -- #


async def check_submission(session: SessionDep, **kwargs) -> bool:
    return await model.Submission.exists(session, **kwargs)


async def count_submissions(session: SessionDep, **kwargs) -> int:
    return await model.Submission.count(session, **kwargs)


async def get_submission_column(session: SessionDep, column: str, **kwargs):
    return await model.Submission.get_column_value(session, column, **kwargs)


def remove_repo(accessor: str) -> None:
    repo_dir = os.path.join(settings.INFER_DIR, accessor)
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)


def clone_repo(accessor: str, repository_url: str) -> None:
    repo_dir = os.path.join(settings.INFER_DIR, accessor)
    remove_repo(accessor)
    Repo.clone_from(
        url=f"https://github.com/{repository_url}.git", to_path=repo_dir)


# -- CREATE SERVICES -- #


async def create_model(session: SessionDep, user_id: int, submission_in: schema.SubmissionCreate) -> model.Submission | None:
    submission_dict = submission_in.model_dump()
    submission_dict["user_id"] = user_id
    submission_dict["accessor"] = submission_in.title.lower().replace(" ", "-")
    return await model.Submission.create(session, **submission_dict)


# -- READ SERVICES -- #


async def get_submission_details(session: SessionDep, **kwargs) -> model.Submission | None:
    result = await model.Submission.get(session, **kwargs, load_strategy={"user": "selectin", "datasets": "selectin"})
    return result


async def get_all_submissions(session: SessionDep, user_id: int | None, submission_status: model.SubmissionStatus | None) -> List[schema.SubmissionOut]:
    params = {
        "session": session,
        "load_strategy": {"user": "selectin", "datasets": "selectin"}
    }

    if user_id is not None:
        params["user_id"] = user_id
    if submission_status is not None:
        params["status"] = submission_status

    return await model.Submission.get_multi(**params)


# TODO: Not sure if this works
async def get_all_pending_submissions(session: SessionDep) -> List[schema.SubmissionOut]:
    pending_statuses = [model.SubmissionStatus.IN_REVIEW,
                        model.SubmissionStatus.REQUEST_FOR_CHANGES, model.SubmissionStatus.ACCEPTED]
    return await model.Submission.get_multi(session, model.Submission.__table__.c.status.in_(pending_statuses), load_strategy={"user": "selectin", "datasets": "selectin"})


# -- UPDATE SERVICES -- #


async def update_submission(session: SessionDep, old_submission: model.Submission, submission_in: schema.SubmissionUpdate) -> model.Submission:
    submission_dict = submission_in.model_dump()
    if hasattr(submission_in, "title") and submission_in.title != old_submission.title:
        submission_dict["accessor"] = submission_in.title.lower().replace(
            " ", "-")

    return await old_submission.update(session, **submission_dict)


# -- DELETE SERVICES -- #


async def delete_submission(session: SessionDep, submission_accessor: str) -> None:
    await model.Submission.delete(session, accessor=submission_accessor)
