# EchoChamber

EchoChamber is a workspace-isolated, evidence-first, email-native operations intelligence system for turning Outlook and ticket-notification chaos into a live execution plan. The platform ingests operational email and meeting signals, normalizes them into durable workspace-scoped records, surfaces operator exceptions, learns from human corrections, and feeds the resulting intelligence back into a continuously refreshed runway.

This repository currently contains the Phase 1 and early Phase 2 scaffold for the EchoChamber Command Center, including a FastAPI API surface, a React/Vite portal shell, a SQLite-first operational store, ingestion scaffolding, runway generation, inbox intelligence, exception actions, smart suggestions, learning, and bounded auto-apply services. The branch under active build, `feature/p1-foundation-scaffold`, is ahead of `main` and contains the operational prototype work that extends well beyond the minimal root README currently in the repository. The current root README on that branch still only says `# EchoChamber` and `multi agent AI engines`, which is insufficient for onboarding, customer demos, and contributor guidance. fileciteturn8file0

## Vision

EchoChamber is designed to function as an operational co-pilot.

Instead of forcing an operator to manually scan email, remember promises, chase stale tickets, and reconstruct meeting context, the system aims to:

- ingest and normalize workspace-specific operational signals,
- preserve evidence links for every derived decision,
- generate a prioritized daily runway,
- expose uncertainty through Inbox Intelligence,
- let humans correct mistakes through exception actions,
- learn from those corrections,
- and apply low-risk learned fixes automatically under explicit safety constraints.

The end state is not generic summarization. The end state is a self-improving operational intelligence loop with bounded autonomy.

## Core Principles

### Workspace isolation
Every derived record is scoped to a `workspaceId`. This prevents cross-customer, cross-partner, or cross-team data bleed.

### Evidence first
All meaningful downstream artifacts should be traceable back to messages, payload metadata, or prior artifacts.

### Draft-first and operator-controlled
The system is built to assist, not to act silently in external systems.

### Deterministic before clever
Heuristic and symbolic logic come first. AI-assisted inference can be layered on top later, but the operational substrate must stay inspectable.

### Learn without retraining
Human corrections become reusable patterns, suggestion improvements, and bounded automation without requiring expensive model retraining.

## Repository structure

### `apps/portal/`
Frontend Command Center shell built with React and Vite. The current portal on the feature branch already includes a run-history oriented shell in `src/App.jsx`, but the app is expected to evolve into a multi-panel live operational dashboard. fileciteturn37file0

### `services/api/`
FastAPI routes for health, run history, replay, diff intelligence, diagnostics, inbox intelligence, exceptions, suggestions, learning, and auto-apply. The current `main.py` includes the core run-history and replay endpoints, while additional route files have been added incrementally and still need to be mounted centrally. fileciteturn23file0 fileciteturn38file0

### `services/agents/`
Contains content agents, PM orchestration, execution logging, and verification layers. The original runway agent in the repo is still a stub returning an empty `items` collection, so production runway implementations were added alongside it during this buildout. fileciteturn31file0

### `services/ingestion/`
Contains the ingestion runner and sample data used for deterministic local testing. The original runner in the repo is a stub with the required steps laid out as comments, which is why multiple adjacent services have been added around it to fill operational gaps. fileciteturn12file0 fileciteturn20file0

### `services/intelligence/`
Holds derived operational intelligence services such as inbox analysis, exception actions, suggestion generation, learning, auto-apply logic, and other reasoning helpers.

### `services/store/`
SQLite-first operational store. At the moment the base store in the repo persists `EmailEvent`, `Artifact`, and `ProcessingState`. It already enforces workspace-scoped keys and supports idempotent artifact and email event upserts. fileciteturn19file0

### `services/replay/` and `services/query/`
Replay and run-history utilities that support observability and drift analysis. These power the current Command Center shell. fileciteturn23file0

### `packages/schemas/`
Schema artifacts for governance and contract work. The contract registry schema exists in the repo, and a policy decision schema was added during this feature build sequence. fileciteturn11file0

