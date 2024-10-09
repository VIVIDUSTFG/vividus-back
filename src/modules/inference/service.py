import asyncio
import mimetypes
import os
import shutil
from pathlib import Path
from uuid import uuid4

import numpy as np
from fastapi import HTTPException, UploadFile, status
from kubernetes import client, config, watch

from src.core.config import settings
from src.core.deps import SessionDep
from src.modules.submission.model import Submission, SubmissionStatus

try:
    config.load_incluster_config()
except Exception:
    config.load_kube_config()

v1 = client.CoreV1Api()
batch_v1 = client.BatchV1Api()


# -- UTILITY METHODS -- #


async def is_valid_video_file(file: UploadFile) -> bool:
    mime_type = mimetypes.guess_type(file.filename)
    if not mime_type or not mime_type.startswith('video'):
        return False

    return True


def fetch_pod_logs(pod_name, namespace='argo'):
    try:
        logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
        return logs
    except client.exceptions.ApiException as e:
        return f"Error fetching logs for pod {pod_name}: {e}\n\n"


def parse_time(seconds):
    seconds = max(0, seconds)
    sec = seconds % 60
    if sec < 10:
        sec = "0" + str(sec)
    else:
        sec = str(sec)
    return str(seconds // 60) + ":" + sec


# -- REMOVAL METHODS -- #


def terminate_workflow(workflow_name: str):
    custom_api = client.CustomObjectsApi()
    try:
        custom_api.patch_namespaced_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            namespace="argo",
            plural="workflows",
            name=workflow_name,
            body={"spec": {"shutdown": "Terminate"}}
        )
    except client.exceptions.ApiException as e:
        pass


def delete_workflow(workflow_name: str):
    custom_api = client.CustomObjectsApi()
    try:
        custom_api.delete_namespaced_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            namespace="argo",
            plural="workflows",
            name=workflow_name
        )
    except client.exceptions.ApiException as e:
        pass


def remove_tmp_data(workflow_name: str):
    data_path = Path(settings.TMP_DIR) / workflow_name
    try:
        if os.path.exists(data_path):
            shutil.rmtree(data_path)
    except Exception as exc:
        pass


# -- SUBMISSION METHODS -- #


async def create_and_submit_workflow(workflow_name: str, feature_type: str, video_path: str, data_path: str, model: str, model_path: str):
    workflow_manifest = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Workflow",
        "metadata": {
            "name": workflow_name,
            "namespace": "argo"
        },
        "spec": {
            "workflowTemplateRef": {
                "name": "inference-workflow"
            },
            "arguments": {
                "parameters": [
                    {"name": "featureType", "value": feature_type},
                    {"name": "videoPath", "value": video_path},
                    {"name": "dataPath", "value": data_path},
                    {"name": "model", "value": model},
                    {"name": "modelPath", "value": model_path}
                ]
            }
        }
    }

    custom_api = client.CustomObjectsApi()
    try:
        custom_api.create_namespaced_custom_object(
            group="argoproj.io",
            version="v1alpha1",
            namespace="argo",
            plural="workflows",
            body=workflow_manifest
        )
    except client.exceptions.ApiException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error submitting workflow: {e}") from e


async def submit_inference(session: SessionDep, file: UploadFile, model: str) -> str:
    workflow_name = str(uuid4())
    data_path = Path(settings.TMP_DIR) / workflow_name
    data_path.mkdir(parents=True, exist_ok=True)

    video_path = data_path / file.filename

    try:
        with open(video_path, "wb") as buffer:
            while data := await file.read(1024):
                buffer.write(data)
    except Exception as exc:
        remove_tmp_data(workflow_name)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Error uploading video file') from exc

    feature_type = await Submission.get_column_value(session, "modality", accessor=model, status=SubmissionStatus.PUBLISHED)

    match feature_type:
        case "rgb_only":
            _rgb_list = (data_path / "rgb.list").touch()
        case "rgb_and_audio":
            _rgb_list = (data_path / "rgb.list").touch()
            _audio_list = (data_path / "audio.list").touch()
        case _:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Invalid model')

    try:
        # await create_and_submit_workflow(workflow_name=workflow_name,
        #                                  feature_type=feature_type,
        #                                  video_path=str(
        #                                      f"/tmp_inference/{workflow_name}/{file.filename}"),
        #                                  data_path=str(
        #                                      f"/tmp_inference/{workflow_name}"),
        #                                  model=model,
        #                                  model_path=str("/infer_models"))  # TODO production paths

        await create_and_submit_workflow(workflow_name=workflow_name,
                                         feature_type=feature_type,
                                         video_path=str(
                                             f"{settings.TMP_DIR}/{workflow_name}/{file.filename}"),
                                         data_path=str(
                                             f"{settings.TMP_DIR}/{workflow_name}"),
                                         model=model,
                                         model_path=str({settings.INFER_DIR}))
        return workflow_name
    except Exception as exc:
        remove_tmp_data(workflow_name)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Error submitting workflow') from exc


