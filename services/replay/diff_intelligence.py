"""Diff intelligence layer for EchoChamber Phase 2.

Provides structured, UI-friendly comparison summaries for replay results.
The goal is to move beyond raw key/value differences into categories that help
operators understand what changed and why it matters.
"""

from __future__ import annotations

from typing import Any


class DiffIntelligence:
    @staticmethod
    def summarize_diff(diff: dict[str, Any]) -> dict[str, Any]:
        changed_keys = sorted(diff.keys())
        severity = DiffIntelligence.classify_severity(changed_keys)

        return {
            "changed": bool(changed_keys),
            "changedKeys": changed_keys,
            "changeCount": len(changed_keys),
            "severity": severity,
            "summary": DiffIntelligence.build_summary(changed_keys, severity),
            "categories": DiffIntelligence.categorize_changes(diff),
        }

    @staticmethod
    def categorize_changes(diff: dict[str, Any]) -> dict[str, list[str]]:
        categories: dict[str, list[str]] = {
            "status": [],
            "timing": [],
            "artifacts": [],
            "validation": [],
            "data": [],
            "other": [],
        }

        for key in diff.keys():
            lower = key.lower()
            if "status" in lower or key == "stage":
                categories["status"].append(key)
            elif "time" in lower or "recorded" in lower or "created" in lower or "updated" in lower:
                categories["timing"].append(key)
            elif "artifact" in lower or "runway" in lower:
                categories["artifacts"].append(key)
            elif "validation" in lower or "check" in lower:
                categories["validation"].append(key)
            elif key in {"details", "ingestion", "processed", "count"}:
                categories["data"].append(key)
            else:
                categories["other"].append(key)

        return {k: v for k, v in categories.items() if v}

    @staticmethod
    def classify_severity(changed_keys: list[str]) -> str:
        if not changed_keys:
            return "none"

        high_impact = {"status", "validation", "workspaceId"}
        medium_impact = {"runway", "ingestion", "details", "stage"}

        if any(key in high_impact for key in changed_keys):
            return "high"
        if any(key in medium_impact for key in changed_keys):
            return "medium"
        return "low"

    @staticmethod
    def build_summary(changed_keys: list[str], severity: str) -> str:
        if not changed_keys:
            return "Replay matched the original run."

        keys = ", ".join(changed_keys[:5])
        if len(changed_keys) > 5:
            keys += ", ..."
        return f"Replay differs from the original run in {len(changed_keys)} field(s): {keys}. Severity: {severity}."
