import argparse
from packages.echochamber.translation.service import TranslationService
from packages.echochamber.phonetics.polish import PolishPronunciationService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    parser.add_argument('--target', default='pl')
    parser.add_argument('--phonetics', action='store_true')

    args = parser.parse_args()

    translation_service = TranslationService()
    phonetics_service = PolishPronunciationService()

    translated = translation_service.translate(
        args.text,
        'en',
        args.target
    )

    print('\nTranslated:')
    print(translated)

    if args.phonetics:
        lesson = phonetics_service.build_lesson(translated)

        print('\nPhonetic Hint:')
        print(lesson.get('phoneticHint'))

        print('\nPractice Chunks:')
        for chunk in lesson.get('practiceChunks', []):
            print(f"- {chunk['text']} => {chunk['hint']}")


if __name__ == '__main__':
    main()
