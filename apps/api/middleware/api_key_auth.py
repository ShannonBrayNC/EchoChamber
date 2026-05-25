import os
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        configured = os.getenv('ECHOCHAMBER_API_KEY')

        if not configured:
            return await call_next(request)

        provided = request.headers.get('x-api-key')

        if provided != configured:
            raise HTTPException(
                status_code=401,
                detail='Invalid API key'
            )

        return await call_next(request)
