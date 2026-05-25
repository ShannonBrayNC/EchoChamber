import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_phrasebook_exists():
    phrasebook = ROOT / 'examples' / 'polish' / 'vanessa_phrasebook.json'

    assert phrasebook.exists()


def test_phrasebook_has_entries():
    phrasebook = ROOT / 'examples' / 'polish' / 'vanessa_phrasebook.json'

    with open(phrasebook, 'r', encoding='utf-8') as handle:
        data = json.load(handle)

    assert len(data) >= 5
