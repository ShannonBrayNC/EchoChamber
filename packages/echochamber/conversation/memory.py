from collections import defaultdict
from datetime import datetime


class ConversationMemory:
    def __init__(self):
        self.sessions = defaultdict(list)

    def append(self, learner_id: str, role: str, content: str):
        self.sessions[learner_id].append({
            'timestamp': datetime.utcnow().isoformat(),
            'role': role,
            'content': content
        })

    def history(self, learner_id: str, limit: int = 10):
        return self.sessions[learner_id][-limit:]
