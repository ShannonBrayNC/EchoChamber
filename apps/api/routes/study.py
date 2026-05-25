from fastapi import APIRouter, HTTPException
from packages.echochamber.learning.session_store import StudySessionStore
from packages.echochamber.learning.spaced_repetition import SpacedRepetitionEngine

router = APIRouter()

store = StudySessionStore()
repetition = SpacedRepetitionEngine()


@router.post('/study/session')
def create_session(payload: dict):
    learner_id = payload.get('learnerId', 'anonymous')
    language = payload.get('language', 'pl')
    phrases = payload.get('phrases', [])

    return store.create_session(
        learner_id=learner_id,
        language=language,
        phrases=phrases
    )


@router.get('/study/session/{session_id}')
def get_session(session_id: str):
    session = store.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    return session


@router.post('/study/session/{session_id}/progress')
def update_progress(session_id: str, payload: dict):
    phrase_index = payload.get('phraseIndex', 0)
    success = payload.get('success', False)

    session = store.update_progress(
        session_id=session_id,
        phrase_index=phrase_index,
        success=success
    )

    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    phrase = session['phrases'][phrase_index]

    return {
        'session': session,
        'nextReviewAt': repetition.next_review(
            phrase.get('successfulAttempts', 0)
        )
    }
