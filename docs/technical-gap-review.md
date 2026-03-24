# EchoChamber Technical Gap Review

Date: 2026-03-23
Branch reviewed: `feature/p1-foundation-scaffold`
Base compared: `main`

## Summary

The branch is a useful scaffold, but it is **not operational within the requirements definition** yet.
The current codebase provides early building blocks for a portal shell, SQLite store, security verifier, replay concepts, and a FastAPI surface. However, the majority of Phase 1 functional requirements are either stubbed, disconnected, or absent.

## What is working now

- Repository has a private feature branch ahead of main with 24 files changed.
- Basic FastAPI app exists with health and run-history endpoints.
- SQLite-backed store exists for `EmailEvent`, `Artifact`, and `ProcessingState`.
- SecuritySentry verifier and a small test suite exist.
- A minimal React/Vite portal exists and can be evolved into the Command Center.

## Critical findings

### 1. Ingestion is still a stub
`services/ingestion/runner.py` does not implement the required deterministic sequence. It does not load workspace config, does not pull Graph mail/calendar, does not classify, does not extract tickets/promises, does not normalize entities, does not write coverage metrics, and does not emit a structured ingestion summary.

### 2. Core entities are missing from the store
The requirements and architecture require `Ticket`, `Task`, `Commitment`, `MeetingPrep`, `Impact`, and exception handling, but the store currently only persists `EmailEvent`, `Artifact`, and `ProcessingState`.

### 3. The PM orchestrator is not wired
`services/agents/pm/orchestrator.py` is still a placeholder and does not execute ingestion, invoke agents, enforce SecuritySentry, or log execution.

### 4. Content agents are mostly placeholders
`DailyRunwayAgent` returns an empty structure and does not generate tasks from stored data. Other required content agents do not exist yet: `CustomerBriefAgent`, `MeetingPrepAgent`, `PromiseMiningAgent`, `AccomplishmentsAgent`, `DraftEmailAgent`.

### 5. UI does not yet meet the required page set
The current React app only shows runs and replay output. Required POC pages such as Ticket Triage, Meeting Prep, Promise Tracker, Inbox Intelligence, Accomplishments, Settings, and Customer Brief are not implemented.

### 6. API surface is incomplete and partially disconnected
The repository contains separate `intelligence_routes.py` and `diagnostics_routes.py`, but `services/api/main.py` does not include those routers. As a result, adaptive intelligence and diagnostics are not operational through the running API.

### 7. Whiteglove workspace support is not implemented
Workspace-specific configuration, theme filtering, partner identity, and ServiceNow-vs-ConnectWise source rules are not yet implemented in code.

### 8. Governance artifacts are incomplete
A contract schema exists, but there is no policy-decision schema, no stored policy-decision artifacts, no contract extraction tool, no diff generation, no CI enforcement, and no documented migration/test gate implementation.

### 9. Required safety controls are incomplete
There is partial action blocking in SecuritySentry, but no concrete prompt-injection mitigation in ingestion/classification, no secrets redaction path, and no evidence validation for most artifact-generating flows because those flows are not fully implemented.

### 10. Test coverage is insufficient for 24-hour operational readiness
Current tests only cover basic store behavior and SecuritySentry. There are no integration tests for ingestion, no API tests, no replay tests, no portal tests, and no end-to-end workflow validation.

## Feature-by-feature requirement status

| Requirement Area | Status | Notes |
|---|---|---|
| Microsoft Graph ingestion | Missing | Stub only |
| Coverage meter + exceptions queue | Missing | No exception entity or UI |
| Today's Runway | Stub | Empty output, no tasks |
| Ticket Triage Board | Missing | No ticket entity/UI |
| Customer Queue Daily Brief | Missing | No agent/UI/export |
| Meeting Prep Studio | Missing | No entity/agent/UI |
| Promise Tracker | Missing | No commitment mining pipeline/UI |
| Accomplishments Generator | Missing | No agent/UI |
| Whiteglove workspaces | Missing | No workspace config/theme support |
| Theme/branding | Missing | No theme model or exports |
| Contract diff + policy decisions | Missing | Schema only |
| Full audit trail | Partial | Execution logger exists conceptually, but orchestration is not wired |
| Prompt-injection mitigation | Missing | Requirement not implemented in ingestion pipeline |
| Secrets redaction | Missing | No redaction pipeline |

## 24-hour operational path

To get EchoChamber operational in the next 24 hours, prioritize:

1. Real ingestion pipeline with deterministic normalization.
2. Store support for `Ticket`, `Task`, `Commitment`, and exceptions.
3. Working PM orchestrator with SecuritySentry and execution logging wired.
4. Daily Runway generation from real store data.
5. Minimal Command Center pages for Runway, Inbox Intelligence, Ticket Triage, and Settings.
6. Workspace config + ticket source rules for at least one real workspace.
7. API router wiring for intelligence/diagnostics.
8. End-to-end smoke tests.

## Tooling constraint

This environment can write files, branches, and pull requests in GitHub, but it does **not** currently expose a GitHub issue-creation action. To avoid losing requirements, issue-ready backlog entries have been committed to `docs/missing-requirements-issue-backlog.md` for direct paste into GitHub Issues.
