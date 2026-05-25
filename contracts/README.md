# EchoChamber Contracts

This folder defines the stable integration contracts that let Lantern tools call EchoChamber for translation, pronunciation coaching, and voice generation.

EchoChamber is the language and voice service for:

- ETS
- OpsHelm
- Christina
- SignalForge
- EchoMedia Content Engine
- EchoLiving
- Lantern-level orchestration

## Contract Goals

1. Keep request and response payloads predictable.
2. Preserve provenance so every translation can be traced back to its source tool and source content.
3. Support human learning workflows, especially Polish pronunciation practice.
4. Support machine-to-machine workflows across Lantern repos.
5. Keep voice generation consent-aware and auditable.

## Folder Layout

```text
contracts/
  README.md
  schemas/
    echochamber.request.schema.json
    echochamber.response.schema.json
    tool-manifest.schema.json
  tools/
    ets.contract.json
    opshelm.contract.json
    christina.contract.json
    signalforge.contract.json
    content-engine.contract.json
    echoliving.contract.json
    lantern.contract.json
  examples/
    polish-learning-request.json
    opshelm-brief-request.json
    content-engine-dialogue-request.json
```

## Core Contract

All tools should call EchoChamber with the same high-level request shape:

```json
{
  "contractVersion": "1.0.0",
  "sourceTool": "opshelm",
  "requestType": "translate_and_voice",
  "sourceLanguage": "en",
  "targetLanguage": "pl",
  "sourceText": "I am thinking about you.",
  "options": {
    "includePhonetics": true,
    "includeAudio": true,
    "preserveFormatting": true
  },
  "provenance": {
    "workspaceId": "personal",
    "artifactType": "phrase",
    "sourceId": "manual-entry"
  }
}
```

## Stability Rules

- Breaking changes require a new major `contractVersion`.
- Additive fields are allowed when optional.
- Existing enum values must not be renamed.
- Tool-specific contracts may restrict the common schema but must not contradict it.
- Voice cloning or person-specific voice output must require explicit consent metadata.

## Contract Ownership

SignalForge should eventually hold cross-platform canonical versions of these schemas. EchoChamber owns the runtime behavior and reference examples.
