"""Replay engine for EchoChamber Phase 2.

Replays a previously logged execution and compares the new result to the stored
execution log payload. The engine is intentionally runner-agnostic: callers pass
in a callable that knows how to rerun a workflow for a workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from services.query.run_history import RunHistoryQuery


@dataclass
class ReplayResult:
    source_run_id: str
    replay_status: str
    original_run: dict[str, Any]
    replay_run: dict[str, Any]
    diff: dict[str, Any]


class ReplayEngine:
    def __init__(self, history: RunHistoryQuery | None = None):
        self.history = history or RunHistoryQuery()

    def replay_run(
        self,
        workspace_id: str,
        run_id: str,
        rerun_callable: Callable[[str], dict[str, Any]],
    ) -> ReplayResult:
        original = self.history.get_run(workspace_id, run_id)
        if not original:
            raise ValueError(f"Run not found: {run_id}")

        replay = rerun_callable(workspace_id)
        diff = self.compare_runs(original, replay)
        replay_status = "matched" if not diff else "changed"

        return ReplayResult(
            source_run_id=run_id,
            replay_status=replay_status,
            original_run=original,
            replay_run=replay,
            diff=diff,
        )

    @staticmethod
    def compare_runs(original: dict[str, Any], replay: dict[str, Any]) -> dict[str, Any]:
        diff: dict[str, Any] = {}
        all_keys = sorted(set(original.keys()) | set(replay.keys()))

        for key in all_keys:
            original_value = original.get(key)
            replay_value = replay.get(key)
            if original_value != replay_value:
                diff[key] = {
                    "original": original_value,
                    "replay": replay_value,
                }

        return diff
