import os


class ElevenLabsService:

    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.default_voice = os.getenv('ELEVENLABS_DEFAULT_VOICE_ID')

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def generate_audio(self, text: str, voice_id: str | None = None):
        if not self.is_enabled():
            return {
                'status': 'disabled',
                'provider': 'elevenlabs'
            }

        return {
            'status': 'stubbed',
            'provider': 'elevenlabs',
            'voiceId': voice_id or self.default_voice,
            'artifactPath': 'storage/audio/demo.mp3'
        }
