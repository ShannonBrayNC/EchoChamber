from fastapi import APIRouter

from services.intelligence.exception_suggestions import ExceptionSuggestionService

router = APIRouter(prefix="/exceptions/suggestions", tags=["exceptions-suggestions"])

service = ExceptionSuggestionService()


@router.get("/{workspace_id}")
def get_workspace_suggestions(workspace_id: str):
    return service.suggest_for_workspace(workspace_id)


@router.get("/{workspace_id}/{message_id}")
def get_message_suggestions(workspace_id: str, message_id: str):
    return service.suggest_for_message(workspace_id, message_id)
