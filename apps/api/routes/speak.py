from fastapi import APIRouter
from packages.echochamber.contracts.models import EchoChamberRequest
from packages.echochamber.tts.elevenlabs_service import ElevenLabsService

router = APIRouter()

service = ElevenLabsService()


@router.post('/speak')
def speak(payload: EchoChamberRequest):
    result = service.generate_audio(
        payload.sourceText,
        payload.voice.voiceId if payload.voice else None
    )

    return result
