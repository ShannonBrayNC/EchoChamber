from fastapi import APIRouter, Body

from services.intelligence.exception_feedback_loop import ExceptionFeedbackLoopService

router = APIRouter(prefix="/exceptions/feedback", tags=["exceptions-feedback"])

service = ExceptionFeedbackLoopService()


@router.post("/{workspace_id}/{message_id}/promote")
def promote_and_refresh(workspace_id: str, message_id: str, body: dict = Body(default={})):  # noqa: B008
    return service.promote_and_refresh(
        workspace_id,
        message_id,
        target_type=body.get("targetType", "task"),
        note=body.get("note"),
        operator=body.get("operator", "ui"),
    )


@router.post("/{workspace_id}/{message_id}/fix")
def fix_and_refresh(workspace_id: str, message_id: str, body: dict = Body(default={})):  # noqa: B008
    return service.fix_and_refresh(
        workspace_id,
        message_id,
        classification=body.get("classification"),
        confidence=body.get("confidence"),
        payload_patch=body.get("payloadPatch"),
        note=body.get("note"),
        operator=body.get("operator", "ui"),
    )


@router.post("/{workspace_id}/{message_id}/ignore")
def ignore_and_refresh(workspace_id: str, message_id: str, body: dict = Body(default={})):  # noqa: B008
    return service.ignore_and_refresh(
        workspace_id,
        message_id,
        note=body.get("note"),
        operator=body.get("operator", "ui"),
    )
