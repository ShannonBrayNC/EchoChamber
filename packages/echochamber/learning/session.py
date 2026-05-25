from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class PhraseProgress:
    english: str
    translated: str
    attempts: int = 0
    successfulAttempts: int = 0
    lastPracticed: str | None = None


@dataclass
class StudySession:
    sessionId: str
    learnerId: str
    language: str
    createdAt: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    phrases: List[PhraseProgress] = field(default_factory=list)
