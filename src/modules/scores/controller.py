from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from src.core.deps import SessionDep
from src.modules.scores import model, schema, service
from src.modules.submission.model import Submission, SubmissionStatus
from src.modules.submission.service import get_submission_details

weights = {
    "precision": 0.2,
    "accuracy": 0.2,
    "recall": 0.2,
    "f1": 0.2,
    "aoc_roc": 0.1,
    "aoc_pr": 0.1
}


# -- UTILS METHODS -- #


async def check_score(session: SessionDep, **kwargs) -> bool:
    return await service.check_score(session, **kwargs)


# -- POST METHODS -- #


async def create_score(session: SessionDep, score_in: schema.ScoreCreate) -> None:
    await service.create_score(session, score_in)


# -- GET METHODS -- #


async def get_score_details(session: SessionDep, score_id: int) -> schema.ScoreOut:
    score = await service.get_score_details(session, id=score_id)
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found"
        )
    return score


async def get_score_details_by_dataset_and_submission(session: SessionDep, dataset_id: int, submission_id: int) -> schema.ScoreOut:
    score = await service.get_score_details(session, dataset_id=dataset_id, submission_id=submission_id)
    return score


async def get_all_scores(session: SessionDep, dataset_id: int | None, submission_id: int | None, status: int | None) -> list[schema.ScoreOut]:
    return await service.get_all_scores(session, dataset_id=dataset_id, submission_id=submission_id, status=status)


async def get_best_submissions(session: SessionDep, limit: int | None, dataset_id: int) -> list[schema.BestSubmissionsListOut]:
    grouped_scores = await service.get_all_grouped_scores_by_submission(session, limit=None, dataset_id=dataset_id)
    count = 0
    ranked_models = []
    for score in grouped_scores:
        if count == limit:
            break

        submission = await Submission.get(session, id=score[0])

        if submission.status != SubmissionStatus.PUBLISHED:
            continue

        weighted_mean = sum(
            score[i + 1] * weight
            for i, (field, weight) in enumerate(weights.items())
        )

        ranked_models.append({
            "id": score[0],
            "title": submission.title,
            "accessor": submission.accessor,
            "resource_title": submission.resource_title,
            "resource_url": submission.resource_url,
            "repository_url": submission.repository_url,
            "precision": score[1],
            "accuracy": score[2],
            "recall": score[3],
            "f1": score[4],
            "aoc_roc": score[5],
            "aoc_pr": score[6],
            "weighted_mean": weighted_mean
        })
        count += 1

    ranked_models.sort(key=lambda x: x["weighted_mean"], reverse=True)

    return ranked_models


async def get_best_submission(session: SessionDep, dataset_id: int) -> schema.BestSubmissionOut | None:
    dataset_scores = await service.get_all_scores(session, dataset_id=dataset_id, submission_id=None, status=model.ScoreStatus.SUCCESS)
    if not dataset_scores:
        return None
    ranked_scores = []
    for score in dataset_scores:
        submission = await Submission.exists(session, id=score.submission_id, status=SubmissionStatus.PUBLISHED)
        if not submission:
            continue
        score = score.model_dump()
        weighted_mean = sum(
            score[field] * weight for field, weight in weights.items())
        score["weighted_mean"] = weighted_mean
        ranked_scores.append(score)

    ranked_scores.sort(key=lambda x: x["weighted_mean"], reverse=True)

    submission = await get_submission_details(session, id=ranked_scores[0]["submission_id"])

    result = schema.BestSubmissionOut(
        submission_id=submission.id, submission_title=submission.title, submission_accessor=submission.accessor)

    return result


async def get_submission_rank(session: SessionDep, submission_id: int) -> int:
    grouped_scores = await service.get_all_grouped_scores_by_submission(session, limit=None, dataset_id=None)

    ranked_models = []
    for score in grouped_scores:

        weighted_mean = sum(
            score[i + 1] * weight
            for i, (field, weight) in enumerate(weights.items())
        )

        ranked_models.append({
            "id": score[0],
            "weighted_mean": weighted_mean
        })

    ranked_models.sort(key=lambda x: x["weighted_mean"], reverse=True)

    for index, item in enumerate(ranked_models):
        if item["id"] == submission_id:
            return index + 1

    return None


async def get_submission_scores(session: SessionDep, submission_id: int) -> schema.SubmissionScoresOut | None:
    scores = await service.get_all_scores(session, dataset_id=None, submission_id=submission_id, status=model.ScoreStatus.SUCCESS)
    if not scores:
        return None
    score = {}
    for item in scores:
        item = item.model_dump()
        for field in weights.keys():
            if field not in score:
                score[field] = 0
            score[field] += item[field]

    for field in weights.keys():
        score[field] /= len(scores)

    return score


async def get_submission_rank_for_dataset(session: SessionDep, submission_id: int, dataset_id: int) -> int:
    grouped_scores = await service.get_all_grouped_scores_by_submission(session, limit=None, dataset_id=dataset_id)

    ranked_models = []
    for score in grouped_scores:

        weighted_mean = sum(
            score[i + 1] * weight
            for i, (field, weight) in enumerate(weights.items())
        )

        ranked_models.append({
            "id": score[0],
            "weighted_mean": weighted_mean
        })

    ranked_models.sort(key=lambda x: x["weighted_mean"], reverse=True)

    for index, item in enumerate(ranked_models):
        if item["id"] == submission_id:
            return index + 1

    return None


def get_submission_events(submission_id: int):
    return StreamingResponse(
        service.stream_submission_events(submission_id), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

# -- UPDATE METHODS -- #


async def update_score(session: SessionDep, score_id: int, score_in: schema.ScoreUpdate) -> None:
    old_score = await service.get_score_details(session, id=score_id)
    if not old_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found"
        )
    await service.update_score(session, old_score=old_score, score_in=score_in)


# -- DELETE METHODS -- #


async def delete_score(session: SessionDep, score_id: int) -> None:
    await service.delete_score(session, score_id)
