from packages.echochamber.translation.providers import get_translation_provider
from packages.echochamber.providers.retry import ProviderRetryPolicy
from packages.echochamber.providers.timeout import timeout


class TranslationService:

    def __init__(self):
        self.provider = get_translation_provider()
        self.retry_policy = ProviderRetryPolicy()

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        def operation():
            with timeout(30):
                return self.provider.translate(
                    text,
                    source_language,
                    target_language
                )

        return self.retry_policy.run(operation)
