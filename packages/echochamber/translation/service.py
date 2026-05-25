from typing import Dict


POLISH_STUBS: Dict[str, str] = {
    'I am thinking about you.': 'Myślę o tobie.',
    'Good morning': 'Dzień dobry',
    'I miss you': 'Tęsknię za tobą'
}


class TranslationService:

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        if target_language.lower() == 'pl':
            return POLISH_STUBS.get(text, f'[pl translation stub] {text}')

        return f'[{target_language} translation stub] {text}'
