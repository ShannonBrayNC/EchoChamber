"""Auto-apply safe learned fixes for EchoChamber.

Uses learned pattern indices and existing exception feedback routes to
automatically apply low-risk fixes when confidence is high enough.
"""

from __future__ import annotations

import json
from typing import Any

from services.intelligence.fix_learning import FixLearningService
from services.intelligence.exception_feedback_loop import ExceptionFeedbackLoopService
from services.store.ops_store import OpsStore


SAFE_CLASSIFICATIONS = {"ticket_update", "meeting_prep", "meeting", "other"}
DEFAULT_MIN_SCORE = 2
DEFAULT_MIN_MATCH_CONFIDENCE = 0.92


class AutoApplyLearningService:
    def __init__(self, store: OpsStore | None = None) -> None:
        self.store = store or OpsStore()
        self.learning = FixLearningService(self.store)
        self.feedback = ExceptionFeedbackLoopService(self.store)

    def auto_apply_for_message(
        self,
        workspace_id: str,
        message_id: str,
        min_score: int = DEFAULT_MIN_SCORE,
        min_match_confidence: float = DEFAULT_MIN_MATCH_CONFIDENCE,
    ) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        email = self._get_email_event(workspace_id, message_id)
        learned = self.learning.suggest_from_learning(workspace_id, message_id)
        recommended_classification = learned.get("recommendedClassification")
        payload_patch = learned.get("recommendedPayloadPatch") or {}
        matches = learned.get("learnedMatches") or []
        best = matches[0] if matches else None

        current_confidence = float(email.get("confidence") or 0.0)
        if not best:
            return self._result("skipped", "No learned pattern match found.", workspace_id, message_id, None)

        if best.get("score", 0) < min_score:
            return self._result("skipped", "Learned match score below safe threshold.", workspace_id, message_id, best)

        if recommended_classification not in SAFE_CLASSIFICATIONS:
            return self._result("skipped", f"Classification {recommended_classification!r} is not in safe auto-apply allowlist.", workspace_id, message_id, best)

        if current_confidence >= min_match_confidence:
            return self._result("skipped", "Current message confidence is already high enough; no auto-fix needed.", workspace_id, message_id, best)

        auto_confidence = min(0.99, max(min_match_confidence, 0.90 + (best.get("score", 0) * 0.01)))

        applied = self.feedback.fix_and_refresh(
            workspace_id=workspace_id,
            message_id=message_id,
            classification=recommended_classification,
            confidence=auto_confidence,
            payload_patch=payload_patch,
            note="Auto-applied safe learned fix",
            operator="auto-learning",
        )

        self.store.upsert_artifact(
            self._artifact_record(
                workspace_id=workspace_id,
                message_id=message_id,
                result={
                    "status": "applied",
                    "message": "Safe learned fix auto-applied.",
                    "workspaceId": workspace_id,
                    "messageId": message_id,
                    "recommendedClassification": recommended_classification,
                    "payloadPatch": payload_patch,
                    "match": best,
                    "applied": applied,
                },
            )
        )

        return {
            "status": "applied",
            "workspaceId": workspace_id,
            "messageId": message_id,
            "recommendedClassification": recommended_classification,
            "payloadPatch": payload_patch,
            "match": best,
            "applied": applied,
        }

    def auto_apply_for_workspace(
        self,
        workspace_id: str,
        limit: int = 25,
        min_score: int = DEFAULT_MIN_SCORE,
        min_match_confidence: float = DEFAULT_MIN_MATCH_CONFIDENCE,
    ) -> dict[str, Any]:
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
            try:
                results.append(
                    self.auto_apply_for_message(
                        workspace_id=workspace_id,
                        message_id=row["messageId"],
                        min_score=min_score,
                        min_match_confidence=min_match_confidence,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "status": "error",
                        "workspaceId": workspace_id,
                        "messageId": row["messageId"],
                        "message": str(exc),
                    }
                )

        applied = sum(1 for r in results if r.get("status") == "applied")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        errors = sum(1 for r in results if r.get("status") == "error")

        return {
            "workspaceId": workspace_id,
            "counts": {
                "evaluated": len(results),
                "applied": applied,
                "skipped": skipped,
                "errors": errors,
            },
            "results": results,
        }

    def _get_email_event(self, workspace_id: str, message_id: str) -> dict[str, Any]:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT workspaceId, messageId, subject, classification, confidence, payloadJson FROM EmailEvent WHERE workspaceId = ? AND messageId = ?",
                (workspace_id, message_id),
            ).fetchone()
        if not row:
            raise ValueError(f"EmailEvent not found for {workspace_id}/{message_id}")
        return dict(row)

    def _artifact_record(self, workspace_id: str, message_id: str, result: dict[str, Any]):
        from services.store.ops_store import ArtifactRecord

        return ArtifactRecord(
            workspace_id=workspace_id,
            artifact_type="AutoAppliedFix",
            artifact_key=f"auto:{message_id}",
            content_json=json.dumps(result),
            evidence_refs_json=json.dumps([
                {"type": "EmailEvent", "messageId": message_id},
                {"type": "LearnedPatternIndex", "workspaceId": workspace_id},
            ]),
        )

    @staticmethod
    def _result(status: str, message: str, workspace_id: str, message_id: str, match: dict[str, Any] | None) -> dict[str, Any]:
        return {
            "status": status,
            "message": message,
            "workspaceId": workspace_id,
            "messageId": message_id,
            "match": match,
        }
