"""Auto-learning from operator fixes for EchoChamber.

This service turns ExceptionFix artifacts into lightweight learned patterns that
can influence future suggestions without requiring model retraining.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

from services.store.ops_store import ArtifactRecord, OpsStore

TOKEN_RE = re.compile(r"[A-Za-z0-9#_-]{3,}")
TICKET_RE = re.compile(r"\b(?:INC|REQ|RITM|CHG|TASK)\d{4,10}|\d{5,8}\b", re.IGNORECASE)
STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "have", "will", "please",
    "need", "next", "follow", "update", "customer", "message", "email", "about", "into",
}


class FixLearningService:
    def __init__(self, store: OpsStore | None = None) -> None:
        self.store = store or OpsStore()

    def learn_from_fix(
        self,
        workspace_id: str,
        message_id: str,
        min_token_occurrences: int = 1,
    ) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        fix = self._get_latest_fix_artifact(workspace_id, message_id)
        email = self._get_email_event(workspace_id, message_id)

        classification = fix.get("classification") or email.get("classification") or "other"
        payload_patch = fix.get("payloadPatch") or {}
        subject = email.get("subject") or ""
        payload = self._safe_json_loads(email.get("payloadJson"))
        snippet = str(payload.get("snippet") or payload.get("summary") or "")
        combined = f"{subject} {snippet}"

        tokens = [t.lower() for t in TOKEN_RE.findall(combined) if t.lower() not in STOPWORDS]
        token_counts = Counter(tokens)
        learned_tokens = sorted([t for t, c in token_counts.items() if c >= min_token_occurrences])[:20]

        ticket_matches = sorted({m.upper() for m in TICKET_RE.findall(combined)})
        learned_pattern = {
            "workspaceId": workspace_id,
            "messageId": message_id,
            "classification": classification,
            "tokens": learned_tokens,
            "ticketHints": ticket_matches,
            "payloadPatch": payload_patch,
            "sourceSubject": subject,
            "learnedAt": self._utcnow(),
        }

        artifact_key = f"pattern:{classification}:{message_id}"
        self.store.upsert_artifact(
            ArtifactRecord(
                workspace_id=workspace_id,
                artifact_type="LearnedPattern",
                artifact_key=artifact_key,
                content_json=json.dumps(learned_pattern),
                evidence_refs_json=json.dumps([
                    {"type": "EmailEvent", "messageId": message_id, "subject": subject},
                    {"type": "ExceptionFix", "messageId": message_id},
                ]),
            )
        )

        return {
            "status": "ok",
            "workspaceId": workspace_id,
            "messageId": message_id,
            "classification": classification,
            "artifactKey": artifact_key,
            "learnedTokens": learned_tokens,
            "ticketHints": ticket_matches,
        }

    def rebuild_workspace_index(self, workspace_id: str) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        fixes = self._list_fix_artifacts(workspace_id)
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for fix in fixes:
            classification = (fix.get("classification") or "other").strip().lower() or "other"
            grouped[classification].append(fix)

        summaries = []
        for classification, items in grouped.items():
            token_counter: Counter[str] = Counter()
            payload_examples: list[dict[str, Any]] = []
            for item in items:
                message_id = item.get("messageId")
                email = self._get_email_event(workspace_id, message_id)
                payload = self._safe_json_loads(email.get("payloadJson"))
                snippet = str(payload.get("snippet") or payload.get("summary") or "")
                combined = f"{email.get('subject') or ''} {snippet}"
                token_counter.update(
                    t.lower()
                    for t in TOKEN_RE.findall(combined)
                    if t.lower() not in STOPWORDS
                )
                if item.get("payloadPatch"):
                    payload_examples.append(item["payloadPatch"])

            summary = {
                "workspaceId": workspace_id,
                "classification": classification,
                "sampleCount": len(items),
                "topTokens": [t for t, _ in token_counter.most_common(15)],
                "payloadExamples": payload_examples[:5],
                "rebuiltAt": self._utcnow(),
            }
            artifact_key = f"index:{classification}"
            self.store.upsert_artifact(
                ArtifactRecord(
                    workspace_id=workspace_id,
                    artifact_type="LearnedPatternIndex",
                    artifact_key=artifact_key,
                    content_json=json.dumps(summary),
                    evidence_refs_json=json.dumps([{ "type": "ExceptionFix", "classification": classification }]),
                )
            )
            summaries.append(summary)

        return {
            "status": "ok",
            "workspaceId": workspace_id,
            "indexCount": len(summaries),
            "indices": summaries,
        }

    def suggest_from_learning(self, workspace_id: str, message_id: str) -> dict[str, Any]:
        self.store._require_workspace(workspace_id)
        email = self._get_email_event(workspace_id, message_id)
        payload = self._safe_json_loads(email.get("payloadJson"))
        snippet = str(payload.get("snippet") or payload.get("summary") or "")
        combined = f"{email.get('subject') or ''} {snippet}"
        message_tokens = {t.lower() for t in TOKEN_RE.findall(combined) if t.lower() not in STOPWORDS}

        indices = self._list_pattern_indices(workspace_id)
        matches = []
        for idx in indices:
            tokens = set((idx.get("topTokens") or [])[:10])
            overlap = sorted(message_tokens.intersection(tokens))
            if not overlap:
                continue
            score = len(overlap)
            classification = idx.get("classification") or "other"
            matches.append(
                {
                    "classification": classification,
                    "score": score,
                    "overlap": overlap,
                    "payloadExamples": idx.get("payloadExamples") or [],
                }
            )

        matches.sort(key=lambda x: (-x["score"], x["classification"]))
        best = matches[0] if matches else None

        return {
            "workspaceId": workspace_id,
            "messageId": message_id,
            "learnedMatches": matches[:5],
            "recommendedClassification": best["classification"] if best else None,
            "recommendedPayloadPatch": (best["payloadExamples"][0] if best and best["payloadExamples"] else {}),
        }

    def _get_latest_fix_artifact(self, workspace_id: str, message_id: str) -> dict[str, Any]:
        fixes = [f for f in self._list_fix_artifacts(workspace_id) if f.get("messageId") == message_id]
        if not fixes:
            raise ValueError(f"No ExceptionFix artifact found for {workspace_id}/{message_id}")
        fixes.sort(key=lambda x: x.get("fixedAt") or "", reverse=True)
        return fixes[0]

    def _list_fix_artifacts(self, workspace_id: str) -> list[dict[str, Any]]:
        artifacts = self.store.list_artifacts(workspace_id, artifact_type="ExceptionFix")
        results = []
        for artifact in artifacts:
            payload = self._safe_json_loads(artifact.get("contentJson"))
            if payload:
                results.append(payload)
        return results

    def _list_pattern_indices(self, workspace_id: str) -> list[dict[str, Any]]:
        artifacts = self.store.list_artifacts(workspace_id, artifact_type="LearnedPatternIndex")
        results = []
        for artifact in artifacts:
            payload = self._safe_json_loads(artifact.get("contentJson"))
            if payload:
                results.append(payload)
        return results

    def _get_email_event(self, workspace_id: str, message_id: str) -> dict[str, Any]:
        with self.store.connect() as conn:
            row = conn.execute(
                "SELECT workspaceId, messageId, subject, classification, confidence, payloadJson FROM EmailEvent WHERE workspaceId = ? AND messageId = ?",
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
    def _utcnow() -> str:
        return datetime.now(UTC).isoformat()
