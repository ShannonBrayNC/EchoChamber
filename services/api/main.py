"""Command Center API for EchoChamber.

Phase 2 scope:
- Health endpoint
- Workspace run history endpoints
- Replay endpoint
- Diff intelligence endpoint
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from services.agents.pm.orchestrator import PMOrchestrator
from services.query.run_history import RunHistoryQuery
from services.replay.diff_intelligence import DiffIntelligence
from services.replay.replay_engine import ReplayEngine


app = FastAPI(title="EchoChamber Command Center API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/workspaces/{workspace_id}/runs")
def list_runs(
    workspace_id: str,
    status: str | None = None,
    stage: str | None = None,
    limit: int = 20,
) -> dict[str, object]:
    history = RunHistoryQuery()
    runs = history.list_runs(workspace_id, status=status, stage=stage, limit=limit)
    summary = history.summarize_runs(workspace_id)
    return {
        "workspaceId": workspace_id,
        "summary": summary,
        "runs": runs,
    }


@app.get("/workspaces/{workspace_id}/runs/{run_id}")
def get_run(workspace_id: str, run_id: str) -> dict[str, object]:
    history = RunHistoryQuery()
    run = history.get_run(workspace_id, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.post("/workspaces/{workspace_id}/runs/{run_id}/replay")
def replay_run(workspace_id: str, run_id: str) -> dict[str, object]:
    engine = ReplayEngine()

    try:
        replay = engine.replay_run(
            workspace_id=workspace_id,
            run_id=run_id,
            rerun_callable=lambda ws: PMOrchestrator(ws).run_daily(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    intelligence = DiffIntelligence.summarize_diff(replay.diff)

    return {
        "sourceRunId": replay.source_run_id,
        "replayStatus": replay.replay_status,
        "diff": replay.diff,
        "intelligence": intelligence,
        "replayRun": replay.replay_run,
    }


@app.get("/workspaces/{workspace_id}/runs/{run_id}/diff")
def diff_run(workspace_id: str, run_id: str) -> dict[str, object]:
    history = RunHistoryQuery()
    run = history.get_run(workspace_id, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    intelligence = DiffIntelligence.summarize_diff({})
    return {
        "workspaceId": workspace_id,
        "runId": run_id,
        "intelligence": intelligence,
        "note": "Use POST /replay to generate a fresh diff against current execution.",
    }
