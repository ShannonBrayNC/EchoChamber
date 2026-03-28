"""Exception action service for EchoChamber.

Implements operator-driven actions for Inbox Intelligence exceptions:
- promote: convert exception signal into a durable Artifact for downstream handling
- fix: patch EmailEvent classification/confidence/payload metadata
- ignore: mark the message as ignored so it stops appearing in the exception queue

This version is designed to work with the current scaffolded Ops Store.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from services.store.ops_store import ArtifactRecord, OpsStore


class ExceptionActionError(ValueError):
    """Raised when an exception action cannot be completed."""


class ExceptionActionService:
    def __init__(self, store: OpsStore | None = None) -> None:
        self.store = store or OpsStore()

    def promote(
        self,
        workspace_id: str,
        message_id: str,
        target_type: str,
        note: str | None = None,
        operator: str = "operator",
    ) -> dict[str, Any]:
        row = self._get_email_event(workspace_id, message_id)
        payload = self._safe_json_loads(row["payloadJson"])
        promoted_at = self._utcnow()
        target_type = target_type.strip().lower()

        if target_type not in {"ticket", "task", "commitment", "noise"}:
            raise ExceptionActionError(f"Unsupported promotion target: {target_type}")

        artifact_key = f"{target_type}:{message_id}"
        content = {
            "artifactType": "ExceptionPromotion",
            "workspaceId": workspace_id,
            "messageId": message_id,
            "targetType": target_type,
            "subject": row["subject"],
            "classification": row["classification"],
            "confidence": row["confidence"],
            "note": note,
            "operator": operator,
            "promotedAt": promoted_at,
            "sourcePayload": payload,
        }
        evidence = [{
            "type": "EmailEvent",
            "messageId": message_id,
            "subject": row["subject"],
            "source": row["source"],
        }]

        self.store.upsert_artifact(
            ArtifactRecord(
                workspace_id=workspace_id,
                artifact_type="ExceptionPromotion",
                artifact_key=artifact_key,
                content_json=json.dumps(content),
                evidence_refs_json=json.dumps(evidence),
            )
        )

        return {
            "status": "ok",
            "action": "promote",
            "workspaceId": workspace_id,
            "messageId": message_id,
            "targetType": target_type,
            "artifactKey": artifact_key,
            "promotedAt": promoted_at,
        }

    def fix(
        self,
        workspace_id: str,
        message_id: str,
        classification: str | None = None,
        confidence: float | None = None,
        payload_patch: dict[str, Any] | None = None,
        note: str | None = None,
        operator: str = "operator",
    ) -> dict[str, Any]:
        row = self._get_email_event(workspace_id, message_id)
        payload = self._safe_json_loads(row["payloadJson"])
        payload_patch = payload_patch or {}
        payload.update(payload_patch)

        new_classification = (classification or row["classification"] or "other").strip()
        new_confidence = confidence if confidence is not None else float(row["confidence"] or 0.0)
        fixed_at = self._utcnow()

        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE EmailEvent
                SET classification = ?,
                    confidence = ?,
                    payloadJson = ?,
                    updatedAt = CURRENT_TIMESTAMP
                WHERE workspaceId = ? AND messageId = ?
                """,
                (
                    new_classification,
                    new_confidence,
                    json.dumps(payload),
                    workspace_id,
                    message_id,
                ),
            )

        audit_key = f"fix:{message_id}:{fixed_at}"
        self.store.upsert_artifact(
            ArtifactRecord(
                workspace_id=workspace_id,
                artifact_type="ExceptionFix",
                artifact_key=audit_key,
                content_json=json.dumps(
                    {
                        "workspaceId": workspace_id,
                        "messageId": message_id,
                        "classification": new_classification,
                        "confidence": new_confidence,
                        "payloadPatch": payload_patch,
                        "note": note,
                        "operator": operator,
                        "fixedAt": fixed_at,
                    }
                ),
                evidence_refs_json=json.dumps([
                    {
                        "type": "EmailEvent",
                        "messageId": message_id,
                        "subject": row["subject"],
                    }
                ]),
            )
        )

        return {
            "status": "ok",
            "action": "fix",
            "workspaceId": workspace_id,
            "messageId": message_id,
            "classification": new_classification,
            "confidence": new_confidence,
            "fixedAt": fixed_at,
        }

    def ignore(
        self,
        workspace_id: str,
        message_id: str,
        note: str | None = None,
        operator: str = "operator",
    ) -> dict[str, Any]:
        row = self._get_email_event(workspace_id, message_id)
        payload = self._safe_json_loads(row["payloadJson"])
        payload["ignored"] = True
        payload["ignoreNote"] = note
        payload["ignoredBy"] = operator
        payload["ignoredAt"] = self._utcnow()

        with self.store.connect() as conn:
            conn.execute(
                """
                UPDATE EmailEvent
                SET payloadJson = ?, updatedAt = CURRENT_TIMESTAMP
                WHERE workspaceId = ? AND messageId = ?
                """,
                (json.dumps(payload), workspace_id, message_id),
            )

        self.store.upsert_artifact(
            ArtifactRecord(
                workspace_id=workspace_id,
                artifact_type="ExceptionIgnore",
                artifact_key=f"ignore:{message_id}",
                content_json=json.dumps(
                    {
                        "workspaceId": workspace_id,
                        "messageId": message_id,
                        "note": note,
                        "operator": operator,
                        "ignoredAt": payload["ignoredAt"],
                    }
                ),
                evidence_refs_json=json.dumps([
                    {
                        "type": "EmailEvent",
                        "messageId": message_id,
                        "subject": row["subject"],
                    }
                ]),
            )
        )

        return {
            "status": "ok",
            "action": "ignore",
            "workspaceId": workspace_id,
            "messageId": message_id,
            "ignoredAt": payload["ignoredAt"],
        }

    def _get_email_event(self, workspace_id: str, message_id: str) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        with self.store.connect() as conn:
            row = conn.execute(
                """
                SELECT workspaceId, messageId, subject, source, classification, confidence, payloadJson
                FROM EmailEvent
                WHERE workspaceId = ? AND messageId = ?
                """,
                (workspace_id, message_id),
            ).fetchone()
        if not row:
            raise ExceptionActionError(f"EmailEvent not found for {workspace_id}/{message_id}")
        return dict(row)

    @staticmethod
    def _safe_json_loads(value: str | None) -> dict[str, Any]:
        if not value:
            return {}
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(UTC).isoformat()
