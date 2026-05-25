class OpsHelmAdapter:
    """Adapter boundary for OpsHelm integration.

    Future responsibilities:
    - ticket translation
    - multilingual customer summaries
    - evidence-safe operational translation
    - meeting prep localization
    """

    def build_translation_request(self, workspace_id: str, text: str):
        return {
            'contractVersion': '1.0.0',
            'sourceTool': 'opshelm',
            'requestType': 'translate',
            'sourceLanguage': 'en',
            'targetLanguage': 'pl',
            'sourceText': text,
            'provenance': {
                'workspaceId': workspace_id,
                'artifactType': 'ticket-summary',
                'sourceId': 'opshelm-adapter'
            }
        }
