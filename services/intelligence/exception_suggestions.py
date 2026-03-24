"""Smart exception suggestions for EchoChamber.

Provides lightweight operator guidance for Inbox Intelligence exceptions without
requiring a live LLM. Suggestions are deterministic and based on the stored
EmailEvent fields and payload metadata.
"""

from __future__ import annotations

import json
import re
from typing import Any

from services.store.ops_store import OpsStore

CW_TICKET_RE = re.compile(r"\b(\d{5,8})\b")
SN_TICKET_RE = re.compile(r"\b(?:INC|REQ|RITM|CHG|TASK)\d{4,10}\b", re.IGNORECASE)


class ExceptionSuggestionService:
    def __init__(self, store: OpsStore | None = None, confidence_threshold: float = 0.80) -> None:
        self.store = store or OpsStore()
        self.confidence_threshold = confidence_threshold

    def suggest_for_message(self, workspace_id: str, message_id: str) -> dict[str, Any]:
        row = self._get_email_event(workspace_id, message_id)
        payload = self._safe_json_loads(row.get("payloadJson"))
        subject = row.get("subject") or ""
        snippet = str(payload.get("snippet") or payload.get("summary") or "")
        combined = f"{subject} {snippet}"
        classification = (row.get("classification") or "").strip().lower()
        confidence = float(row.get("confidence") or 0.0)

        suggestions: list[dict[str, Any]] = []

        ticket_id = self._extract_ticket_id(payload) or self._detect_ticket_id(combined)
        if ticket_id and classification not in {"ticket_update", "ticket", "case_update"}:
            suggestions.append(
                {
                    "kind": "promote",
                    "priority": "high",
                    "title": "Promote to ticket workflow",
                    "reason": f"Detected likely ticket identifier {ticket_id} in message content.",
                    "proposedAction": {
                        "endpoint": f"/exceptions/feedback/{workspace_id}/{message_id}/fix",
                        "method": "POST",
                        "body": {
                            "classification": "ticket_update",
                            "confidence": 0.95,
                            "payloadPatch": {"ticketId": ticket_id},
                            "note": "Auto-suggested ticket classification",
                            "operator": "suggestion-engine",
                        },
                    },
                }
            )

        if self._looks_like_meeting(payload, combined) and classification not in {"meeting", "meeting_prep"}:
            suggestions.append(
                {
                    "kind": "fix",
                    "priority": "medium",
                    "title": "Classify as meeting prep",
                    "reason": "Detected meeting-oriented content but current classification does not reflect it.",
                    "proposedAction": {
                        "endpoint": f"/exceptions/feedback/{workspace_id}/{message_id}/fix",
                        "method": "POST",
                        "body": {
                            "classification": "meeting_prep",
                            "confidence": max(confidence, 0.9),
                            "note": "Auto-suggested meeting classification",
                            "operator": "suggestion-engine",
                        },
                    },
                }
            )

        if self._looks_like_promise(payload, combined) and not payload.get("ignored"):
            suggestions.append(
                {
                    "kind": "promote",
                    "priority": "medium",
                    "title": "Promote to commitment tracking",
                    "reason": "Detected promise or follow-up language that should appear in commitment tracking.",
                    "proposedAction": {
                        "endpoint": f"/exceptions/feedback/{workspace_id}/{message_id}/promote",
                        "method": "POST",
                        "body": {
                            "targetType": "commitment",
                            "note": "Auto-suggested commitment promotion",
                            "operator": "suggestion-engine",
                        },
                    },
                }
            )

        if self._looks_like_noise(payload, combined, confidence):
            suggestions.append(
                {
                    "kind": "ignore",
                    "priority": "low",
                    "title": "Ignore likely noise",
                    "reason": "Message appears informational or automated and is likely safe to suppress from the queue.",
                    "proposedAction": {
                        "endpoint": f"/exceptions/feedback/{workspace_id}/{message_id}/ignore",
                        "method": "POST",
                        "body": {
                            "note": "Auto-suggested ignore for likely noise",
                            "operator": "suggestion-engine",
                        },
                    },
                }
            )

        if confidence < self.confidence_threshold and not suggestions:
            suggestions.append(
                {
                    "kind": "review",
                    "priority": "medium",
                    "title": "Manual review recommended",
                    "reason": "Confidence is below threshold and no deterministic action could be recommended safely.",
                    "proposedAction": None,
                }
            )

        return {
            "workspaceId": workspace_id,
            "messageId": message_id,
            "classification": classification or "unclassified",
            "confidence": confidence,
            "suggestions": suggestions,
        }

    def suggest_for_workspace(self, workspace_id: str, limit: int = 25) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        with self.store.connect() as conn:
            rows = conn.execute(
                """
                SELECT messageId
                FROM EmailEvent
                WHERE workspaceId = ?
                ORDER BY updatedAt DESC, messageId ASC
                LIMIT ?
                """,
                (workspace_id, limit),
            ).fetchall()

        results = []
        for row in rows:
            result = self.suggest_for_message(workspace_id, row["messageId"])
            if result["suggestions"]:
                results.append(result)

        return {
            "workspaceId": workspace_id,
            "count": len(results),
            "items": results,
        }

    def _get_email_event(self, workspace_id: str, message_id: str) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        with self.store.connect() as conn:
            row = conn.execute(
                """
                SELECT workspaceId, messageId, subject, source, classification, confidence, payloadJson, updatedAt
                FROM EmailEvent
                WHERE workspaceId = ? AND messageId = ?
                """,
                (workspace_id, message_id),
            ).fetchone()
        if not row:
            raise ValueError(f"EmailEvent not found for {workspace_id}/{message_id}")
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
    def _extract_ticket_id(payload: dict[str, Any]) -> str | None:
        for key in ("ticketId", "ticket_id", "caseId", "incidentId"):
            value = payload.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _detect_ticket_id(text: str) -> str | None:
        snow = SN_TICKET_RE.search(text)
        if snow:
            return snow.group(0).upper()
        cw = CW_TICKET_RE.search(text)
        if cw:
            return cw.group(1)
        return None

    @staticmethod
    def _looks_like_meeting(payload: dict[str, Any], text: str) -> bool:
        if any(payload.get(key) for key in ("meetingId", "meetingTime", "startTime", "agenda")):
            return True
        lowered = text.lower()
        return any(term in lowered for term in ("meeting", "agenda", "steering committee", "prep for", "attendees"))

    @staticmethod
    def _looks_like_promise(payload: dict[str, Any], text: str) -> bool:
        if any(payload.get(key) for key in ("promise", "promiseText", "promisedDate")):
            return True
        lowered = text.lower()
        return any(term in lowered for term in ("i will", "i'll", "we will", "we'll", "follow up", "send the update"))

    @staticmethod
    def _looks_like_noise(payload: dict[str, Any], text: str, confidence: float) -> bool:
        if payload.get("ignored"):
            return False
        lowered = text.lower()
        noise_markers = (
            "newsletter",
            "unsubscribe",
            "automated",
            "no-reply",
            "notification only",
            "fyi",
        )
        return confidence < 0.5 and any(marker in lowered for marker in noise_markers)
