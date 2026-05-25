POLISH_CHARACTER_WEIGHTS = {
    'ą': 2,
    'ę': 2,
    'ł': 2,
    'ś': 2,
    'ż': 2,
    'ź': 2,
    'cz': 1,
    'sz': 1,
    'rz': 1
}


class PhraseDifficultyScorer:

    def score(self, phrase: str) -> dict:
        score = 1

        for pattern, weight in POLISH_CHARACTER_WEIGHTS.items():
            if pattern in phrase:
                score += weight

        score += max(0, len(phrase.split()) - 2)

        if score <= 2:
            level = 'beginner'
        elif score <= 5:
            level = 'intermediate'
        else:
            level = 'advanced'

        return {
            'score': score,
            'level': level
        }
