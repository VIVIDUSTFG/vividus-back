from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from src.core.deps import SessionDep
from src.modules.inference import service

# -- POST METHODS -- #


async def submit_inference(session: SessionDep, file: UploadFile, model: str) -> JSONResponse:
    try:
        result = await service.submit_inference(session, file, model)
        return JSONResponse(content={"workflow_name": result})
    except HTTPException as e:
        error_code = e.status_code
        error_detail = e.detail
        return HTTPException(status_code=error_code, detail=error_detail)


def terminate_and_delete_workflow(workflow_name: str) -> None:
    service.terminate_workflow(workflow_name)
    service.delete_workflow(workflow_name)
    service.remove_tmp_data(workflow_name)

# -- GET METHODS -- #


def get_workflow_events(workflow_name: str):
    return StreamingResponse(service.stream_workflow_events(workflow_name), media_type="text/event-stream")


def get_workflow_result(workflow_name: str):
    try:
        result = service.get_workflow_result(workflow_name)
        return result
    except HTTPException as e:
        error_code = e.status_code
        error_detail = e.detail
        return HTTPException(status_code=error_code, detail=error_detail)
