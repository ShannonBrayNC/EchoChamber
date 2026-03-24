# EchoChamber Missing Requirements → GitHub Issue Backlog

Use each section below as a **GitHub Issue**. Titles are prefixed for priority.

---

## P0-01: Implement Microsoft Graph ingestion pipeline

**Problem**
Ingestion runner is currently a stub and does not meet required deterministic sequence.

**Requirements**
- Pull mail (Inbox, allowed folders, Sent Items) and calendar events
- Classify all messages
- Extract ticket IDs, asks, promises, due dates
- Normalize into EmailEvent, Ticket, Task, Commitment
- Maintain coverage metrics
- Route low-confidence items to Exceptions queue
- Emit ingestion summary

**Acceptance Criteria**
- No message is silently dropped
- Coverage meter is accurate
- Ingestion is idempotent and deterministic

---

## P0-02: Expand Ops Store to required entities

**Problem**
Store only supports EmailEvent, Artifact, ProcessingState.

**Requirements**
Add tables/collections:
- Ticket
- Task
- Commitment
- MeetingPrep
- Impact
- Exception

**Acceptance Criteria**
- All entities include workspaceId
- Upserts follow deterministic keys
- Evidence references are enforced

---

## P0-03: Implement PM Orchestrator execution loop

**Problem**
Orchestrator is placeholder and not wired.

**Requirements**
- Execute ingestion
- Invoke agents (runway, etc.)
- Run SecuritySentry validation
- Log execution artifacts
- Return structured execution report

**Acceptance Criteria**
- Failure blocks execution
- Execution logs are persisted

---

## P0-04: Implement DailyRunwayAgent logic

**Problem**
Returns empty output.

**Requirements**
- Generate tasks from Ticket, Commitment, MeetingPrep
- Include stale tickets and overdue commitments
- Attach evidence links

**Acceptance Criteria**
- Runway produces actionable tasks with receipts

---

## P0-05: Implement Ticket Triage pipeline

**Problem**
No Ticket entity or UI exists.

**Requirements**
- Populate Ticket entity from ingestion
- Build API for ticket queries
- Build UI board with required buckets

**Acceptance Criteria**
- Board shows derived data only (no live parsing)

---

## P0-06: Implement Promise Mining pipeline

**Problem**
No commitment extraction or tracking exists.

**Requirements**
- Extract promises from Sent Items
- Track due dates and risk
- Generate reminders (draft-only)

**Acceptance Criteria**
- Promises include evidence links
- Promises can be converted to tasks

---

## P0-07: Implement Meeting Prep system

**Problem**
No MeetingPrep entity or agent exists.

**Requirements**
- Pull calendar events
- Generate prep briefs
- Include open loops and decisions
- Generate agenda + email draft + recap template

---

## P0-08: Implement Customer Brief generator

**Problem**
Missing Phase 2 core feature.

**Requirements**
- Summarize open tickets
- Include risk/stale/waiting breakdown
- Include diff vs last brief
- Output HTML/Markdown

---

## P0-09: Implement Whiteglove workspace configuration

**Problem**
Workspace concept exists but not implemented.

**Requirements**
- Workspace config model
- Ticket source rules per workspace
- Branding + theme filtering
- Guardrail banner in UI

**Acceptance Criteria**
- No cross-workspace data access

---

## P0-10: Wire API routers for intelligence + diagnostics

**Problem**
Routes exist but are not mounted.

**Requirements**
- Include intelligence_routes
- Include diagnostics_routes

---

## P1-01: Implement Contract Registry enforcement

**Problem**
Schema exists but no enforcement.

**Requirements**
- Contract extraction tool
- Diff generation
- Policy decision storage
- CI integration

---

## P1-02: Implement Inbox Intelligence page

**Requirements**
- Coverage meter
- Exceptions queue
- Drill-down for unprocessed messages

---

## P1-03: Implement Accomplishments generator

**Requirements**
- Aggregate metrics
- Generate review-ready outputs

---

## P1-04: Implement safety controls

**Requirements**
- Prompt injection mitigation
- Secrets redaction
- Evidence validation enforcement

---

## P1-05: End-to-end integration test suite

**Requirements**
- Ingestion → store → agents → API → UI
- Replay + diff validation

---

## Notes

These issues are derived directly from requirements and architecture documents. They are intentionally structured to prevent drift and enforce alignment with:
- Evidence-first design
- Workspace isolation
- Draft-only outputs
- Deterministic ingestion pipeline
