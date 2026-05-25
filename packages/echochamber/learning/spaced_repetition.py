from datetime import datetime, timedelta


class SpacedRepetitionEngine:

    def next_review(self, successful_attempts: int):
        now = datetime.utcnow()

        if successful_attempts <= 0:
            delta = timedelta(hours=4)
        elif successful_attempts == 1:
            delta = timedelta(days=1)
        elif successful_attempts == 2:
            delta = timedelta(days=3)
        elif successful_attempts == 3:
            delta = timedelta(days=7)
        else:
            delta = timedelta(days=14)

        return (now + delta).isoformat()
