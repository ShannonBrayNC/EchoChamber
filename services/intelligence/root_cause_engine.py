"""Root cause analysis engine for EchoChamber.

This module combines deterministic pattern analysis with optional LLM-backed
reasoning. Phase 2 behavior is safe by default:
- deterministic evidence gathering always runs
- heuristic root-cause hypotheses are always available
- LLM reasoning is optional and only augments the evidence pack
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from services.query.run_history import RunHistoryQuery
from services.intelligence.llm_reasoner import LLMReasoner


class RootCauseEngine:
    def __init__(
        self,
        history: RunHistoryQuery | None = None,
        llm_reasoner: LLMReasoner | None = None,
    ):
        self.history = history or RunHistoryQuery()
        self.llm_reasoner = llm_reasoner or LLMReasoner()

    def diagnose_workspace(self, workspace_id: str, max_runs: int = 20) -> dict[str, Any]:
        runs = self.history.list_runs(workspace_id, limit=max_runs)
        failures = [run for run in runs if run.get("status") == "failed"]
        latest_failure = failures[0] if failures else None

        evidence = self._build_evidence(workspace_id, runs, failures)
        heuristic = self._heuristic_analysis(evidence)
        llm_reasoning = self.llm_reasoner.reason_root_cause(evidence, heuristic)

        return {
            "workspaceId": workspace_id,
            "evidence": evidence,
            "heuristic": heuristic,
            "llmReasoning": llm_reasoning,
            "latestFailure": latest_failure,
        }

    def _build_evidence(
        self,
        workspace_id: str,
        runs: list[dict[str, Any]],
        failures: list[dict[str, Any]],
    ) -> dict[str, Any]:
        stages = Counter(run.get("stage", "unknown") for run in failures)
        statuses = Counter(run.get("status", "unknown") for run in runs)
        severities = Counter(
            ((run.get("details") or {}).get("severity") or "unknown")
            for run in failures
        )

        return {
            "workspaceId": workspace_id,
            "totalRuns": len(runs),
            "failedRuns": len(failures),
            "statusCounts": dict(statuses),
            "failureStages": dict(stages),
            "failureSeverities": dict(severities),
            "sampleFailureIds": [run.get("runId") for run in failures[:5]],
        }

    def _heuristic_analysis(self, evidence: dict[str, Any]) -> dict[str, Any]:
        failed_runs = evidence.get("failedRuns", 0)
        stages = evidence.get("failureStages", {})

        hypotheses: list[dict[str, str]] = []
        primary_stage = max(stages, key=stages.get) if stages else None

        if failed_runs == 0:
            hypotheses.append({
                "category": "stability",
                "confidence": "high",
                "hypothesis": "No failed runs were detected in the sampled history.",
                "recommendedAction": "Continue monitoring for replay drift and confidence degradation.",
            })
        else:
            if primary_stage == "validation":
                hypotheses.append({
                    "category": "governance",
                    "confidence": "high",
                    "hypothesis": "Validation failures dominate the workspace history, suggesting evidence, policy, or forbidden-action violations.",
                    "recommendedAction": "Inspect SecuritySentry checks, evidenceRefs population, and replay diffs for the last failed runs.",
                })
            elif primary_stage == "ingestion":
                hypotheses.append({
                    "category": "data_pipeline",
                    "confidence": "medium",
                    "hypothesis": "Ingestion appears to be the most failure-prone stage, suggesting malformed inputs or state progression issues.",
                    "recommendedAction": "Compare ProcessingState transitions and sample input payloads across the latest success/failure boundary.",
                })
            else:
                hypotheses.append({
                    "category": "general",
                    "confidence": "medium",
                    "hypothesis": "Failures are present without a single dominant stage, indicating cross-cutting instability or mixed failure modes.",
                    "recommendedAction": "Group recent failures by stage and compare the latest failed run to the latest successful run.",
                })

            if failed_runs >= 3:
                hypotheses.append({
                    "category": "trend",
                    "confidence": "medium",
                    "hypothesis": "The workspace shows repeated failures rather than isolated noise.",
                    "recommendedAction": "Run a replay batch and review diff intelligence severity for each replay result.",
                })

        return {
            "primaryStage": primary_stage,
            "hypotheses": hypotheses,
        }
