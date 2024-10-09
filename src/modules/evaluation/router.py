from fastapi import APIRouter, status

from src.core.deps import AdminDep, SessionDep
from src.modules.evaluation import controller, schema

router = APIRouter(tags=['Evaluation'])


# -- POST ENDPOINTS -- #


@router.post(
    '',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def submit_evaluation(session: SessionDep, user: AdminDep, evaluation_in: schema.EvaluationCreate):
    """
    **Submit an Evaluation**

    _Requires USER role_

    Accepts an evaluation to be submitted.
    """
    await controller.submit_evaluation(session, evaluation_in)
