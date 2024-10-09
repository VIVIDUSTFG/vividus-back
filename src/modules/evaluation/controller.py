from fastapi import HTTPException
from pydantic import ValidationError
from redis import Redis
from rq import Queue

from src.core.config import settings
from src.core.deps import SessionDep
from src.modules.dataset.model import Dataset
from src.modules.evaluation import schema, service
from src.modules.scores.controller import (
    check_score, create_score, delete_score,
    get_score_details_by_dataset_and_submission)
from src.modules.scores.model import Score
from src.modules.scores.schema import ScoreCreate
from src.modules.submission.model import Submission

redis_conn = Redis(host=settings.REDIS_HOST,
                   port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)

# -- POST METHODS -- #


async def submit_evaluation(session: SessionDep, evaluation_in: schema.EvaluationCreate) -> None:
    try:
        submission_id = await Submission.get_column_value(session, 'id', accessor=evaluation_in.submission_accessor)
        dataset_id = await Dataset.get_column_value(session, 'id', accessor=evaluation_in.dataset_accessor)

        score_check = await check_score(session, submission_id=submission_id, dataset_id=dataset_id)
        if not score_check:
            await create_score(session, ScoreCreate(submission_id=submission_id, dataset_id=dataset_id))
        else:
            score = await get_score_details_by_dataset_and_submission(session, dataset_id, submission_id)
            await delete_score(session, score_id=score.id)
            await create_score(session, ScoreCreate(submission_id=submission_id, dataset_id=dataset_id))
        score_id = await Score.get_column_value(
            session, 'id', submission_id=submission_id, dataset_id=dataset_id)

        queue = Queue(connection=redis_conn)
        job = queue.enqueue(service.submit_evaluation, evaluation_in.dataset_accessor,
                            evaluation_in.submission_accessor, score_id)
        return None
    except ValidationError as e:
        error_code = 400
        error_detail = e.errors()
        raise HTTPException(status_code=error_code, detail=error_detail)
    except Exception as e:
        score_check = await check_score(session, submission_id=submission_id, dataset_id=dataset_id)
        if score_check:
            await Score.delete(session, submission_id=submission_id, dataset_id=dataset_id)
        error_code = 500
        error_detail = e
        raise HTTPException(status_code=error_code, detail=error_detail) from e
