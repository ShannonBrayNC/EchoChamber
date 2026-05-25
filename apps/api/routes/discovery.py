from pathlib import Path
import json
from fastapi import APIRouter
from packages.echochamber.providers.health import get_provider_health

router = APIRouter()

ROOT = Path(__file__).resolve().parents[3]


@router.get('/contracts')
def contracts():
    registry = ROOT / 'contracts' / 'registry.json'

    with open(registry, 'r', encoding='utf-8') as handle:
        return json.load(handle)


@router.get('/languages')
def languages():
    return {
        'supported': [
            {
                'code': 'en',
                'name': 'English'
            },
            {
                'code': 'pl',
                'name': 'Polish'
            }
        ]
    }


@router.get('/providers')
def providers():
    return {
        'translationProviders': [
            'dev_stub',
            'openai'
        ],
        'voiceProviders': [
            'elevenlabs'
        ]
    }


@router.get('/provider-health')
def provider_health():
    return get_provider_health()


@router.get('/phrasebook')
def phrasebook():
    phrasebook_path = ROOT / 'examples' / 'polish' / 'vanessa_phrasebook.json'

    with open(phrasebook_path, 'r', encoding='utf-8') as handle:
        return json.load(handle)
