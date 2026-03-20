"""LLM Reasoner (safe stub for Phase 2).

This module provides an optional reasoning layer. In Phase 2:
- No external calls are required
- The reasoning is simulated / structured
- Can later plug into OpenAI / Azure OpenAI
"""

from __future__ import annotations

from typing import Any


class LLMReasoner:
    def reason_root_cause(self, evidence: dict[str, Any], heuristic: dict[str, Any]) -> dict[str, Any]:
        # Phase 2: deterministic pseudo-reasoning (safe + fast)
        primary_stage = heuristic.get("primaryStage")
        failed_runs = evidence.get("failedRuns", 0)

        explanation = f"Based on {failed_runs} failed runs"

        if primary_stage:
            explanation += f", the dominant failure stage is '{primary_stage}', suggesting localized instability."
        else:
            explanation += ", no dominant failure stage was identified."

        explanation += " The system recommends prioritizing investigation of that stage before others."

        return {
            "mode": "deterministic",
            "explanation": explanation,
            "confidence": "medium" if failed_runs else "high",
        }
