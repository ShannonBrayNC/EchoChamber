from datetime import datetime
from fastapi import APIRouter
from packages.echochamber.contracts.models import EchoChamberRequest
from packages.echochamber.translation.service import TranslationService
from packages.echochamber.phonetics.polish import PolishPronunciationService

router = APIRouter()

translation_service = TranslationService()
phonetics_service = PolishPronunciationService()


@router.post('/lesson')
def lesson(payload: EchoChamberRequest):
    translated = translation_service.translate(
        payload.sourceText,
        payload.sourceLanguage,
        payload.targetLanguage
    )

    lesson_data = phonetics_service.build_lesson(translated)

    return {
        'contractVersion': payload.contractVersion,
        'status': 'success',
        'translatedText': translated,
        'targetLanguage': payload.targetLanguage,
        'phoneticHint': lesson_data.get('phoneticHint'),
        'practiceChunks': lesson_data.get('practiceChunks', []),
        'artifact': {
            'artifactId': 'lesson-artifact',
            'workspaceId': payload.provenance.workspaceId,
            'createdAt': datetime.utcnow().isoformat()
        }
    }
