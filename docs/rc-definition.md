# EchoChamber RC Definition

## RC Goal

EchoChamber RC1 establishes the first stable multilingual translation and pronunciation service for Lantern.

The RC must demonstrate:

- stable contracts
- schema validation
- translation requests
- Polish pronunciation lessons
- optional ElevenLabs voice generation
- provenance-aware artifact metadata
- local-first developer execution

## Required RC Features

### API

- `/health`
- `/api/v1/translate`
- `/api/v1/lesson`
- `/api/v1/speak`

### Contracts

- request schema
- response schema
- contract registry
- tool manifests
- examples
- CI validation

### Translation

- English to Polish translation
- formatting preservation
- deterministic fallback behavior

### Pronunciation

- phonetic hints
- practice chunks
- Polish-specific character guidance

### Audio

- ElevenLabs wrapper
- disabled fallback mode
- metadata persistence

## Explicit Non-RC Scope

The RC does NOT require:

- production auth
- production Azure deployment
- full React UI
- enterprise RBAC
- advanced analytics
- large-scale storage
- custom voice cloning workflows

## RC Success Criteria

EchoChamber RC1 is successful when:

1. OpsHelm can submit a translation request.
2. A Polish lesson is returned.
3. Audio can optionally be generated.
4. Contracts validate in CI.
5. Artifacts remain traceable to provenance.
6. A new developer can clone and run locally.
