from fastapi import APIRouter

from services.intelligence.root_cause_engine import RootCauseEngine

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/{workspace_id}")
def diagnose(workspace_id: str):
    engine = RootCauseEngine()
    return engine.diagnose_workspace(workspace_id)
