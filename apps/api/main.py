from fastapi import FastAPI
from apps.api.routes.translate import router as translate_router
from apps.api.routes.lesson import router as lesson_router
from apps.api.routes.speak import router as speak_router
from apps.api.routes.artifacts import router as artifact_router
from apps.api.routes.discovery import router as discovery_router
from apps.api.routes.study import router as study_router
from apps.api.middleware.tracing import RequestTracingMiddleware
from apps.api.middleware.api_key_auth import ApiKeyAuthMiddleware
from apps.api.middleware.rate_limit import SimpleRateLimitMiddleware

app = FastAPI(
    title='EchoChamber',
    version='0.1.0-rc1'
)

app.add_middleware(RequestTracingMiddleware)
app.add_middleware(ApiKeyAuthMiddleware)
app.add_middleware(SimpleRateLimitMiddleware)

app.include_router(translate_router, prefix='/api/v1')
app.include_router(lesson_router, prefix='/api/v1')
app.include_router(speak_router, prefix='/api/v1')
app.include_router(artifact_router, prefix='/api/v1')
app.include_router(discovery_router, prefix='/api/v1')
app.include_router(study_router, prefix='/api/v1')


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'echochamber',
        'version': '0.1.0-rc1',
        'capabilities': [
            'translation',
            'phonetics',
            'artifact-storage',
            'voice-generation',
            'workspace-isolation',
            'adaptive-learning',
            'study-sessions'
        ]
    }
