from fastapi import FastAPI
from apps.api.routes.translate import router as translate_router
from apps.api.routes.lesson import router as lesson_router
from apps.api.routes.speak import router as speak_router
from apps.api.routes.artifacts import router as artifact_router

app = FastAPI(
    title='EchoChamber',
    version='0.1.0-rc1'
)

app.include_router(translate_router, prefix='/api/v1')
app.include_router(lesson_router, prefix='/api/v1')
app.include_router(speak_router, prefix='/api/v1')
app.include_router(artifact_router, prefix='/api/v1')


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'echochamber',
        'version': '0.1.0-rc1'
    }
