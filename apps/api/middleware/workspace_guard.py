from fastapi import HTTPException


class WorkspaceGuard:

    @staticmethod
    def validate_workspace(workspace_id: str):
        if not workspace_id:
            raise HTTPException(
                status_code=400,
                detail='workspaceId is required'
            )

        if '..' in workspace_id:
            raise HTTPException(
                status_code=400,
                detail='Invalid workspaceId'
            )
