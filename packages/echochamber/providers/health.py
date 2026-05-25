import os


def get_provider_health():
    return {
        'translation': {
            'dev_stub': {
                'status': 'available',
                'default': os.getenv('ECHOCHAMBER_TRANSLATION_PROVIDER', 'dev_stub') == 'dev_stub'
            },
            'openai': {
                'status': 'configured' if os.getenv('OPENAI_API_KEY') else 'not_configured',
                'default': os.getenv('ECHOCHAMBER_TRANSLATION_PROVIDER') == 'openai'
            }
        },
        'voice': {
            'elevenlabs': {
                'status': 'configured' if os.getenv('ELEVENLABS_API_KEY') else 'not_configured',
                'defaultVoiceConfigured': bool(os.getenv('ELEVENLABS_DEFAULT_VOICE_ID'))
            }
        }
    }
