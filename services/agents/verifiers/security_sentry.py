"""SecuritySentry verifier for EchoChamber Phase 1.

Phase 1 rules enforced:
- workspaceId is required
- artifacts must include evidence references
- artifact rows must belong to the requested workspace
- auto-send / external side effects remain disallowed by policy
"""

from __future__ import annotations

import json
from typing import Any

from services.store.ops_store import OpsStore


FORBIDDEN_ACTIONS = {
    "send_email",
    "send_message",
    "post_ticket_update",
    "external_write",
    "webhook_post",
}


class SecuritySentry:
    def __init__(self, store: OpsStore | None = None):
        self.store = store or OpsStore()

    def validate_workspace(self, workspace_id: str) -> dict[str, Any]:
        is_valid = bool(workspace_id and workspace_id.strip())
        return {
            "check": "workspace_required",
            "passed": is_valid,
            "message": "workspaceId present" if is_valid else "workspaceId missing",
        }

    def validate_artifacts(self, workspace_id: str) -> dict[str, Any]:
        artifacts = self.store.list_artifacts(workspace_id)
        failures: list[str] = []

        for artifact in artifacts:
            if artifact["workspaceId"] != workspace_id:
                failures.append(f"Artifact workspace mismatch: {artifact['artifactKey']}")
                continue

            evidence_refs = json.loads(artifact["evidenceRefsJson"])
            if not evidence_refs:
                failures.append(f"Artifact missing evidence refs: {artifact['artifactKey']}")

        return {
            "check": "artifact_validation",
            "passed": len(failures) == 0,
            "message": "Artifacts validated" if not failures else "; ".join(failures),
            "artifactCount": len(artifacts),
        }

    def validate_actions(self, requested_actions: list[str] | None = None) -> dict[str, Any]:
        requested_actions = requested_actions or []
        forbidden = [action for action in requested_actions if action in FORBIDDEN_ACTIONS]
        return {
            "check": "forbidden_actions",
            "passed": len(forbidden) == 0,
            "message": "No forbidden actions requested" if not forbidden else f"Forbidden actions: {', '.join(forbidden)}",
        }

    def run(self, workspace_id: str, requested_actions: list[str] | None = None) -> dict[str, Any]:
        checks = [
            self.validate_workspace(workspace_id),
            self.validate_artifacts(workspace_id) if workspace_id and workspace_id.strip() else {
                "check": "artifact_validation",
                "passed": False,
                "message": "workspaceId missing, artifact validation skipped",
                "artifactCount": 0,
            },
            self.validate_actions(requested_actions),
        ]

        passed = all(check["passed"] for check in checks)
        return {
            "verifier": "SecuritySentry",
            "workspaceId": workspace_id,
            "passed": passed,
            "checks": checks,
        }
