from fastapi import APIRouter

from services.intelligence.inbox_intelligence import InboxIntelligenceService

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/{workspace_id}")
def get_inbox_intelligence(workspace_id: str):
    service = InboxIntelligenceService()
    return service.get_workspace_snapshot(workspace_id)
