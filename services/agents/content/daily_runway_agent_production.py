"""Production Daily Runway Agent for EchoChamber.

Generates a workspace-scoped daily execution plan from stored operational data.
Compatible with the current scaffolded SQLite store.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from services.store.ops_store import ArtifactRecord, OpsStore, WorkspaceRequiredError

DEFAULT_STALE_HOURS = 48
DEFAULT_RUNWAY_LIMIT = 25


@dataclass(frozen=True)
class RunwayItem:
    workspace_id: str
    item_id: str
    title: str
    category: str
    priority: str
    score: int
    status: str
    due_at: str | None
    source_type: str
    source_key: str
    rationale: list[str]
    evidence_refs: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspaceId": self.workspace_id,
            "itemId": self.item_id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "score": self.score,
            "status": self.status,
            "dueAt": self.due_at,
            "sourceType": self.source_type,
            "sourceKey": self.source_key,
            "rationale": self.rationale,
            "evidenceRefs": self.evidence_refs,
        }


class DailyRunwayAgent:
    def __init__(
        self,
        store: OpsStore | None = None,
        stale_hours: int = DEFAULT_STALE_HOURS,
        runway_limit: int = DEFAULT_RUNWAY_LIMIT,
    ) -> None:
        self.store = store or OpsStore()
        self.stale_hours = stale_hours
        self.runway_limit = runway_limit

    def generate(self, workspace_id: str) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        candidates: list[RunwayItem] = []
        candidates.extend(self._derive_from_email_events(workspace_id))
        candidates.extend(self._derive_from_artifacts(workspace_id))
        deduped = self._dedupe_items(candidates)
        ordered = self._sort_items(deduped)[: self.runway_limit]
        generated_at = datetime.now(UTC).isoformat()
        artifact_key = datetime.now(UTC).strftime("%Y%m%d")

        payload = {
            "artifactType": "Runway",
            "workspaceId": workspace_id,
            "generatedAt": generated_at,
            "counts": {
                "candidateCount": len(candidates),
                "finalCount": len(ordered),
            },
            "items": [item.to_dict() for item in ordered],
        }

        evidence_refs = self._collect_runway_evidence(ordered)
        self.store.upsert_artifact(
            ArtifactRecord(
                workspace_id=workspace_id,
                artifact_type="Runway",
                artifact_key=artifact_key,
                content_json=json.dumps(payload),
                evidence_refs_json=json.dumps(evidence_refs),
            )
        )
        return payload

    def _derive_from_email_events(self, workspace_id: str) -> list[RunwayItem]:
        rows = self._query_rows(
            """
            SELECT workspaceId, messageId, subject, source, classification, confidence, payloadJson, createdAt, updatedAt
            FROM EmailEvent
            WHERE workspaceId = ?
            ORDER BY updatedAt DESC, messageId ASC
            """,
            [workspace_id],
        )
        items: list[RunwayItem] = []
        now = datetime.now(UTC)
        for row in rows:
            payload = self._safe_json_loads(row["payloadJson"])
            subject = row["subject"] or "Untitled email"
            classification = (row["classification"] or "other").lower()
            confidence = float(row["confidence"]) if row["confidence"] is not None else 0.0
            updated_at = self._parse_dt(row["updatedAt"])
            age_hours = self._hours_since(updated_at, now)
            evidence = [{
                "type": "EmailEvent",
                "messageId": row["messageId"],
                "subject": subject,
                "source": row["source"],
            }]
            ticket_id = self._first_nonempty(
                payload.get("ticketId"),
                payload.get("ticket_id"),
                payload.get("caseId"),
                payload.get("incidentId"),
            )
            if classification in {"ticket_update", "ticket", "case_update"}:
                items.append(
                    self._build_ticket_item(
                        workspace_id=workspace_id,
                        message_id=row["messageId"],
                        subject=subject,
                        payload=payload,
                        confidence=confidence,
                        ticket_id=ticket_id or row["messageId"],
                        age_hours=age_hours,
                        evidence=evidence,
                    )
                )
                continue
            if classification in {"meeting_prep", "meeting"}:
                items.append(
                    self._build_meeting_item(
                        workspace_id=workspace_id,
                        message_id=row["messageId"],
                        subject=subject,
                        payload=payload,
                        age_hours=age_hours,
                        evidence=evidence,
                    )
                )
                continue
            if self._looks_like_promise(payload, subject):
                items.append(
                    self._build_commitment_item(
                        workspace_id=workspace_id,
                        message_id=row["messageId"],
                        subject=subject,
                        payload=payload,
                        evidence=evidence,
                    )
                )
                continue
            if self._looks_like_action_request(payload, subject):
                items.append(
                    self._build_action_item(
                        workspace_id=workspace_id,
                        message_id=row["messageId"],
                        subject=subject,
                        payload=payload,
                        confidence=confidence,
                        age_hours=age_hours,
                        evidence=evidence,
                    )
                )
        return items

    def _derive_from_artifacts(self, workspace_id: str) -> list[RunwayItem]:
        rows = self._query_rows(
            """
            SELECT workspaceId, artifactType, artifactKey, contentJson, evidenceRefsJson, createdAt, updatedAt
            FROM Artifact
            WHERE workspaceId = ?
              AND artifactType IN ('ExecutionLog', 'MeetingPrep', 'CustomerBrief')
            ORDER BY updatedAt DESC, artifactType ASC, artifactKey ASC
            """,
            [workspace_id],
        )
        items: list[RunwayItem] = []
        for row in rows:
            artifact_type = row["artifactType"]
            content = self._safe_json_loads(row["contentJson"])
            evidence_refs = self._safe_json_loads(row["evidenceRefsJson"], [])
            if artifact_type == "ExecutionLog":
                details = content.get("details", {})
                if details.get("status") == "failed" or content.get("status") == "failed":
                    items.append(
                        RunwayItem(
                            workspace_id=workspace_id,
                            item_id=f"runfix:{row['artifactKey']}",
                            title=f"Investigate failed run {row['artifactKey']}",
                            category="platform",
                            priority="high",
                            score=88,
                            status="open",
                            due_at=None,
                            source_type="ExecutionLog",
                            source_key=row["artifactKey"],
                            rationale=[
                                "Recent orchestration run recorded failure state.",
                                "Platform instability blocks downstream brief generation.",
                            ],
                            evidence_refs=evidence_refs,
                        )
                    )
            if artifact_type == "MeetingPrep":
                meeting_title = content.get("title") or f"Meeting {row['artifactKey']}"
                due_at = content.get("time") or content.get("startTime")
                items.append(
                    RunwayItem(
                        workspace_id=workspace_id,
                        item_id=f"prep:{row['artifactKey']}",
                        title=f"Review prep brief for {meeting_title}",
                        category="meeting",
                        priority="medium",
                        score=70,
                        status="open",
                        due_at=due_at,
                        source_type="MeetingPrep",
                        source_key=row["artifactKey"],
                        rationale=["Prep artifact exists and should be reviewed before the meeting."],
                        evidence_refs=evidence_refs,
                    )
                )
        return items

    def _build_ticket_item(self, workspace_id: str, message_id: str, subject: str, payload: dict[str, Any], confidence: float, ticket_id: str, age_hours: int, evidence: list[dict[str, Any]]) -> RunwayItem:
        rationale: list[str] = []
        score = 40
        priority_text = str(payload.get("priority") or payload.get("severity") or "").lower()
        status_text = str(payload.get("status") or "").lower()
        snippet = str(payload.get("snippet") or payload.get("summary") or "").lower()
        if "critical" in priority_text or "sev1" in priority_text or "urgent" in priority_text:
            score += 35
            rationale.append("Ticket carries critical or urgent priority.")
        if any(word in snippet for word in ("blocked", "outage", "down", "escalation")):
            score += 25
            rationale.append("Message content signals elevated operational risk.")
        if age_hours >= self.stale_hours:
            score += 20
            rationale.append(f"Ticket appears stale at ~{age_hours} hours since last update.")
        if confidence < 0.80:
            score -= 10
            rationale.append("Classification confidence is lower than target threshold.")
        if "waiting on customer" in status_text:
            score -= 8
            rationale.append("Status indicates partial external dependency.")
        if not rationale:
            rationale.append("Open ticket activity requires a next-step review.")
        return RunwayItem(
            workspace_id=workspace_id,
            item_id=f"ticket:{ticket_id}",
            title=f"Advance ticket {ticket_id}: {subject}",
            category="ticket",
            priority=self._priority_from_score(score),
            score=score,
            status="open",
            due_at=self._extract_due_at(payload),
            source_type="EmailEvent",
            source_key=message_id,
            rationale=rationale,
            evidence_refs=evidence,
        )

    def _build_meeting_item(self, workspace_id: str, message_id: str, subject: str, payload: dict[str, Any], age_hours: int, evidence: list[dict[str, Any]]) -> RunwayItem:
        agenda = payload.get("agenda") or []
        due_at = self._extract_due_at(payload)
        score = 62
        rationale = ["Upcoming meeting requires preparation."]
        if agenda:
            rationale.append(f"Agenda includes {len(agenda)} tracked topics.")
            score += min(len(agenda) * 4, 12)
        if age_hours < 24:
            score += 8
            rationale.append("Meeting-related signal is recent and timely.")
        return RunwayItem(
            workspace_id=workspace_id,
            item_id=f"meeting:{message_id}",
            title=f"Prepare for meeting: {subject}",
            category="meeting",
            priority=self._priority_from_score(score),
            score=score,
            status="open",
            due_at=due_at,
            source_type="EmailEvent",
            source_key=message_id,
            rationale=rationale,
            evidence_refs=evidence,
        )

    def _build_commitment_item(self, workspace_id: str, message_id: str, subject: str, payload: dict[str, Any], evidence: list[dict[str, Any]]) -> RunwayItem:
        due_at = self._extract_due_at(payload)
        score = 72
        rationale = ["Detected probable promise or commitment that needs follow-through."]
        if due_at:
            due_dt = self._parse_dt(due_at)
            if due_dt:
                now = datetime.now(UTC)
                if due_dt <= now:
                    score += 20
                    rationale.append("Commitment appears overdue.")
                elif due_dt <= now + timedelta(days=1):
                    score += 12
                    rationale.append("Commitment due within 24 hours.")
        promise_text = self._first_nonempty(
            payload.get("promise"),
            payload.get("promiseText"),
            payload.get("summary"),
            subject,
        )
        return RunwayItem(
            workspace_id=workspace_id,
            item_id=f"commitment:{message_id}",
            title=f"Deliver promised follow-up: {promise_text}",
            category="commitment",
            priority=self._priority_from_score(score),
            score=score,
            status="open",
            due_at=due_at,
            source_type="EmailEvent",
            source_key=message_id,
            rationale=rationale,
            evidence_refs=evidence,
        )

    def _build_action_item(self, workspace_id: str, message_id: str, subject: str, payload: dict[str, Any], confidence: float, age_hours: int, evidence: list[dict[str, Any]]) -> RunwayItem:
        score = 55
        rationale = ["Detected direct ask or pending next action from email content."]
        if age_hours >= 24:
            score += 10
            rationale.append("Request has aged beyond one day.")
        if confidence >= 0.9:
            score += 5
            rationale.append("Signal confidence is strong.")
        else:
            score -= 5
            rationale.append("Signal confidence is moderate and should be reviewed.")
        next_action = self._first_nonempty(
            payload.get("ask"),
            payload.get("nextAction"),
            payload.get("snippet"),
            subject,
        )
        return RunwayItem(
            workspace_id=workspace_id,
            item_id=f"action:{message_id}",
            title=f"Respond to ask: {next_action}",
            category="action",
            priority=self._priority_from_score(score),
            score=score,
            status="open",
            due_at=self._extract_due_at(payload),
            source_type="EmailEvent",
            source_key=message_id,
            rationale=rationale,
            evidence_refs=evidence,
        )

    def _dedupe_items(self, items: list[RunwayItem]) -> list[RunwayItem]:
        best_by_id: dict[str, RunwayItem] = {}
        for item in items:
            current = best_by_id.get(item.item_id)
            if current is None or item.score > current.score:
                best_by_id[item.item_id] = item
                continue
            if current.score == item.score and (item.due_at or "") < (current.due_at or ""):
                best_by_id[item.item_id] = item
        return list(best_by_id.values())

    def _sort_items(self, items: list[RunwayItem]) -> list[RunwayItem]:
        def key(item: RunwayItem) -> tuple[Any, ...]:
            due_sort = item.due_at or "9999-12-31T23:59:59+00:00"
            return (-item.score, due_sort, item.category, item.title.lower(), item.item_id)
        return sorted(items, key=key)

    def _collect_runway_evidence(self, items: list[RunwayItem]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        collected: list[dict[str, Any]] = []
        for item in items:
            for ref in item.evidence_refs:
                key = json.dumps(ref, sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
                collected.append(ref)
        return collected

    def _query_rows(self, sql: str, params: list[Any]) -> list[sqlite3.Row]:
        with self.store.connect() as conn:
            return conn.execute(sql, params).fetchall()

    @staticmethod
    def _priority_from_score(score: int) -> str:
        if score >= 90:
            return "critical"
        if score >= 75:
            return "high"
        if score >= 60:
            return "medium"
        return "low"

    @staticmethod
    def _safe_json_loads(value: str | None, default: Any | None = None) -> Any:
        if value is None or value == "":
            return default if default is not None else {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default if default is not None else {}

    @staticmethod
    def _first_nonempty(*values: Any) -> str | None:
        for value in values:
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return None

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

    @staticmethod
    def _hours_since(value: datetime | None, now: datetime) -> int:
        if value is None:
            return 999999
        return int((now - value).total_seconds() // 3600)

    @staticmethod
    def _extract_due_at(payload: dict[str, Any]) -> str | None:
        for key in ("dueAt", "dueDate", "promisedDate", "deadline", "meetingTime", "startTime"):
            value = payload.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _looks_like_promise(payload: dict[str, Any], subject: str) -> bool:
        promise_fields = ("promise", "promiseText", "promisedDate")
        if any(payload.get(field) for field in promise_fields):
            return True
        combined = f"{subject} {payload.get('snippet', '')}".lower()
        return any(phrase in combined for phrase in (
            "i will",
            "i'll",
            "we will",
            "we'll",
            "promised",
            "follow up tomorrow",
            "send the update",
        ))

    @staticmethod
    def _looks_like_action_request(payload: dict[str, Any], subject: str) -> bool:
        if payload.get("ask") or payload.get("nextAction"):
            return True
        combined = f"{subject} {payload.get('snippet', '')}".lower()
        return any(phrase in combined for phrase in (
            "please",
            "can you",
            "need you to",
            "confirm",
            "review",
            "next step",
        ))


def generate_runway(workspace_id: str, store: OpsStore | None = None) -> dict[str, Any]:
    return DailyRunwayAgent(store=store).generate(workspace_id)


if __name__ == "__main__":
    try:
        print(json.dumps(generate_runway("default"), indent=2))
    except WorkspaceRequiredError as exc:
        raise SystemExit(str(exc))
