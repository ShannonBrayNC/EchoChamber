"""Inbox Intelligence service for EchoChamber.

Provides coverage metrics, exception candidates, and drill-down over EmailEvent
records already stored in the Ops Store.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from services.store.ops_store import OpsStore


class InboxIntelligenceService:
    def __init__(self, store: OpsStore | None = None, confidence_threshold: float = 0.80) -> None:
        self.store = store or OpsStore()
        self.confidence_threshold = confidence_threshold

    def get_workspace_snapshot(self, workspace_id: str) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        rows = self._email_rows(workspace_id)
        artifacts = self.store.list_artifacts(workspace_id)
        runway_artifacts = [a for a in artifacts if a["artifactType"] == "Runway"]
        execution_logs = [a for a in artifacts if a["artifactType"] == "ExecutionLog"]

        exceptions = self._build_exceptions(rows)
        coverage = self._build_coverage(rows, exceptions)
        buckets = self._build_classification_buckets(rows)
        timeline = self._build_timeline(rows)

        return {
            "workspaceId": workspace_id,
            "coverage": coverage,
            "exceptions": exceptions,
            "classificationBuckets": buckets,
            "timeline": timeline,
            "artifacts": {
                "runwayCount": len(runway_artifacts),
                "executionLogCount": len(execution_logs),
            },
        }

    def _email_rows(self, workspace_id: str) -> list[dict[str, Any]]:
        with self.store.connect() as conn:
            rows = conn.execute(
                """
                SELECT workspaceId, messageId, subject, source, classification, confidence, payloadJson, createdAt, updatedAt
                FROM EmailEvent
                WHERE workspaceId = ?
                ORDER BY updatedAt DESC, messageId ASC
                """,
                (workspace_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def _build_coverage(self, rows: list[dict[str, Any]], exceptions: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(rows)
        classified = sum(1 for row in rows if row.get("classification"))
        high_confidence = sum(1 for row in rows if (row.get("confidence") or 0) >= self.confidence_threshold)
        covered = total - len(exceptions)
        coverage_percent = round((covered / total) * 100, 1) if total else 100.0

        return {
            "totalMessages": total,
            "classifiedMessages": classified,
            "highConfidenceMessages": high_confidence,
            "exceptionCount": len(exceptions),
            "coveredMessages": covered,
            "coveragePercent": coverage_percent,
            "confidenceThreshold": self.confidence_threshold,
        }

    def _build_exceptions(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        exceptions: list[dict[str, Any]] = []

        for row in rows:
            payload = self._safe_json_loads(row.get("payloadJson"))
            classification = (row.get("classification") or "").strip().lower()
            confidence = float(row.get("confidence") or 0.0)
            reasons: list[str] = []

            if not classification:
                reasons.append("Missing classification")
            elif classification == "other":
                reasons.append("Generic classification needs review")

            if confidence < self.confidence_threshold:
                reasons.append(f"Confidence below threshold ({confidence:.2f})")

            if classification in {"ticket_update", "ticket", "case_update"} and not self._extract_ticket_id(payload):
                reasons.append("Ticket message missing ticket identifier")

            if classification in {"meeting_prep", "meeting"} and not any(payload.get(k) for k in ("meetingId", "meetingTime", "startTime")):
                reasons.append("Meeting message missing meeting metadata")

            if reasons:
                exceptions.append(
                    {
                        "messageId": row["messageId"],
                        "subject": row["subject"],
                        "classification": row.get("classification") or "unclassified",
                        "confidence": confidence,
                        "updatedAt": row.get("updatedAt"),
                        "reasons": reasons,
                        "payloadPreview": payload,
                    }
                )

        return exceptions

    def _build_classification_buckets(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for row in rows:
            key = (row.get("classification") or "unclassified").strip().lower() or "unclassified"
            counts[key] = counts.get(key, 0) + 1

        return [
            {"classification": key, "count": counts[key]}
            for key in sorted(counts.keys(), key=lambda x: (-counts[x], x))
        ]

    def _build_timeline(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        days: dict[str, int] = {}
        for row in rows:
            updated_at = self._parse_dt(row.get("updatedAt"))
            if not updated_at:
                continue
            day_key = updated_at.astimezone(UTC).strftime("%Y-%m-%d")
            days[day_key] = days.get(day_key, 0) + 1

        return [
            {"date": day, "messages": days[day]}
            for day in sorted(days.keys())[-7:]
        ]

    @staticmethod
    def _extract_ticket_id(payload: dict[str, Any]) -> str | None:
        for key in ("ticketId", "ticket_id", "caseId", "incidentId"):
            value = payload.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _safe_json_loads(value: str | None) -> dict[str, Any]:
        if not value:
            return {}
        try:
            data = json.loads(value)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=UTC)
            return dt.astimezone(UTC)
        except ValueError:
            return None
