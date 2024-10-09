from fastapi import APIRouter, File, Form, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse

from src.core.deps import SessionDep, UserDep
from src.modules.inference import controller

router = APIRouter(tags=['Inference'])

# -- POST ENDPOINTS -- #


@router.post(
    '',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def submit_inference(session: SessionDep, user: UserDep, file: UploadFile = File(...), model: str = Form(...)) -> JSONResponse:
    """
    **Submit an Inference**

    _Requires USER role_

    Accepts a video file and a model name to perform inference.
    """
    return await controller.submit_inference(session, file, model)


@router.post(
    '/terminate/{workflow_name}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
def terminate_and_delete_workflow(user: UserDep, workflow_name: str) -> None:
    """
    **Terminate and Delete Workflow**

    Terminates and deletes a workflow.
    """
    return controller.terminate_and_delete_workflow(workflow_name)


# -- GET ENDPOINTS -- #


@router.get(
    '/events/{workflow_name}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
async def get_workflow_events(workflow_name: str) -> StreamingResponse:
    """
    **Get Workflow Events**

    Streams the events of a workflow.
    """
    return controller.get_workflow_events(workflow_name)


@router.get(
    '/result/{workflow_name}',
    status_code=status.HTTP_200_OK,
    response_model=None
)
def get_workflow_result(user: UserDep, workflow_name: str) -> JSONResponse:
    """
    **Get Workflow Result**

    _Requires USER role_

    Returns the result of a workflow.
    """
    return controller.get_workflow_result(workflow_name)
