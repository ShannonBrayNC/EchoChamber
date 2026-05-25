# EchoChamber

EchoChamber is the Lantern language bridge: a translation, pronunciation, and voice-learning tool that helps people communicate across language barriers while preserving tone, intent, and voice.

The first driving use case is personal and practical: help Shannon learn Polish for Vanessa by taking English text, translating it into Polish, generating audio through ElevenLabs, and breaking the output into pronunciation-friendly learning blocks.

## New Mission

EchoChamber converts meaning across languages and delivery modes:

1. **Text in**: user provides text, syntax, message drafts, repo content, scripts, or tool output.
2. **Translation**: EchoChamber translates the source content into a target language.
3. **Pronunciation coaching**: it returns phonetic guidance, syllable breakdowns, letter/character notes, and practice prompts.
4. **Voice generation**: it sends the translated text to ElevenLabs and saves playable audio.
5. **Cross-repo integration**: Lantern, ETS, Christina, OpsHelm, SignalForge, EchoLiving, and Content Engine can call EchoChamber for translation and voice output.

## Why It Exists

Lantern is meant to operate across people, systems, markets, and stories. Language should not be the wall. EchoChamber becomes the voice-room where a thought can enter in one language and leave as:

- a translated message,
- a pronunciation lesson,
- a saved audio clip,
- a reusable API response,
- or a downstream artifact for another repo.

## Core Capabilities

### MVP

- Translate text to Polish first, then expand to any supported language.
- Generate ElevenLabs text-to-speech audio from translated text.
- Save generated audio locally or to future object storage.
- Produce pronunciation guidance for learners.
- Return structured JSON for other Lantern tools.
- Expose a FastAPI service and CLI entry point.

### Phase 2

- Voice clone support with explicit consent controls.
- Phrasebook and spaced-repetition practice mode.
- Repo/document translation pipelines.
- Web UI for translation, playback, practice, and export.
- Webhook support for automation workflows.
- Azure deployment with Key Vault-backed secrets.

### Phase 3

- Conversational tutor mode.
- Speech-to-text pronunciation scoring.
- Multi-speaker dialogue generation.
- Content Engine audiobook/dialogue support.
- OpsHelm customer-facing multilingual briefs.
- Christina multilingual business assistant responses.

## Architecture

```text
apps/
  api/                 FastAPI service
  web/                 Future React/Tailwind UI
packages/
  echochamber/         Core translation, phonetics, TTS orchestration
  contracts/           JSON schemas and integration contracts
docs/
  requirements.md      Product and technical requirements
  architecture.md      System architecture
  integrations.md      Lantern/repo integration model
  polish-pronunciation.md
scripts/
  demo_translate.py    Local CLI/demo entry point
tests/
  unit/                Unit tests
```

## API Shape

```http
POST /api/v1/translate
POST /api/v1/speak
POST /api/v1/lesson
POST /api/v1/repo/translate
GET  /api/v1/languages
GET  /health
```

## Example Request

```json
{
  "source_text": "I am thinking about you.",
  "source_language": "en",
  "target_language": "pl",
  "voice_id": "default-polish-or-custom-voice",
  "include_audio": true,
  "include_phonetics": true
}
```

## Example Response

```json
{
  "source_text": "I am thinking about you.",
  "translated_text": "Myślę o tobie.",
  "target_language": "pl",
  "phonetic_hint": "MYSH-leh oh TOH-byeh",
  "practice_chunks": [
    {
      "text": "Myślę",
      "hint": "MYSH-leh",
      "note": "ś is a soft sh sound; ę at the end often sounds close to eh"
    },
    {
      "text": "o tobie",
      "hint": "oh TOH-byeh",
      "note": "bie sounds like byeh"
    }
  ],
  "audio": {
    "provider": "elevenlabs",
    "status": "generated",
    "path": "storage/audio/2026/05/example.mp3"
  }
}
```

## Environment Variables

Create `.env` from `.env.example`.

```bash
ELEVENLABS_API_KEY=
ELEVENLABS_DEFAULT_VOICE_ID=
TRANSLATION_PROVIDER=openai
OPENAI_API_KEY=
ECHOCHAMBER_STORAGE_ROOT=./storage
```

## Local Development

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
uvicorn apps.api.main:app --reload
```

Demo:

```bash
python scripts/demo_translate.py "I am thinking about you" --target pl --audio
```

## Design Rules

- Do not clone or synthesize a private person’s voice without explicit consent.
- Do not leak repo content across workspaces or customers.
- Store secrets only in environment variables or Key Vault.
- Treat translated repo content as an artifact with provenance.
- Keep translation, phonetics, and audio metadata together.
- Every generated audio file should include source text, translated text, provider, model, voice, and timestamp metadata.

## Lantern Role

EchoChamber is not replacing ETS, Christina, Lantern, or OpsHelm. It is the multilingual voice layer they can all call.

- **ETS**: translate evidence, summaries, trust records, and civic/security artifacts.
- **Christina**: speak to businesses and customers in their preferred language.
- **OpsHelm**: translate customer briefs, meeting prep, and ticket summaries.
- **SignalForge**: store cross-platform translation contracts and shared schemas.
- **Content Engine**: generate multilingual scripts, dialogue, and audiobook-ready narration.
- **EchoLiving**: communicate with guests and property partners globally.

## Status

Repo repurpose is underway. Current focus: MVP translation + Polish pronunciation + ElevenLabs audio generation.
