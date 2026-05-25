from packages.echochamber.phonetics.polish import PolishPronunciationService


def test_polish_phonetics():
    service = PolishPronunciationService()

    result = service.build_lesson('Myślę o tobie.')

    assert result['phoneticHint'] == 'MYSH-leh oh TOH-byeh'
    assert len(result['practiceChunks']) > 0
