# EchoChamber RC Readiness Review and Sprint Plan

Reviewed: 2026-05-25  
Repository: `ShannonBrayNC/EchoChamber`  
Target: First RC candidate for EchoChamber as Lantern's multilingual translation, pronunciation, and voice service.

## Executive Assessment

EchoChamber is not RC-ready yet. The repo now has a clear product direction and early architecture documentation, but the release candidate is blocked by the absence of a runnable service, incomplete contract assets, missing validation, no test harness, no artifact storage model, and no ElevenLabs integration implementation.

The RC should be defined as a demoable, contract-valid, local-first service that can:

1. accept a valid EchoChamber translation request,
2. translate English to Polish,
3. produce a pronunciation lesson,
4. optionally generate ElevenLabs audio,
5. persist artifact metadata,
6. validate examples/contracts in CI,
7. expose a stable FastAPI surface for Lantern tools.

## Current Project State

The repo now defines EchoChamber as the Lantern language bridge. The architecture states that EchoChamber accepts text or repo artifacts, translates them, optionally generates pronunciation coaching, and can create ElevenLabs audio artifacts. It also defines the expected API, translation, pronunciation, ElevenLabs, contract, and artifact layers.

The integrations document identifies ETS, OpsHelm, Christina, SignalForge, Content Engine, and EchoLiving as consumers, each with integration constraints.

The governance document defines the need for contracts, provenance, consent-aware processing, workspace identifiers, and future CI validation.

The contracts README defines stable integration contracts, schema examples, tool manifests, and stability rules, but several referenced files either need completion or need validation wiring.

## RC Blocker Summary

| ID | Blocker | Severity | RC Impact |
|---|---|---:|---|
| RC-01 | No runnable FastAPI application committed | Critical | Nothing can be started, tested, or called by other tools |
| RC-02 | Translation service is not implemented | Critical | Core product promise cannot execute |
| RC-03 | Pronunciation/phonetics engine is not implemented | Critical | Polish-learning use case cannot be demonstrated |
| RC-04 | ElevenLabs service wrapper is missing | Critical | Voice/audio output cannot be generated |
| RC-05 | Artifact storage and metadata model are missing | High | Outputs cannot be saved, audited, or reused |
| RC-06 | Contract registry and schema set are incomplete | High | Tool-to-tool integration is not stable |
| RC-07 | No contract validation script/workflow | High | Contract drift cannot be detected |
| RC-08 | Tool manifests are incomplete or not enforced | High | ETS/OpsHelm/Christina/etc. cannot safely integrate |
| RC-09 | No tests | Critical | No RC confidence gate exists |
| RC-10 | No local developer bootstrap | High | A contributor cannot reliably run the project |
| RC-11 | No `.env.example`/secret contract for providers | Medium | ElevenLabs/OpenAI configuration is ambiguous |
| RC-12 | No API examples or smoke-test collection | Medium | Demo and integration validation are manual only |
| RC-13 | Consent guardrails are documented but unenforced | High | Voice cloning/synthesis safety is not operational |
| RC-14 | Workspace/provenance guard is documented but unenforced | High | Cross-tool/cross-workspace leakage risk remains |
| RC-15 | No release checklist or RC definition of done | Medium | RC scope can drift |

---

# Sprint 0 — RC Definition and Repo Foundation

## Goal

Freeze what “RC-ready” means and make the repo predictable for Codex, GitHub Actions, and human contributors.

## Issues

### RC-00.1 — Define RC scope and release gates

**Problem:** EchoChamber has vision and architecture, but no concrete RC definition of done.

**Acceptance Criteria**

- `docs/rc-definition.md` exists.
- RC scope explicitly includes:
  - FastAPI service
  - `/health`
  - `/api/v1/translate`
  - `/api/v1/lesson`
  - optional `/api/v1/speak`
  - contract validation
  - sample Polish learning request
  - local artifact metadata persistence
- RC explicitly excludes:
  - production auth
  - full React UI
  - production Azure deployment
  - real voice cloning workflow unless consent metadata is implemented

### RC-00.2 — Add local project bootstrap files

**Problem:** The README describes local development, but the supporting files are incomplete or missing.

