import asyncio
import os
import shutil
from pathlib import Path
from uuid import uuid4

import numpy as np
from fastapi import HTTPException, status
from kubernetes import client, config, watch
from sklearn.metrics import (accuracy_score, average_precision_score, f1_score,
                             precision_score, recall_score, roc_auc_score)

from src.core.config import settings
from src.core.database.session import SessionLocal
from src.core.deps import SessionDep
from src.modules.scores import controller as score_controller
from src.modules.scores.model import Score
from src.modules.scores.schema import ScoreStatus, ScoreUpdate
from src.modules.submission.model import Submission

try:
    config.load_incluster_config()
except Exception:
    config.load_kube_config()

v1 = client.CoreV1Api()
batch_v1 = client.BatchV1Api()


# -- UTILITY METHODS -- #


def fetch_pod_logs(pod_name, namespace='argo'):
    try:
        logs = v1.read_namespaced_pod_log(
            name=pod_name, namespace=namespace, container='main')
        return logs
    except client.exceptions.ApiException as e:
        return f"Error fetching logs for pod {pod_name}: {e}\n\n"


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


# -- SUBMISSIONS METHODS -- #


async def create_and_submit_evaluation(workflow_name: str, feature_type: str, data_path: str, model: str, model_path: str):
    workflow_manifest = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Workflow",
        "metadata": {
            "name": workflow_name,
            "namespace": "argo"
        },
        "spec": {
            "workflowTemplateRef": {
                "name": "evaluation-workflow"
            },
            "arguments": {
                "parameters": [
                    {"name": "featureType", "value": feature_type},
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


async def submit_evaluation(dataset_accessor: str, submission_accessor: str, score_id: int) -> None:
    async with SessionLocal() as session:
        workflow_name = str(uuid4())
        data_path = Path(settings.TMP_DIR) / workflow_name
        data_path.mkdir(parents=True, exist_ok=True)

        dataset_path = Path(settings.DATASETS_DIR) / dataset_accessor

        feature_type = await Submission.get_column_value(session, "modality", accessor=submission_accessor)

        for item in os.listdir(dataset_path):
            src_path = os.path.join(dataset_path, item)
            dst_path = os.path.join(data_path, item)

            if os.path.isdir(src_path):
                if not os.path.exists(dst_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    for sub_item in os.listdir(src_path):
                        shutil.copy(os.path.join(src_path, sub_item),
                                    os.path.join(dst_path, sub_item))
            else:
                shutil.copy(src_path, dst_path)

        match feature_type:
            case "rgb_only":
                _rgb_list = (data_path / "rgb.list").touch()
            case "rgb_and_audio":
                _rgb_list = (data_path / "rgb.list").touch()
                _audio_list = (data_path / "audio.list").touch()
            case _:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='Invalid model hello')

        try:
            # await create_and_submit_evaluation(
            #     workflow_name=workflow_name,
            #     feature_type=feature_type,
            #     data_path=str(f"/tmp_inference/{workflow_name}"),
            #     model=submission_accessor,
            #     model_path=str("/infer_models")  # TODO production paths
            # )
            await create_and_submit_evaluation(
                workflow_name=workflow_name,
                feature_type=feature_type,
                data_path=f"{settings.TMP_DIR}/{workflow_name}",
                model=submission_accessor,
                model_path=f"{settings.INFER_DIR}"
            )
            await watch_workflow_status(session, score_id, workflow_name)
        except Exception as exc:
            score_check = await score_controller.check_score(session, id=score_id)
            if score_check:
                await Score.delete(session, id=score_id)
            terminate_workflow(workflow_name)
            remove_tmp_data(workflow_name)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Error submitting evaluation: {exc}") from exc


# -- WATCHER METHODS -- #


async def watch_workflow_status(session: SessionDep, score_id: int, workflow_name: str):
    custom_api = client.CustomObjectsApi()
    watcher = watch.Watch()

    workflow_completed = False

    try:
        while not workflow_completed:
            try:
                workflow = custom_api.get_namespaced_custom_object(
                    group="argoproj.io",
                    version="v1alpha1",
                    namespace="argo",
                    plural="workflows",
                    name=workflow_name
                )
                workflow_status = workflow.get('status')

                if workflow_status:
                    workflow_phase = workflow_status.get('phase', 'Unknown')
                else:
                    workflow_phase = 'Unknown'

                for event in watcher.stream(v1.list_namespaced_pod, namespace="argo", label_selector=f"workflows.argoproj.io/workflow={workflow_name}", timeout_seconds=30):
                    obj = event['object']
                    pod_name = obj.metadata.name
                    pod_status = obj.status.phase

                    if pod_status in ['Failed', 'Error']:
                        logs = fetch_pod_logs(pod_name)
                        await score_controller.update_score(session, score_id=score_id, score_in=ScoreUpdate(status=ScoreStatus.ERROR, status_message=f"Pod {pod_name} failed: {logs}"))
                        workflow_completed = True
                        break

                if workflow_phase == 'Succeeded':
                    await get_workflow_result(session, workflow_name, score_id)
                    workflow_completed = True
                    break

                await asyncio.sleep(5)

            except client.exceptions.ApiException as e:
                await score_controller.update_score(session, score_id=score_id, score_in=ScoreUpdate(status=ScoreStatus.ERROR, status_message=f"Error while fetching workflow: {e}"))
                break
            except Exception as e:
                await score_controller.update_score(session, score_id=score_id, score_in=ScoreUpdate(status=ScoreStatus.ERROR, status_message=f"Unexpected error: {e}"))
                break
    finally:
        watcher.stop()


async def get_workflow_result(session: SessionDep, workflow_name: str, score_id: int):
    data_path = Path(settings.TMP_DIR) / workflow_name
    if not data_path.exists():
        await score_controller.update_score(session, score_id=score_id, score_in=ScoreUpdate(status=ScoreStatus.ERROR, status_message=f"Workflow {workflow_name} data_path not found"))
    else:

        try:
            result_path = data_path / "results.npy"
            pred = list(np.load(result_path))

            gt_path = data_path / "gt.npy"
            gt = list(np.load(gt_path))

            if len(pred) > len(gt):
                pred = pred[:len(gt)]
            elif len(pred) < len(gt):
                padding_size = len(gt) - len(pred)
                pred = np.pad(pred, (0, padding_size),
                              'constant', constant_values=0)

            precision = precision_score(gt, pred)
            accuracy = accuracy_score(gt, pred)
            f1 = f1_score(gt, pred)
            recall = recall_score(gt, pred)
            auc_roc = roc_auc_score(gt, pred)
            auc_pr = average_precision_score(gt, pred)

            await score_controller.update_score(session, score_id=score_id, score_in=ScoreUpdate(status=ScoreStatus.SUCCESS, status_message=None, precision=precision, accuracy=accuracy, f1=f1, recall=recall, aoc_roc=auc_roc, aoc_pr=auc_pr))

        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Error getting workflow result: {exc}") from exc
        finally:
            remove_tmp_data(workflow_name)
            delete_workflow(workflow_name)
