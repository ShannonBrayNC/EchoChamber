"""EchoChamber Ops Store

SQLite-first store with workspace isolation guardrails.
Phase 1 scope:
- Core schema bootstrap
- Workspace-bound inserts
- Idempotent upserts for EmailEvent and Artifact
- Query helpers for artifacts by workspace
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DB_PATH = Path("data/echochamber.db")


class WorkspaceRequiredError(ValueError):
    """Raised when a workspaceId is missing."""


@dataclass(frozen=True)
class EmailEventRecord:
    workspace_id: str
    message_id: str
    subject: str
    source: str = "graph"
    classification: str | None = None
    confidence: float | None = None
    payload_json: str | None = None


@dataclass(frozen=True)
class ArtifactRecord:
    workspace_id: str
    artifact_type: str
    artifact_key: str
    content_json: str
    evidence_refs_json: str


class OpsStore:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connect(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS EmailEvent (
                    workspaceId TEXT NOT NULL,
                    messageId TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    source TEXT NOT NULL,
                    classification TEXT NULL,
                    confidence REAL NULL,
                    payloadJson TEXT NULL,
                    createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (workspaceId, messageId)
                );

                CREATE TABLE IF NOT EXISTS Artifact (
                    workspaceId TEXT NOT NULL,
                    artifactType TEXT NOT NULL,
                    artifactKey TEXT NOT NULL,
                    contentJson TEXT NOT NULL,
                    evidenceRefsJson TEXT NOT NULL,
                    createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (workspaceId, artifactType, artifactKey)
                );

                CREATE TABLE IF NOT EXISTS ProcessingState (
                    workspaceId TEXT NOT NULL,
                    stateKey TEXT NOT NULL,
                    stateValue TEXT NOT NULL,
                    updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (workspaceId, stateKey)
                );
                """
            )

    @staticmethod
    def _require_workspace(workspace_id: str) -> None:
        if not workspace_id or not workspace_id.strip():
            raise WorkspaceRequiredError("workspaceId is required")

    def upsert_email_event(self, record: EmailEventRecord) -> None:
        self._require_workspace(record.workspace_id)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO EmailEvent (
                    workspaceId, messageId, subject, source, classification, confidence, payloadJson
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspaceId, messageId)
                DO UPDATE SET
                    subject = excluded.subject,
                    source = excluded.source,
                    classification = excluded.classification,
                    confidence = excluded.confidence,
                    payloadJson = excluded.payloadJson,
                    updatedAt = CURRENT_TIMESTAMP
                """,
                (
                    record.workspace_id,
                    record.message_id,
                    record.subject,
                    record.source,
                    record.classification,
                    record.confidence,
                    record.payload_json,
                ),
            )

    def upsert_artifact(self, record: ArtifactRecord) -> None:
        self._require_workspace(record.workspace_id)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO Artifact (
                    workspaceId, artifactType, artifactKey, contentJson, evidenceRefsJson
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(workspaceId, artifactType, artifactKey)
                DO UPDATE SET
                    contentJson = excluded.contentJson,
                    evidenceRefsJson = excluded.evidenceRefsJson,
                    updatedAt = CURRENT_TIMESTAMP
                """,
                (
                    record.workspace_id,
                    record.artifact_type,
                    record.artifact_key,
                    record.content_json,
                    record.evidence_refs_json,
                ),
            )

    def set_processing_state(self, workspace_id: str, state_key: str, state_value: dict[str, Any]) -> None:
        self._require_workspace(workspace_id)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO ProcessingState (workspaceId, stateKey, stateValue)
                VALUES (?, ?, ?)
                ON CONFLICT(workspaceId, stateKey)
                DO UPDATE SET stateValue = excluded.stateValue, updatedAt = CURRENT_TIMESTAMP
                """,
                (workspace_id, state_key, json.dumps(state_value)),
            )

    def get_processing_state(self, workspace_id: str, state_key: str) -> dict[str, Any] | None:
        self._require_workspace(workspace_id)
        with self.connect() as conn:
            row = conn.execute(
                "SELECT stateValue FROM ProcessingState WHERE workspaceId = ? AND stateKey = ?",
                (workspace_id, state_key),
            ).fetchone()
            return json.loads(row[0]) if row else None

    def list_artifacts(self, workspace_id: str, artifact_type: str | None = None) -> list[dict[str, Any]]:
        self._require_workspace(workspace_id)
        query = "SELECT workspaceId, artifactType, artifactKey, contentJson, evidenceRefsJson, createdAt, updatedAt FROM Artifact WHERE workspaceId = ?"
        params: list[Any] = [workspace_id]
        if artifact_type:
            query += " AND artifactType = ?"
            params.append(artifact_type)
        query += " ORDER BY updatedAt DESC"

        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
