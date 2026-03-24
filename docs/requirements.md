# OpsHelm — Technical Requirements

## 1. Purpose

OpsHelm is an **Email-Native Operations Console** designed to convert Outlook email, ticket notifications, and calendar events into actionable operational intelligence.

The system ingests email via Microsoft Graph and produces:

- A daily execution plan (“Today’s Runway”)
- Customer queue daily briefs (one-click, branded)
- Meeting preparation briefs
- Promise/commitment tracking with reminders and receipts
- Quarterly and yearly accomplishment summaries (review-ready)

OpsHelm must support **Whiteglove partner delivery**, where identity, branding, and ticket sources are isolated by workspace.

---

## 2. Core Design Principles

- **Email is the system of record**
- **Evidence first** (every summary links to source receipts)
- **No silent automation** (drafts only, explicit approval required)
- **Workspace isolation** (no cross-customer or cross-partner leakage)
- **Contracts over vibes** (AI codegen must respect function contracts)

---

## 3. Definitions

### 3.1 Workspace

A **Workspace** is a hard operational boundary that governs:

- Mailbox identity and folders (e.g., Parex vs ParkPlace)
- Ticket source patterns (ConnectWise vs ServiceNow via email)
- Branding identity (From name, signature, disclaimers)
- Allowed customer themes
- Data isolation (partition key: `workspaceId`)
- Output voice and export headers

**Acceptance Criteria**
- No entity may be created, queried, or exported without a `workspaceId`
- UI must clearly indicate the active workspace (guardrail banner)

---

### 3.2 Theme (Customer Branding)

A **Theme** defines customer-specific branding:

