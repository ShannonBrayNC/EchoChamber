POLISH_PHONETICS = {
    'Myślę o tobie.': {
        'phoneticHint': 'MYSH-leh oh TOH-byeh',
        'practiceChunks': [
            {
                'text': 'Myślę',
                'hint': 'MYSH-leh',
                'note': 'ś sounds like a soft sh'
            },
            {
                'text': 'o tobie',
                'hint': 'oh TOH-byeh',
                'note': 'bie sounds like byeh'
            }
        ]
    },
    'Dzień dobry': {
        'phoneticHint': 'jen DOH-bri'
    }
}


class PolishPronunciationService:

    def build_lesson(self, phrase: str):
        return POLISH_PHONETICS.get(
            phrase,
            {
                'phoneticHint': 'phonetic hint unavailable',
                'practiceChunks': []
            }
        )
