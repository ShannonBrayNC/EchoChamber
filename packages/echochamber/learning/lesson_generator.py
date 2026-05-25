from packages.echochamber.learning.difficulty import PhraseDifficultyScorer


class AdaptiveLessonGenerator:

    def __init__(self):
        self.scorer = PhraseDifficultyScorer()

    def generate(self, phrases: list[dict], learner_level: str = 'beginner'):
        selected = []

        for phrase in phrases:
            difficulty = self.scorer.score(phrase['polish'])

            if learner_level == difficulty['level']:
                selected.append({
                    'phrase': phrase,
                    'difficulty': difficulty
                })

        return selected[:10]
