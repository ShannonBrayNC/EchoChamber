import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get('x-correlation-id') or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        response.headers['x-correlation-id'] = correlation_id
        response.headers['x-echochamber-duration-ms'] = str(duration_ms)

        return response
