"""Execution logging for EchoChamber Phase 1.

Stores orchestration run summaries as workspace-scoped artifacts so runs are
queryable, auditable, and replay-friendly.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from services.store.ops_store import ArtifactRecord, OpsStore


class ExecutionLogger:
    def __init__(self, store: OpsStore | None = None):
        self.store = store or OpsStore()

    def log_run(
        self,
        workspace_id: str,
        status: str,
        stage: str,
        details: dict[str, Any],
        evidence_refs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        run_id = f"run-{uuid4()}"
        payload = {
            "runId": run_id,
            "status": status,
            "stage": stage,
            "details": details,
            "recordedAt": datetime.now(timezone.utc).isoformat(),
        }
        artifact = ArtifactRecord(
            workspace_id=workspace_id,
            artifact_type="ExecutionLog",
            artifact_key=run_id,
            content_json=json.dumps(payload),
            evidence_refs_json=json.dumps(evidence_refs or []),
        )
        self.store.upsert_artifact(artifact)
        return payload
