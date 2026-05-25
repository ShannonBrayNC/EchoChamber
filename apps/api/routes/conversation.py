from fastapi import APIRouter
from packages.echochamber.conversation.tutor import ConversationalTutor
from packages.echochamber.conversation.memory import ConversationMemory
from packages.echochamber.conversation.pronunciation import PronunciationScorer

router = APIRouter()

tutor = ConversationalTutor()
memory = ConversationMemory()
scorer = PronunciationScorer()


@router.post('/conversation/respond')
def respond(payload: dict):
    learner_id = payload.get('learnerId', 'anonymous')
    message = payload.get('message', '')

    memory.append(learner_id, 'user', message)

    response = tutor.respond(message)

    memory.append(
        learner_id,
        'assistant',
        response['translatedText']
    )

    response['history'] = memory.history(learner_id)

    return response


@router.post('/conversation/pronunciation-score')
def pronunciation_score(payload: dict):
    expected = payload.get('expected', '')
    spoken = payload.get('spoken', '')

    return scorer.score(expected, spoken)
