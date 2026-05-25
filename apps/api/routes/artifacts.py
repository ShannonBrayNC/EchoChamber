from fastapi import APIRouter, HTTPException, Query
from packages.echochamber.artifacts.service import ArtifactService
from apps.api.middleware.workspace_guard import WorkspaceGuard

router = APIRouter()
artifact_service = ArtifactService()


@router.get('/artifacts/{artifact_id}')
def get_artifact(
    artifact_id: str,
    workspaceId: str = Query(..., description='Workspace boundary for artifact retrieval')
):
    WorkspaceGuard.validate_workspace(workspaceId)

    try:
        artifact = artifact_service.get_artifact(
            artifact_id=artifact_id,
            workspace_id=workspaceId
        )
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail='Artifact does not belong to requested workspace'
        )

    if not artifact:
        raise HTTPException(
            status_code=404,
            detail='Artifact not found'
        )

    return artifact