**Acceptance Criteria**

- `requirements.txt` exists.
- `.env.example` exists.
- `pyproject.toml` exists with project metadata.
- `apps/api/main.py` exists.
- `scripts/demo_translate.py` exists.
- Running `pip install -r requirements.txt` is sufficient for local API startup.

### RC-00.3 — Add repository release checklist

**Problem:** There is no repeatable RC release checklist.

**Acceptance Criteria**

- `docs/release-checklist.md` exists.
- Checklist includes tests, contract validation, environment validation, API smoke tests, artifact persistence, and audio-disabled fallback.

---

# Sprint 1 — Contract Spine and Tool Manifests

## Goal

Make EchoChamber callable by ETS, OpsHelm, Christina, SignalForge, Content Engine, EchoLiving, and Lantern through stable, validated contracts.

## Issues

### RC-01.1 — Complete contract registry

**Problem:** Contracts are described, but the registry is not complete enough to drive compatibility checks.

**Acceptance Criteria**

- `contracts/registry.json` exists.
- Registry includes:
  - `registryVersion`
  - `updatedAt`
  - contract list
  - owners
  - consumers
  - request schema path
  - response schema path
  - stability value
- Registry includes at least:
  - `translate`
  - `translate_and_voice`
  - `pronunciation_lesson`
  - `repo_artifact_translation`

### RC-01.2 — Complete JSON schemas

**Problem:** The request schema exists, but the full schema set referenced by docs/contracts must exist and be validated.

**Acceptance Criteria**

- These files exist:
  - `contracts/schemas/echochamber.request.schema.json`
  - `contracts/schemas/echochamber.response.schema.json`
  - `contracts/schemas/pronunciation.lesson.schema.json`
  - `contracts/schemas/voice.generation.schema.json`
  - `contracts/schemas/translation.artifact.schema.json`
  - `contracts/schemas/tool-manifest.schema.json`
  - `contracts/schemas/policy-decision.schema.json`
- Schemas use JSON Schema draft 2020-12.
- Schemas reject missing provenance for tool-originated requests.
- Schemas require consent metadata when voice clone or named voice is requested.

### RC-01.3 — Add per-tool contract manifests

**Problem:** Integrated tools are listed, but their exact permissions and request types are not enforceable.

**Acceptance Criteria**

- These files exist:
  - `contracts/tools/ets.contract.json`
  - `contracts/tools/opshelm.contract.json`
  - `contracts/tools/christina.contract.json`
  - `contracts/tools/signalforge.contract.json`
  - `contracts/tools/content-engine.contract.json`
  - `contracts/tools/echoliving.contract.json`
  - `contracts/tools/lantern.contract.json`
- Each manifest declares:
  - allowed request types
  - voice allowed/blocked
  - provenance requirements
  - formatting rules
  - workspace rules

### RC-01.4 — Add contract examples

**Problem:** There are no enough examples to validate cross-tool usage.

**Acceptance Criteria**

- These example files exist:
  - `contracts/examples/polish-learning-request.json`
  - `contracts/examples/opshelm-brief-request.json`
  - `contracts/examples/christina-customer-message.json`
  - `contracts/examples/content-engine-dialogue-request.json`
  - `contracts/examples/ets-evidence-translation.json`
- Every example validates against `echochamber.request.schema.json`.

---

# Sprint 2 — API Skeleton and Domain Models

## Goal

Create a runnable FastAPI service with typed models and stubbed behavior that returns contract-valid responses.

## Issues

### RC-02.1 — Add FastAPI app shell

**Problem:** Architecture describes API endpoints, but there is no confirmed runnable app shell.

**Acceptance Criteria**

- `apps/api/main.py` exists.
- `/health` returns status and version.
- Routers are organized under `apps/api/routes/`.
- App starts with `uvicorn apps.api.main:app --reload`.

### RC-02.2 — Add typed request/response models

**Problem:** Runtime payloads need validation beyond static JSON Schema.

**Acceptance Criteria**

- `packages/echochamber/contracts/models.py` exists.
- Pydantic models exist for:
  - `EchoChamberRequest`
  - `EchoChamberResponse`
  - `PronunciationChunk`
  - `AudioArtifact`
  - `Provenance`
  - `VoiceOptions`
