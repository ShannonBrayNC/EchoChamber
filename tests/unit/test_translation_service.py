from packages.echochamber.translation.service import TranslationService


def test_polish_translation_stub():
    service = TranslationService()

    result = service.translate(
        'I am thinking about you.',
        'en',
        'pl'
    )

    assert result == 'Myślę o tobie.'
