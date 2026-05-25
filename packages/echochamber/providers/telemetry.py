from datetime import datetime


class ProviderTelemetry:

    def build_event(
        self,
        provider: str,
        operation: str,
        status: str,
        duration_ms: float,
        metadata: dict | None = None
    ):
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider,
            'operation': operation,
            'status': status,
            'durationMs': duration_ms,
            'metadata': metadata or {}
        }
