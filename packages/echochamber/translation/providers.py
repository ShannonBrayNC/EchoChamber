import os


class DevStubTranslationProvider:
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        stubs = {
            'I am thinking about you.': 'Myślę o tobie.',
            'I am thinking about you': 'Myślę o tobie.',
            'Good morning': 'Dzień dobry'
        }

        if target_language.lower() == 'pl':
            return stubs.get(text, '[pl translation stub] ' + text)

        return '[' + target_language + ' translation stub] ' + text


class OpenAITranslationProvider:
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        if not os.getenv('OPENAI_API_KEY'):
            return DevStubTranslationProvider().translate(text, source_language, target_language)

        return DevStubTranslationProvider().translate(text, source_language, target_language)


def get_translation_provider():
    provider = os.getenv('ECHOCHAMBER_TRANSLATION_PROVIDER', 'dev_stub').lower()

    if provider == 'openai':
        return OpenAITranslationProvider()

    return DevStubTranslationProvider()
