from datetime import datetime
from packages.echochamber.translation.service import TranslationService
from packages.echochamber.phonetics.polish import PolishPronunciationService


class ConversationalTutor:
    def __init__(self):
        self.translation = TranslationService()
        self.phonetics = PolishPronunciationService()

    def respond(self, message: str, source_language: str = 'en', target_language: str = 'pl'):
        translated = self.translation.translate(
            message,
            source_language,
            target_language
        )
        lesson = self.phonetics.build_lesson(translated)

        return {
            'createdAt': datetime.utcnow().isoformat(),
            'sourceText': message,
            'translatedText': translated,
            'targetLanguage': target_language,
            'coachResponse': self._coach_response(translated, lesson),
            'phoneticHint': lesson.get('phoneticHint'),
            'practiceChunks': lesson.get('practiceChunks', [])
        }

    def _coach_response(self, translated: str, lesson: dict):
        hint = lesson.get('phoneticHint') or 'practice slowly, one phrase at a time'
        return f'Say: {translated}. Practice it slowly as: {hint}.'
