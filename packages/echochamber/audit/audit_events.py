from datetime import datetime


class AuditEventFactory:

    @staticmethod
    def build(event_type: str, workspace_id: str, payload: dict):
        return {
            'eventType': event_type,
            'workspaceId': workspace_id,
            'timestamp': datetime.utcnow().isoformat(),
            'payload': payload
        }
