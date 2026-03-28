"""Run history query layer for EchoChamber Phase 1.

Provides workspace-scoped access to execution logs so the portal and future API
surfaces can inspect past runs without reading raw database rows directly.
"""

from __future__ import annotations

import json
from typing import Any

from services.store.ops_store import OpsStore


class RunHistoryQuery:
    def __init__(self, store: OpsStore | None = None):
        self.store = store or OpsStore()

    def list_runs(
        self,
        workspace_id: str,
        status: str | None = None,
        stage: str | None = None,
        limit: int | None = 20,
    ) -> list[dict[str, Any]]:
        artifacts = self.store.list_artifacts(workspace_id, artifact_type="ExecutionLog")
        runs: list[dict[str, Any]] = []

        for artifact in artifacts:
            payload = json.loads(artifact["contentJson"])
            payload["artifactKey"] = artifact["artifactKey"]
            payload["workspaceId"] = artifact["workspaceId"]
            payload["createdAt"] = artifact["createdAt"]
            payload["updatedAt"] = artifact["updatedAt"]

            if status and payload.get("status") != status:
                continue
            if stage and payload.get("stage") != stage:
                continue

            runs.append(payload)

        if limit is not None:
            return runs[:limit]
        return runs

    def get_run(self, workspace_id: str, run_id: str) -> dict[str, Any] | None:
        runs = self.list_runs(workspace_id, limit=None)
        for run in runs:
            if run.get("runId") == run_id or run.get("artifactKey") == run_id:
                return run
        return None

    def summarize_runs(self, workspace_id: str) -> dict[str, Any]:
        runs = self.list_runs(workspace_id, limit=None)
        total = len(runs)
        ok = sum(1 for run in runs if run.get("status") == "ok")
        failed = sum(1 for run in runs if run.get("status") == "failed")

        return {
            "workspaceId": workspace_id,
            "totalRuns": total,
            "okRuns": ok,
            "failedRuns": failed,
            "latestRun": runs[0] if runs else None,
        }
