class PronunciationScorer:

    def score(self, expected: str, spoken: str):
        expected_clean = expected.lower().strip()
        spoken_clean = spoken.lower().strip()

        if expected_clean == spoken_clean:
            score = 100
        elif expected_clean in spoken_clean:
            score = 85
        else:
            overlap = len(set(expected_clean.split()) & set(spoken_clean.split()))
            score = min(80, overlap * 20)

        if score >= 90:
            feedback = 'Excellent pronunciation.'
        elif score >= 70:
            feedback = 'Very good. Slow down slightly on difficult sounds.'
        else:
            feedback = 'Practice the phrase more slowly and focus on syllables.'

        return {
            'score': score,
            'feedback': feedback
        }
