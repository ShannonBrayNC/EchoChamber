"""Adaptive intelligence API routes.
"""

from fastapi import APIRouter

from services.intelligence.adaptive_advisor import AdaptiveAdvisor

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/{workspace_id}")
def analyze_workspace(workspace_id: str):
    advisor = AdaptiveAdvisor()
    return advisor.analyze_workspace(workspace_id)
