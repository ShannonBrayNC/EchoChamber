"""Adaptive intelligence layer for EchoChamber.

Analyzes historical execution runs to identify recurring failure patterns and
produce actionable suggestions for operators.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from services.query.run_history import RunHistoryQuery


class AdaptiveAdvisor:
    def __init__(self, history: RunHistoryQuery | None = None):
        self.history = history or RunHistoryQuery()

    def analyze_workspace(self, workspace_id: str) -> dict[str, Any]:
        runs = self.history.list_runs(workspace_id, limit=None)
        failures = [run for run in runs if run.get("status") == "failed"]

        stage_counts = Counter(run.get("stage", "unknown") for run in failures)
        recurring = [
            {"stage": stage, "count": count}
            for stage, count in stage_counts.items()
            if count >= 2
        ]

        suggestions = self._build_suggestions(failures, recurring)

        return {
            "workspaceId": workspace_id,
            "totalRuns": len(runs),
            "failedRuns": len(failures),
            "recurringFailures": recurring,
            "suggestions": suggestions,
            "health": self._classify_health(len(runs), len(failures)),
        }

    def _build_suggestions(
        self,
        failures: list[dict[str, Any]],
        recurring: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        suggestions: list[dict[str, str]] = []

        if not failures:
            suggestions.append({
                "type": "stability",
                "message": "No failures detected. Continue monitoring replay drift and validation trends.",
            })
            return suggestions

        if recurring:
            for item in recurring:
                stage = item["stage"]
                suggestions.append({
                    "type": "recurring_failure",
                    "message": f"Recurring failures detected in stage '{stage}'. Review validation artifacts and replay diffs for that stage first.",
                })

        if any(run.get("stage") == "validation" for run in failures):
            suggestions.append({
                "type": "governance",
                "message": "Validation-stage failures are present. Inspect SecuritySentry checks, evidence refs, and forbidden action requests.",
            })

        if len(failures) >= 3:
            suggestions.append({
                "type": "operational",
                "message": "Multiple failures detected. Schedule an automated replay batch and compare diff severity across recent runs.",
            })

        if not suggestions:
            suggestions.append({
                "type": "triage",
                "message": "Review the latest failed run and compare it against the last successful run to isolate the change boundary.",
            })

        return suggestions

    @staticmethod
    def _classify_health(total_runs: int, failed_runs: int) -> str:
        if total_runs == 0:
            return "unknown"
        ratio = failed_runs / total_runs
        if ratio == 0:
            return "healthy"
        if ratio <= 0.25:
            return "watch"
        return "critical"