def get_workflow_result(workflow_name: str):
    data_path = Path(settings.TMP_DIR) / workflow_name
    if not data_path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Workflow {workflow_name} not found")

    try:
        result_path = data_path / "results.npy"
        pred_binary = list(np.load(result_path))

        result = {
            "contains_violence": any(pred == 1 for pred in pred_binary),
            "violence_intervals_seconds": [],
            "violence_intervals_frames": [],
        }

        video_duration = int(np.ceil(len(pred_binary) * 0.96))

        if result["contains_violence"]:
            start_idx = None
            for i, pred in enumerate(pred_binary):
                if pred == 1:
                    if start_idx is None:
                        start_idx = i
                elif start_idx is not None:
                    interval_frames = [start_idx, i - 1] if i - \
                        1 != start_idx else [start_idx]
                    interval_seconds = [parse_time(
                        int(np.floor((start_idx + 1) * 0.96))), parse_time(int(np.ceil(i * 0.96)))]
                    result["violence_intervals_frames"].append(interval_frames)
                    result["violence_intervals_seconds"].append(
                        interval_seconds)
                    start_idx = None

            if start_idx is not None:
                interval_frames = [start_idx, len(
                    pred_binary) - 1] if len(pred_binary) - 1 != start_idx else [start_idx]
                interval_seconds = [parse_time(
                    int(np.floor((start_idx + 1) * 0.96))), parse_time(video_duration)]
                result["violence_intervals_frames"].append(interval_frames)
                result["violence_intervals_seconds"].append(interval_seconds)

        return result

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error loading result for workflow {workflow_name}: {exc}") from exc
    finally:
        remove_tmp_data(workflow_name)


# -- STREAMING METHODS -- #


async def stream_workflow_events(workflow_name: str):
    custom_api = client.CustomObjectsApi()
    watcher = watch.Watch()

    workflow_completed = False
    pod_statuses = {}

    try:
        while not workflow_completed:
            try:
                # Fetch the workflow status
                workflow = custom_api.get_namespaced_custom_object(
                    group="argoproj.io",
                    version="v1alpha1",
                    namespace="argo",
                    plural="workflows",
                    name=workflow_name,
                )
                workflow_status = workflow.get('status')

                if workflow_status:
                    workflow_phase = workflow_status.get('phase', 'Unknown')
                else:
                    workflow_phase = 'Unknown'

                # Stream pod events
                for event in watcher.stream(v1.list_namespaced_pod, namespace='argo', label_selector=f'workflows.argoproj.io/workflow={workflow_name}', timeout_seconds=30):
                    obj = event['object']
                    pod_name = obj.metadata.name
                    pod_status = obj.status.phase

                    # Track pod statuses to ensure we capture all events
                    if pod_name not in pod_statuses or pod_statuses[pod_name] != pod_status:
                        pod_statuses[pod_name] = pod_status
                        yield f"data: Pod {pod_name} status: {pod_status}\n\n"

                        # Fetch and yield logs if the pod failed
                        if pod_status in ['Failed', 'Error']:
                            logs = fetch_pod_logs(pod_name)
                            yield f"data: Pod {pod_name} logs:\n{logs}\n\n"

                # Check if the workflow itself has completed
                if workflow_phase in ['Succeeded', 'Failed', 'Error']:
                    yield f"data: Workflow {workflow_name} status: {workflow_phase}\n\n"
                    workflow_completed = True
                    break
                else:
                    yield f"data: Workflow {workflow_name} status: {workflow_phase}\n\n"

                await asyncio.sleep(5)  # Short delay to avoid tight loop

            except client.exceptions.ApiException as e:
                yield f"data: Error Fetching Workflow Status: {e}\n\n"
                break

            except Exception as e:
                yield f"data: Workflow Unexpected Error: {e}\n\n"
                break

    finally:
        watcher.stop()
