class ProviderFallbackChain:
    def __init__(self, providers: list):
        self.providers = providers

    def translate(self, text: str, source_language: str, target_language: str):
        last_error = None

        for provider in self.providers:
            try:
                return provider.translate(
                    text,
                    source_language,
                    target_language
                )
            except Exception as error:
                last_error = error

        if last_error:
            raise last_error

        raise RuntimeError('No translation providers available')