- Models align with JSON schemas.

### RC-02.3 — Add translation route

**Problem:** `/api/v1/translate` is required for RC.

**Acceptance Criteria**

- `POST /api/v1/translate` accepts `EchoChamberRequest`.
- Response includes translated text, target language, provenance, and artifact metadata.
- When translation provider is unavailable, service returns deterministic stub output in dev mode.

### RC-02.4 — Add lesson route

**Problem:** Polish learning requires pronunciation lesson generation.

**Acceptance Criteria**

- `POST /api/v1/lesson` accepts text and target language.
- Response includes phonetic hint and practice chunks.
- Polish-specific characters are handled for at least:
  - ś
  - ł
  - ę
  - ą
  - cz
  - sz
  - rz/ż

### RC-02.5 — Add speech route

**Problem:** Voice generation requires an API surface even if disabled in local dev.

**Acceptance Criteria**

- `POST /api/v1/speak` exists.
- If ElevenLabs is not configured, response returns a clear provider-disabled status.
- If configured, route delegates to ElevenLabs service.

---

# Sprint 3 — Translation, Pronunciation, and Audio Services

## Goal

Implement the actual MVP behavior behind the routes.

## Issues

### RC-03.1 — Implement translation service

**Problem:** EchoChamber cannot perform its primary function.

**Acceptance Criteria**

- `packages/echochamber/translation/service.py` exists.
- Supports provider abstraction:
  - `dev_stub`
  - `openai`
  - future provider slot
- English-to-Polish demo phrase works.
- Translation preserves formatting when requested.

### RC-03.2 — Implement Polish pronunciation service

**Problem:** The Vanessa/Polish learning use case depends on useful pronunciation guidance.

**Acceptance Criteria**

- `packages/echochamber/phonetics/polish.py` exists.
- Returns:
  - phonetic hint
  - syllable/practice chunks
  - character notes
  - slow-practice phrase
- Includes tests for at least 10 common Polish phrases.

### RC-03.3 — Implement ElevenLabs service wrapper

**Problem:** Audio generation is only conceptual.

**Acceptance Criteria**

- `packages/echochamber/tts/elevenlabs_service.py` exists.
- Reads `ELEVENLABS_API_KEY` and default voice ID from environment.
- Does not log secrets.
- Supports disabled/dev mode.
- Saves audio file when generation succeeds.
- Returns provider metadata and artifact path.

### RC-03.4 — Implement artifact service

**Problem:** Generated translations/audio need traceability.

**Acceptance Criteria**

- `packages/echochamber/artifacts/service.py` exists.
- Stores metadata as JSON under `storage/artifacts/`.
- Stores audio under `storage/audio/`.
- Artifact metadata includes:
  - source text hash
  - translated text
  - source tool
  - workspace ID
  - provider
  - voice ID
  - timestamp

---

# Sprint 4 — Safety, Consent, and Workspace Guards

## Goal

Turn documented safety boundaries into executable checks.

## Issues

### RC-04.1 — Enforce provenance guard

**Problem:** Provenance is required by architecture/governance but not enforced.

**Acceptance Criteria**

- Requests from non-manual tools require provenance.
- Missing `workspaceId` is rejected.
- Missing `sourceId` is rejected.
- Validation errors are clear and test-covered.

### RC-04.2 — Enforce voice consent guard

**Problem:** Consent is documented but not operational.

**Acceptance Criteria**

- Named/custom voice generation requires `consentId` or explicit consent flag.
- Voice clone requests without consent are rejected.
- Default non-cloned voice may be allowed for MVP.
- Tests cover allowed and blocked cases.

### RC-04.3 — Add workspace leakage guard

**Problem:** Tool outputs may later cross customers/workspaces without enforcement.

**Acceptance Criteria**

- Artifact writes include workspace ID.
- Artifact reads require workspace ID.
- No artifact lookup is allowed by raw artifact ID alone.
- Tests prove workspace A cannot read workspace B artifact metadata.

---

# Sprint 5 — Contract Validation and CI

## Goal

Add automated confidence gates before RC tagging.

## Issues

### RC-05.1 — Add contract validation script

