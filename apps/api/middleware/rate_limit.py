from collections import defaultdict
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else 'unknown'
        now = time.time()

        self.requests[client] = [
            ts for ts in self.requests[client]
            if now - ts < 60
        ]

        if len(self.requests[client]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail='Rate limit exceeded'
            )

        self.requests[client].append(now)

        return await call_next(request)
