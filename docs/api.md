# EchoChamber API Reference

## Health

### GET `/health`

Returns runtime status and capabilities.

---

## Translation

### POST `/api/v1/translate`

Translate text between supported languages.

### Example

```json
{
  "contractVersion": "1.0.0",
  "sourceTool": "manual",
  "requestType": "translate",
  "sourceLanguage": "en",
  "targetLanguage": "pl",
  "sourceText": "I am thinking about you.",
  "provenance": {
    "workspaceId": "demo",
    "artifactType": "phrase",
    "sourceId": "sample"
  }
}
```

---

## Pronunciation Lesson

### POST `/api/v1/lesson`

Returns pronunciation guidance and practice chunks.

---

## Speech

### POST `/api/v1/speak`

Generates speech when ElevenLabs is configured.

---

## Artifacts

### GET `/api/v1/artifacts/{artifact_id}`

Retrieves a workspace-scoped artifact.

Requires:

- `workspaceId` query parameter

---

## Contracts

### GET `/api/v1/contracts`

Returns the active contract registry.

---

## Languages

### GET `/api/v1/languages`

Returns supported languages.

---

## Providers

### GET `/api/v1/providers`

Returns configured provider categories.

---

## Phrasebook

### GET `/api/v1/phrasebook`

Returns the seeded Polish learning phrasebook.
