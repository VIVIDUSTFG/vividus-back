import asyncio
from typing import List

import redis
from sqlmodel import func

from src.core.config import settings
from src.core.deps import SessionDep
from src.modules.scores import model, schema

redis_client = redis.Redis(host=settings.REDIS_HOST,
                           port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD, db=1)


# -- UTILS SERVICES -- #


async def check_score(session: SessionDep, **kwargs) -> bool:
    return await model.Score.exists(session, **kwargs)


# -- CREATE SERVICES -- #


async def create_score(session: SessionDep, score_in: schema.ScoreCreate) -> None:
    await model.Score.create(session, **score_in.model_dump())


# -- READ SERVICES -- #


async def get_all_scores(session: SessionDep, dataset_id: int | None, submission_id: int | None, status: model.ScoreStatus | None) -> list[schema.ScoreOut]:
    params = {
        "session": session,
    }
    if dataset_id is not None:
        params["dataset_id"] = dataset_id
    if submission_id is not None:
        params["submission_id"] = submission_id
    if status is not None:
        params["status"] = status
    return await model.Score.get_multi(**params)


async def get_score_details(session: SessionDep, **kwargs) -> model.Score | None:
    return await model.Score.get(session, **kwargs)


async def get_all_grouped_scores_by_submission(session: SessionDep, limit: int | None, dataset_id: int | None) -> List[schema.GroupedSubmissionScoresOut]:
    filters = {
        "status": model.ScoreStatus.SUCCESS,
        "dataset_id": dataset_id
    }
    aggregates = {
        "precision": func.avg,
        "accuracy": func.avg,
        "recall": func.avg,
        "f1": func.avg,
        "aoc_roc": func.avg,
        "aoc_pr": func.avg
    }
    grouped_scores = await model.Score.get_grouped_aggregates(
        session=session,
        group_by="submission_id",
        aggregates=aggregates,
        limit=limit,
        **filters
    )
    return grouped_scores


async def stream_submission_events(submission_id):
    pubsub = redis_client.pubsub()
    pubsub.subscribe("entity_updates")

    while True:
        message = pubsub.get_message()
        if message and message["type"] == "message":
            data = message.get("data")
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            elif isinstance(data, int):
                data = str(data)
            if data == str(submission_id):
                yield f"data: {data}\n\n"
        await asyncio.sleep(5)


# -- UPDATE SERVICES -- #


async def update_score(session: SessionDep, old_score: model.Score, score_in: schema.ScoreUpdate) -> None:
    await old_score.update(session, **score_in.model_dump())
    redis_client.publish("entity_updates", str(old_score.submission_id))


# -- DELETE SERVICES -- #


async def delete_score(session: SessionDep, score_id: int) -> None:
    await model.Score.delete(session, id=score_id)


async def delete_all_submission_scores(session: SessionDep, submission_id: int) -> None:
    await model.Score.delete_multi(session, submission_id=submission_id)
