from pathlib import Path
from datetime import datetime
import hashlib
import json
import os
import uuid


class ArtifactService:

    def __init__(self):
        root = os.getenv('ECHOCHAMBER_STORAGE_ROOT', './storage')
        self.root = Path(root)
        self.artifacts = self.root / 'artifacts'
        self.audio = self.root / 'audio'

        self.artifacts.mkdir(parents=True, exist_ok=True)
        self.audio.mkdir(parents=True, exist_ok=True)

    def save_translation_artifact(
        self,
        workspace_id: str,
        source_tool: str,
        source_text: str,
        translated_text: str,
        provider: str = 'dev_stub',
        voice_id: str | None = None
    ):
        artifact_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        source_hash = hashlib.sha256(
            source_text.encode('utf-8')
        ).hexdigest()

        payload = {
            'artifactId': artifact_id,
            'workspaceId': workspace_id,
            'sourceTool': source_tool,
            'sourceTextHash': source_hash,
            'translatedText': translated_text,
            'provider': provider,
            'voiceId': voice_id,
            'createdAt': created_at
        }

        output = self.artifacts / f'{artifact_id}.json'

        with open(output, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2)

        return payload

    def get_artifact(self, artifact_id: str, workspace_id: str):
        target = self.artifacts / f'{artifact_id}.json'

        if not target.exists():
            return None

        with open(target, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)

        if payload.get('workspaceId') != workspace_id:
            raise PermissionError('workspace mismatch')

        return payload
