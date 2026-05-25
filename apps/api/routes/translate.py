from datetime import datetime
from fastapi import APIRouter
from packages.echochamber.contracts.models import EchoChamberRequest
from packages.echochamber.translation.service import TranslationService

router = APIRouter()

translation_service = TranslationService()


@router.post('/translate')
def translate(payload: EchoChamberRequest):
    translated = translation_service.translate(
        payload.sourceText,
        payload.sourceLanguage,
        payload.targetLanguage
    )

    return {
        'contractVersion': payload.contractVersion,
        'status': 'success',
        'translatedText': translated,
        'targetLanguage': payload.targetLanguage,
        'artifact': {
            'artifactId': 'demo-artifact',
            'workspaceId': payload.provenance.workspaceId,
            'createdAt': datetime.utcnow().isoformat()
        }
    }
