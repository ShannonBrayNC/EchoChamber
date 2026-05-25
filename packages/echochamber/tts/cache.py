from pathlib import Path
import hashlib
import os


class VoiceCache:
    def __init__(self):
        root = os.getenv('ECHOCHAMBER_STORAGE_ROOT', './storage')
        self.cache_root = Path(root) / 'voice-cache'
        self.cache_root.mkdir(parents=True, exist_ok=True)

    def cache_key(self, text: str, voice_id: str):
        return hashlib.sha256(
            f'{voice_id}:{text}'.encode('utf-8')
        ).hexdigest()

    def get(self, text: str, voice_id: str):
        key = self.cache_key(text, voice_id)
        target = self.cache_root / f'{key}.mp3'

        if target.exists():
            return str(target)

        return None

    def store(self, text: str, voice_id: str, source_path: str):
        key = self.cache_key(text, voice_id)
        target = self.cache_root / f'{key}.mp3'

        with open(source_path, 'rb') as src:
            with open(target, 'wb') as dst:
                dst.write(src.read())

        return str(target)