**Problem:** Contract drift cannot be detected.

**Acceptance Criteria**

- `scripts/validate_contracts.py` validates:
  - JSON parse correctness
  - examples against schemas
  - tool manifests against schema
  - registry paths exist
- Script exits non-zero on validation failure.

### RC-05.2 — Add GitHub Actions workflow

**Problem:** No automated validation exists.

**Acceptance Criteria**

- `.github/workflows/ci.yml` exists.
- CI runs:
  - Python install
  - unit tests
  - contract validation
  - basic import check
- CI fails on schema/example mismatch.

### RC-05.3 — Add smoke test script

**Problem:** RC demo cannot be verified quickly.

**Acceptance Criteria**

- `scripts/smoke_test.py` exists.
- Validates:
  - `/health`
  - `/api/v1/translate`
  - `/api/v1/lesson`
  - `/api/v1/speak` disabled fallback

---

# Sprint 6 — RC Demo Path

## Goal

Create a simple, repeatable demo that proves EchoChamber works for Polish learning and Lantern tool integration.

## Issues

### RC-06.1 — Add demo CLI

**Problem:** The README references a demo command, but the demo path needs to exist.

**Acceptance Criteria**

- `scripts/demo_translate.py` accepts:
  - source text
  - source language
  - target language
  - audio flag
  - phonetics flag
- Demo prints translation and practice chunks.
- Audio generation is optional.

### RC-06.2 — Add Polish learning demo fixture

**Problem:** The first real use case needs a polished demo.

**Acceptance Criteria**

- `examples/polish/vanessa_phrasebook.json` exists.
- Contains at least 20 phrases.
- Includes English, Polish, phonetic hint, and learner note.

### RC-06.3 — Add Lantern integration demo

**Problem:** EchoChamber must prove it can serve other repos.

**Acceptance Criteria**

- `examples/lantern/opshelm_customer_brief_translation.json` exists.
- `examples/lantern/ets_evidence_translation.json` exists.
- Both are contract-valid.

---

# Sprint 7 — RC Hardening and Documentation

## Goal

Prepare the release candidate for tagging and external demo.

## Issues

### RC-07.1 — Update README with real startup/test commands

**Problem:** README should match actual repo behavior.

**Acceptance Criteria**

- README startup command works.
- README demo command works.
- README explains dev stub mode vs real provider mode.

### RC-07.2 — Add API reference

**Problem:** Integrating tools need endpoint documentation.

**Acceptance Criteria**

- `docs/api.md` exists.
- Documents request/response for:
  - `/health`
  - `/api/v1/translate`
  - `/api/v1/lesson`
  - `/api/v1/speak`
  - `/api/v1/contracts`

### RC-07.3 — Add RC release notes template

**Problem:** RC releases need consistent notes.

**Acceptance Criteria**

- `docs/release-notes/rc-template.md` exists.
- Includes:
  - summary
  - known issues
  - testing performed
  - contract version
  - migration notes

---

# Recommended Sprint Order

1. Sprint 0 — RC Definition and Repo Foundation
2. Sprint 1 — Contract Spine and Tool Manifests
3. Sprint 2 — API Skeleton and Domain Models
4. Sprint 3 — Translation, Pronunciation, and Audio Services
5. Sprint 4 — Safety, Consent, and Workspace Guards
6. Sprint 5 — Contract Validation and CI
7. Sprint 6 — RC Demo Path
8. Sprint 7 — RC Hardening and Documentation

## Next Highest Priority Recommendation

Start with **Sprint 0 + Sprint 1 together**.

Reason: EchoChamber is becoming a cross-repo language service. Before building deeper code, the repository needs a locked contract spine and a precise RC definition. Otherwise ETS, OpsHelm, Christina, and Content Engine will each invent slightly different request/response shapes, creating integration fog.

The first implementation PR should therefore add:

- `docs/rc-definition.md`
- `docs/release-checklist.md`
- `contracts/registry.json`
- missing schemas
- missing tool manifests
- missing examples
- `scripts/validate_contracts.py`
- `.github/workflows/ci.yml`

That gives Codex and future agents a clean runway instead of a foggy runway with a raccoon holding glowsticks.
