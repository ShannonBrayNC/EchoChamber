from fastapi import APIRouter, Body

from services.intelligence.auto_apply_learning import AutoApplyLearningService

router = APIRouter(prefix="/auto-apply", tags=["auto-apply"])

service = AutoApplyLearningService()


@router.post("/{workspace_id}/{message_id}")
def auto_apply_message(workspace_id: str, message_id: str):
    return service.auto_apply_for_message(workspace_id, message_id)


@router.post("/{workspace_id}")
def auto_apply_workspace(workspace_id: str, body: dict = Body(default={})):  # noqa: B008
    return service.auto_apply_for_workspace(
        workspace_id,
        limit=body.get("limit", 25),
    )
