from fastapi import HTTPException


class VoiceConsentGuard:

    @staticmethod
    def validate(payload):
        voice = payload.voice

        if not voice:
            return

        if voice.voiceId and not voice.consentId:
            raise HTTPException(
                status_code=400,
                detail='voiceId requires consentId'
            )
