class ETSAdapter:
    """Adapter boundary for ETS integration.

    Future responsibilities:
    - multilingual evidence verification
    - immutable translation references
    - governance-safe localization
    - civic/research translation workflows
    """

    def build_evidence_translation_request(self, workspace_id: str, text: str):
        return {
            'contractVersion': '1.0.0',
            'sourceTool': 'ets',
            'requestType': 'repo_artifact_translation',
            'sourceLanguage': 'en',
            'targetLanguage': 'pl',
            'sourceText': text,
            'provenance': {
                'workspaceId': workspace_id,
                'artifactType': 'evidence-record',
                'sourceId': 'ets-adapter'
            }
        }