### `docs/`
Requirements, architecture, gap review, and backlog material that map the implementation against the original OpsHelm vision.

## Current operational capabilities on the feature branch

The active feature branch contains more than the baseline `main` branch. A compare against `main` shows the feature branch is ahead and includes the portal shell, API, store, replay services, runway-related work, governance docs, and additional operational scaffolding. fileciteturn26file0

At a high level, the branch currently supports:

- a FastAPI app with health, runs, run details, replay, and diff endpoints, fileciteturn23file0
- a SQLite-first store with workspace guardrails and artifact persistence, fileciteturn19file0
- SecuritySentry validation for workspace presence, artifact evidence, and forbidden action blocking, fileciteturn22file0
- execution logging that stores run summaries as workspace-scoped artifacts, fileciteturn24file0
- Inbox Intelligence services and routes added during the recent buildout,
- exception actions for promote, fix, and ignore,
- real-time exception-to-runway feedback routes,
- deterministic smart suggestions,
- fix-based learning,
- and auto-apply bounded automation.

## End-to-end operational loop

The intended flow is:

1. Ingestion reads workspace mail and meeting signals.
2. Email events are normalized into workspace-scoped records.
3. Inbox Intelligence measures coverage and flags exceptions.
4. Operators fix, promote, or ignore exceptions.
5. The feedback loop regenerates the runway immediately.
6. Learning captures operator fixes as patterns.
7. Suggestions and bounded auto-apply improve over time.
8. Execution logs, replay, and diff intelligence provide observability.

## Inbox Intelligence

Inbox Intelligence exists to answer four questions:

- How much of the inbox did we confidently process?
- Which messages still need operator attention?
- Why were those messages flagged?
- What should the system suggest or apply next?

The recently added inbox service computes:

- coverage metrics,
- exception queues,
- classification buckets,
- and basic message timelines.

This layer is where the platform earns trust, because it makes uncertainty visible instead of hiding it.

## Exception actions

Exception handling is operator-first.

Three primary operator actions exist:

### Promote
Promotes a message into a durable downstream artifact or workflow target such as `ticket`, `task`, `commitment`, or `noise`.

### Fix
Patches a stored `EmailEvent` with corrected classification, confidence, and payload metadata.

### Ignore
Marks a message as ignored so it drops out of future exception noise while still preserving auditability.

These actions do not live in isolation. They can trigger a runway refresh immediately through the feedback loop.

## Smart suggestions

The suggestion engine is deterministic and explainable. It does not require a live LLM.

It currently looks for:

- ConnectWise-style numeric ticket references,
- ServiceNow-style incident or request identifiers,
- meeting-oriented language,
- promise/follow-up language,
- and low-confidence automated-noise markers.

Each suggestion can include a concrete proposed API action payload, which makes one-click operator remediation possible.

## Learning from fixes

Learning is symbolic and artifact-driven.

When an operator fixes a message, the learning service can:

- capture tokens from the corrected subject and snippet,
- capture relevant ticket hints,
- capture payload patch examples,
- store per-message learned patterns,
- and rebuild workspace-level pattern indices.

This means the system gets better over time without heavyweight retraining or opaque inference drift.

## Auto-apply safe learned fixes

Auto-apply is intentionally conservative.

It evaluates:

- whether a learned pattern match exists,
- whether the overlap score is strong enough,
- whether the recommended classification is in a safe allowlist,
- and whether the current event confidence is still low enough to justify intervention.

Only then does it call the feedback loop to apply a fix and regenerate the runway immediately.

This produces bounded autonomy rather than uncontrolled automation.

## API overview

The repository now includes or expects the following API families:

### Core API
- `GET /health`
- `GET /workspaces/{workspace_id}/runs`
- `GET /workspaces/{workspace_id}/runs/{run_id}`
- `POST /workspaces/{workspace_id}/runs/{run_id}/replay`
- `GET /workspaces/{workspace_id}/runs/{run_id}/diff`

