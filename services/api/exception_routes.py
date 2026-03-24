from fastapi import APIRouter, Body

from services.intelligence.exception_actions import ExceptionActionService

router = APIRouter(prefix="/exceptions", tags=["exceptions"])

service = ExceptionActionService()


@router.post("/{workspace_id}/{message_id}/promote")
def promote(workspace_id: str, message_id: str, body: dict = Body(default={})):  # noqa: B008
    return service.promote(
        workspace_id,
        message_id,
        target_type=body.get("targetType", "task"),
        note=body.get("note"),
        operator=body.get("operator", "ui"),
    )


@router.post("/{workspace_id}/{message_id}/fix")
def fix(workspace_id: str, message_id: str, body: dict = Body(default={})):  # noqa: B008
    return service.fix(
        workspace_id,
        message_id,
        classification=body.get("classification"),
        confidence=body.get("confidence"),
        payload_patch=body.get("payloadPatch"),
        note=body.get("note"),
        operator=body.get("operator", "ui"),
    )


@router.post("/{workspace_id}/{message_id}/ignore")
def ignore(workspace_id: str, message_id: str, body: dict = Body(default={})):  # noqa: B008
    return service.ignore(
        workspace_id,
        message_id,
        note=body.get("note"),
        operator=body.get("operator", "ui"),
    )
