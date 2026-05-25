import os
import httpx


class DevStubTranslationProvider:
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        stubs = {
            'I am thinking about you.': 'Myślę o tobie.',
            'I am thinking about you': 'Myślę o tobie.',
            'Good morning': 'Dzień dobry',
            'I miss you': 'Tęsknię za tobą'
        }

        if target_language.lower() == 'pl':
            return stubs.get(text, '[pl translation stub] ' + text)

        return '[' + target_language + ' translation stub] ' + text


class OpenAITranslationProvider:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
        self.timeout = float(os.getenv('ECHOCHAMBER_PROVIDER_TIMEOUT_SECONDS', '30'))

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        if not self.api_key:
            return DevStubTranslationProvider().translate(text, source_language, target_language)

        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Translate the user text. Preserve intent, tone, and formatting. Return only the translated text.'
                },
                {
                    'role': 'user',
                    'content': f'Source language: {source_language}\nTarget language: {target_language}\nText:\n{text}'
                }
            ],
            'temperature': 0.2
        }

        response = httpx.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()


def get_translation_provider():
    provider = os.getenv('ECHOCHAMBER_TRANSLATION_PROVIDER', 'dev_stub').lower()

    if provider == 'openai':
        return OpenAITranslationProvider()

    return DevStubTranslationProvider()
