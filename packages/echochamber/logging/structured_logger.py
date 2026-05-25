import json
from datetime import datetime


class StructuredLogger:

    @staticmethod
    def log(event_type: str, payload: dict):
        message = {
            'timestamp': datetime.utcnow().isoformat(),
            'eventType': event_type,
            'payload': payload
        }

        print(json.dumps(message, ensure_ascii=False))
