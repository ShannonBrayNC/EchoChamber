"""Instant exception-to-runway feedback loop for EchoChamber.

Applies an exception action and immediately regenerates the workspace runway so
operator corrections show up in downstream execution planning without waiting
for a separate orchestration cycle.
"""

from __future__ import annotations

from typing import Any

from services.intelligence.exception_actions import ExceptionActionService
from services.agents.content.daily_runway_agent_production import generate_runway
from services.store.ops_store import OpsStore


class ExceptionFeedbackLoopService:
    def __init__(self, store: OpsStore | None = None) -> None:
        self.store = store or OpsStore()
        self.actions = ExceptionActionService(self.store)

    def promote_and_refresh(
        self,
        workspace_id: str,
        message_id: str,
        target_type: str,
        note: str | None = None,
        operator: str = "ui",
    ) -> dict[str, Any]:
        action = self.actions.promote(
            workspace_id=workspace_id,
            message_id=message_id,
            target_type=target_type,
            note=note,
            operator=operator,
        )
        runway = generate_runway(workspace_id, store=self.store)
        return {
            "status": "ok",
            "mode": "promote_and_refresh",
            "action": action,
            "runway": self._runway_summary(runway),
        }

    def fix_and_refresh(
        self,
        workspace_id: str,
        message_id: str,
        classification: str | None = None,
        confidence: float | None = None,
        payload_patch: dict[str, Any] | None = None,
        note: str | None = None,
        operator: str = "ui",
    ) -> dict[str, Any]:
        action = self.actions.fix(
            workspace_id=workspace_id,
            message_id=message_id,
            classification=classification,
            confidence=confidence,
            payload_patch=payload_patch,
            note=note,
            operator=operator,
        )
        runway = generate_runway(workspace_id, store=self.store)
        return {
            "status": "ok",
            "mode": "fix_and_refresh",
            "action": action,
            "runway": self._runway_summary(runway),
        }

    def ignore_and_refresh(
        self,
        workspace_id: str,
        message_id: str,
        note: str | None = None,
        operator: str = "ui",
    ) -> dict[str, Any]:
        action = self.actions.ignore(
            workspace_id=workspace_id,
            message_id=message_id,
            note=note,
            operator=operator,
        )
        runway = generate_runway(workspace_id, store=self.store)
        return {
            "status": "ok",
            "mode": "ignore_and_refresh",
            "action": action,
            "runway": self._runway_summary(runway),
        }

    @staticmethod
    def _runway_summary(runway: dict[str, Any]) -> dict[str, Any]:
        items = runway.get("items", [])
        return {
            "artifactType": runway.get("artifactType"),
            "workspaceId": runway.get("workspaceId"),
            "generatedAt": runway.get("generatedAt"),
            "counts": runway.get("counts", {}),
            "topItems": items[:5],
        }
