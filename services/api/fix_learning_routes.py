from fastapi import APIRouter, Body

from services.intelligence.fix_learning import FixLearningService

router = APIRouter(prefix="/learning", tags=["learning"])

service = FixLearningService()


@router.post("/{workspace_id}/{message_id}/learn")
def learn_from_fix(workspace_id: str, message_id: str):
    return service.learn_from_fix(workspace_id, message_id)


@router.post("/{workspace_id}/rebuild")
def rebuild_index(workspace_id: str):
    return service.rebuild_workspace_index(workspace_id)


@router.get("/{workspace_id}/{message_id}")
def suggest_from_learning(workspace_id: str, message_id: str):
    return service.suggest_from_learning(workspace_id, message_id)
