import os
from pathlib import Path
import uuid
import httpx


class ElevenLabsService:

    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.default_voice = os.getenv('ELEVENLABS_DEFAULT_VOICE_ID')
        self.storage_root = Path(
            os.getenv('ECHOCHAMBER_STORAGE_ROOT', './storage')
        ) / 'audio'

        self.storage_root.mkdir(parents=True, exist_ok=True)

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def generate_audio(self, text: str, voice_id: str | None = None):
        if not self.is_enabled():
            return {
                'status': 'disabled',
                'provider': 'elevenlabs'
            }

        selected_voice = voice_id or self.default_voice

        if not selected_voice:
            return {
                'status': 'missing_voice',
                'provider': 'elevenlabs'
            }

        response = httpx.post(
            f'https://api.elevenlabs.io/v1/text-to-speech/{selected_voice}',
            headers={
                'xi-api-key': self.api_key,
                'Content-Type': 'application/json'
            },
            json={
                'text': text,
                'model_id': 'eleven_multilingual_v2'
            },
            timeout=60
        )

        response.raise_for_status()

        artifact_name = f'{uuid.uuid4()}.mp3'
        artifact_path = self.storage_root / artifact_name

        with open(artifact_path, 'wb') as handle:
            handle.write(response.content)

        return {
            'status': 'generated',
            'provider': 'elevenlabs',
            'voiceId': selected_voice,
            'artifactPath': str(artifact_path)
        }
