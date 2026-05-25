import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / 'contracts'


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def validate_registry():
    registry = load_json(CONTRACTS / 'registry.json')
    assert 'contracts' in registry
    assert len(registry['contracts']) > 0


def validate_examples():
    examples = CONTRACTS / 'examples'
    if not examples.exists():
        return

    for file in examples.glob('*.json'):
        data = load_json(file)
        assert 'contractVersion' in data
        assert 'sourceTool' in data
        assert 'requestType' in data


def validate_tool_manifests():
    manifests = CONTRACTS / 'tools'

    for file in manifests.glob('*.json'):
        data = load_json(file)
        assert 'tool' in data
        assert 'allowedRequestTypes' in data


if __name__ == '__main__':
    validate_registry()
    validate_examples()
    validate_tool_manifests()
    print('EchoChamber contract validation passed.')
