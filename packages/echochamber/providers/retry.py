import time
from typing import Callable, TypeVar

T = TypeVar('T')


class ProviderRetryPolicy:
    def __init__(self, attempts: int = 3, backoff_seconds: float = 0.5):
        self.attempts = attempts
        self.backoff_seconds = backoff_seconds

    def run(self, operation: Callable[[], T]) -> T:
        last_error: Exception | None = None

        for attempt in range(1, self.attempts + 1):
            try:
                return operation()
            except Exception as error:
                last_error = error

                if attempt < self.attempts:
                    time.sleep(self.backoff_seconds * attempt)

        assert last_error is not None
        raise last_error
