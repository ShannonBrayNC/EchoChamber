from pathlib import Path
from datetime import datetime
import json
import os
import uuid


class StudySessionStore:
    def __init__(self):
        root = os.getenv('ECHOCHAMBER_STORAGE_ROOT', './storage')
        self.sessions_root = Path(root) / 'sessions'
        self.sessions_root.mkdir(parents=True, exist_ok=True)

    def create_session(self, learner_id: str, language: str, phrases: list[dict] | None = None):
        session_id = str(uuid.uuid4())
        payload = {
            'sessionId': session_id,
            'learnerId': learner_id,
            'language': language,
            'createdAt': datetime.utcnow().isoformat(),
            'phrases': phrases or []
        }

        self._write(payload)
        return payload

    def get_session(self, session_id: str):
        path = self.sessions_root / f'{session_id}.json'

        if not path.exists():
            return None

        with open(path, 'r', encoding='utf-8') as handle:
            return json.load(handle)

    def update_progress(self, session_id: str, phrase_index: int, success: bool):
        session = self.get_session(session_id)

        if not session:
            return None

        phrase = session['phrases'][phrase_index]
        phrase['attempts'] = phrase.get('attempts', 0) + 1
        phrase['successfulAttempts'] = phrase.get('successfulAttempts', 0) + (1 if success else 0)
        phrase['lastPracticed'] = datetime.utcnow().isoformat()

        self._write(session)
        return session

    def _write(self, payload: dict):
        path = self.sessions_root / f"{payload['sessionId']}.json"

        with open(path, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