- Logo (SVG/PNG)
- Color palette (primary, secondary, accent, background, card, text)
- Label aliases (e.g., *Ticket #* vs *Case*, *Priority* vs *Severity*)
- Export footer and disclaimer blocks
- Optional email tone/voice template

**Acceptance Criteria**
- All exports (HTML, Markdown, PDF, DOCX) use Workspace identity + Theme
- Theme availability is filtered by workspace

---

### 3.3 Ticket Sources

A **TicketSource** is a configurable email extraction profile.

Required support:
- **ConnectWise** numeric tickets (e.g., `#162518`)
- **ServiceNow** identifiers:
  - `INC#######`
  - `REQ#######`
  - `RITM#######`
  - `CHG#######`
  - `TASK#######`

**Acceptance Criteria**
- Ticket ID detection is configuration-driven, not hard-coded
- Multiple ticket sources may coexist per workspace

---

## 4. Core Data Entities (POC)

All derived entities must reference source evidence and include confidence metadata.

### 4.1 EmailEvent

- Message metadata (IDs, timestamps, sender/recipients)
- Subject and snippet
- Classification:
  - Ticket, Meeting, SentSummary, Internal, Noise, Other
- Extracted fields:
  - Ticket ID, customer, priority, status, asks, promises, due dates
- Confidence scores (classification and extraction)
- Evidence links (message URL, attachments)

---

### 4.2 Ticket

- Ticket ID, customer, queue
- Status bucket:
  - New
  - Waiting on Customer
  - Waiting on Me
  - In Progress
  - Risk
- Priority/severity
- Last customer and internal touch timestamps
- Next action
- Risk flags
- Evidence references (emails, artifacts)

---

### 4.3 Task (Runway Item)

- Title and next action
- Due date and ETA estimate
- Priority and status
- Source reference (Email, Ticket, Meeting)
- Evidence links

---

### 4.4 Commitment (Promise)

- Recipient (“promised to”)
- Promise text
- Promised date and due date
- Status:
  - Open
  - At Risk
  - Done
- Evidence email reference
- Reminder/escalation metadata

---

### 4.5 MeetingPrep

- Meeting ID, title, time, attendees
- Open loops (tickets and promises)
- Generated prep brief
- Evidence references
- Generated outputs:
  - Agenda draft
  - Update email draft
  - Post-meeting recap template

---

### 4.6 Artifact and Impact

**Artifact**
- Type (Script, Report, Brief, Runbook, Dashboard, Other)
- Title and creation date
- Delivery targets
- Related tickets
- Link or file reference

**Impact**
- Estimated hours saved
- Risk reduced or outcome achieved

---

## 5. Functional Requirements

### 5.1 Ingestion (Microsoft Graph)

The system must ingest:

- Mail:
  - Inbox
  - Workspace-approved folders
  - Sent Items
- Calendar events (for meeting prep)

Processing requirements:
- Classify all messages
- Extract ticket IDs using workspace ticket sources
- Extract asks and promises with due dates
- Maintain processing coverage metrics
- Route low-confidence items to an Exceptions queue

**Acceptance Criteria**
- Inbox Coverage Meter shows processed vs unprocessed
- No message is silently dropped

---

### 5.2 Today’s Runway (Daily Execution Plan)

- One-click generation of today’s prioritized tasks
- Derived from:
  - Ticket asks and promises
  - Stale tickets
  - Upcoming meetings
  - Overdue commitments
- Each item includes evidence links

**Acceptance Criteria**
- “Generate Runway” produces actionable items with receipts

---

### 5.3 Ticket Triage Board

Buckets:
- New
- Waiting on Customer
- Waiting on Me
- In Progress
- Risk

Ticket cards display:
- Ticket ID, customer, queue
- Priority/severity
- Last touch age
- Next action
- Risk flags with reasons

**Acceptance Criteria**
- Board supports search and drill-in
- Data is derived from stored tickets, not live parsing

---

### 5.4 Customer Queue Daily Brief

For a selected workspace, customer, and scope:

- Summarize all open tickets
- Include:
  - Top risks
  - Stale tickets
  - Waiting on customer vs waiting on team
  - **Diff since last brief**
- Optional generation of draft customer updates

Output modes:
- Internal Ops
- Technical
- Executive

Exports:
- HTML and Markdown (POC)
- PDF/DOCX (Phase 2)

**Acceptance Criteria**
- One-click generation produces a preview and Artifact record
- Diff section exists even in simplified POC form

---

### 5.5 Meeting Prep Studio

- List upcoming meetings
- Generate prep briefs covering:
  - Changes since last meeting
  - Open loops
  - Decisions required
- Generate:
  - Agenda draft
  - Update email draft
  - Post-meeting recap template

**Acceptance Criteria**
- Prep generation produces an Artifact linked to evidence

---

### 5.6 Promise Tracker

- Mine promises from Sent Items and replies
- Track due dates and risk
- Escalation reminders
- Draft update emails using workspace identity

**Acceptance Criteria**
- Promises include evidence links
- Promises can be converted to tasks

---

### 5.7 Accomplishments Generator

- Generate quarterly/yearly summaries based on:
  - Tickets touched/closed
  - Artifacts delivered
  - Promises kept
  - Proactive issues identified
  - Estimated hours saved
- Output tones:
  - Performance Review
  - Executive Update
  - Resume Bullets

**Acceptance Criteria**
- Output is review-ready with metrics

---

### 5.8 Whiteglove Mode (Partner Delivery)

- Separate workspaces for Parex and ParkPlace
- ParkPlace workspace uses ServiceNow ticket patterns
- Branding, exports, and drafts reflect partner identity
- No cross-workspace data mixing

**Acceptance Criteria**
- Theme lists are workspace-scoped
- Guardrail banner clearly indicates active identity

---

## 6. Governance and AI Safety

### 6.1 Contract Registry

- Maintain a registry of function signatures and invariants
- All AI-generated code changes must produce a contract diff
- Breaking changes require explicit PM approval

---

### 6.2 Policy Decisions

Each detected contract change is classified as:
- SAFE
- RISKY
- BREAKING

Resulting decisions:
- APPROVE
- DENY
- APPROVE_WITH_CONDITIONS

All decisions must be recorded as Policy Decision artifacts.

---

## 7. Required UI Pages (POC)

- Command Center
- Customer Brief
- Ticket Triage
- Meeting Prep
- Promise Tracker
- Inbox Intelligence
- Accomplishments
- Settings (Workspace and Branding)

---

## 8. Safety and Trust Requirements

- Evidence-first summaries
- Draft-only outputs (no auto-send)
- Prompt-injection mitigation:
  - Email content treated as untrusted data
- Secrets redacted by default
- Full audit trail for AI-assisted changes
