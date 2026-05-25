class EchoLivingAdapter:
    """Adapter boundary for EchoLiving integration.

    Future responsibilities:
    - multilingual guest messaging
    - hospitality phrasebooks
    - check-in instructions
    - emergency communication templates
    """

    def build_guest_message_request(self, workspace_id: str, text: str):
        return {
            'contractVersion': '1.0.0',
            'sourceTool': 'echoliving',
            'requestType': 'translate_and_voice',
            'sourceLanguage': 'en',
            'targetLanguage': 'pl',
            'sourceText': text,
            'options': {
                'includeAudio': True
            },
            'provenance': {
                'workspaceId': workspace_id,
                'artifactType': 'guest-message',
                'sourceId': 'echoliving-adapter'
            }
        }