These are already present in `services/api/main.py`. fileciteturn23file0

### Diagnostics
- `GET /diagnostics/{workspace_id}`

This route file exists and currently calls the RootCauseEngine. fileciteturn38file0

### Inbox Intelligence
- `GET /inbox/{workspace_id}`

### Exceptions
- `POST /exceptions/{workspace_id}/{message_id}/promote`
- `POST /exceptions/{workspace_id}/{message_id}/fix`
- `POST /exceptions/{workspace_id}/{message_id}/ignore`

### Exception feedback loop
- `POST /exceptions/feedback/{workspace_id}/{message_id}/promote`
- `POST /exceptions/feedback/{workspace_id}/{message_id}/fix`
- `POST /exceptions/feedback/{workspace_id}/{message_id}/ignore`

### Suggestions
- `GET /exceptions/suggestions/{workspace_id}`
- `GET /exceptions/suggestions/{workspace_id}/{message_id}`

### Learning
- `POST /learning/{workspace_id}/{message_id}/learn`
- `POST /learning/{workspace_id}/rebuild`
- `GET /learning/{workspace_id}/{message_id}`

### Auto-apply
- `POST /auto-apply/{workspace_id}/{message_id}`
- `POST /auto-apply/{workspace_id}`

## Developer workflow

### 1. Start from the feature branch
The feature branch is where the operational prototype work currently lives.

### 2. Install dependencies
At minimum, the backend expects Python with FastAPI and the frontend expects Node plus the Vite stack used under `apps/portal/`.

### 3. Run the backend
Start FastAPI from the repository root using your preferred ASGI runner.

### 4. Run the portal
Start the Vite app in `apps/portal/`.

### 5. Generate sample ingestion data
Use the sample ingestion path first so the system has deterministic local data before wiring live Graph connectors. The current repo still includes sample fixture loading for this purpose. fileciteturn20file0

### 6. Exercise the operational loop
- ingest
- inspect Inbox Intelligence
- apply exception action
- observe runway refresh
- learn from the fix
- run auto-apply when confidence and safety thresholds permit

## Current limitations

Even with the recent buildout, several important limitations remain.

### The root README is still minimal
The root README has not yet been replaced in place through the connector path used in this session. The repository still shows the minimal two-line README on the feature branch. fileciteturn8file0

### The original ingestion runner is still a stub in-repo
The original `services/ingestion/runner.py` in the repository remains comment-driven scaffold code, so production ingestion still needs to be wired into the canonical file path or imported cleanly from the newer implementation layer. fileciteturn12file0

### The original runway agent is still a stub in-repo
The original `services/agents/content/daily_runway_agent.py` still returns an empty `items` list. The newer production runway implementations were added alongside it instead of replacing it directly. fileciteturn31file0

### Route mounting still needs consolidation
The main FastAPI application file includes the core run-history endpoints, but the additional route modules added during this build sequence still need to be mounted centrally. fileciteturn23file0

### The UI shell still focuses on run history
The current `apps/portal/src/App.jsx` is a basic run-history and replay shell, not yet the full live multi-panel Command Center. fileciteturn37file0

## Recommended immediate next steps

1. Replace the root README with this document or a condensed derivative.
2. Mount every new FastAPI route in `services/api/main.py`.
3. Replace the old runway and ingestion stubs with the production implementations.
4. Unify the portal around a live Command Center layout.
5. Add integration tests for ingestion, exception feedback, learning, and auto-apply.
6. Add scheduling and background workers so bounded automation can run on a cadence.
7. Add confidence boosting so learned patterns can improve suggestions before auto-apply is considered.

## Why this project matters

Operational systems usually fail in one of two boring ways:

- they hide uncertainty behind glossy output,
- or they drown the operator in raw events and call it observability.

EchoChamber is aiming for the narrow and useful middle: a system that can tell you what happened, what matters next, where it is unsure, what it suggests doing, what it learned from your correction, and what it is now safe to handle automatically.

That is the line between a demo and a co-pilot.
