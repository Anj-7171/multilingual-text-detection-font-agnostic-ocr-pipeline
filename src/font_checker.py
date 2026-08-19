from pathlib import Path
from fontTools.ttLib import TTFont


FONT_DIR = Path(r"C:\Windows\Fonts")

TEST_TEXT = {
    "english": "Hello World OCR Test",
    "hindi": "नमस्ते दुनिया OCR परीक्षण",
    "tamil": "வணக்கம் உலகம் OCR சோதனை",
}


FONT_CANDIDATES = [
    "arial.ttf",
    "times.ttf",
    "calibri.ttf",
    "comic.ttf",
    "impact.ttf",
    "mangal.ttf",
    "kokila.ttf",
    "aparaj.ttf",
    "utsaah.ttf",
    "segoeui.ttf",
    "tahoma.ttf",
    "gautami.ttf",
    "latha.ttf",
    "tunga.ttf",
    "kartika.ttf",
]


def get_supported_characters(font_path):
    """Return the Unicode code points supported by a font."""

    font = TTFont(str(font_path), fontNumber=0)

    cmap = font.getBestCmap()

    if cmap is None:
        return set()

    return set(cmap.keys())


def check_font(font_path, text):
    """Check whether every character in text exists in the font."""

    supported_chars = get_supported_characters(font_path)

    missing = []

    for char in text:
        if char.isspace():
            continue

        if ord(char) not in supported_chars:
            missing.append(char)

    return missing


def main():

    print("=" * 70)
    print("FONT UNICODE COVERAGE CHECK")
    print("=" * 70)

    results = {
        script: []
        for script in TEST_TEXT
    }

    for font_name in FONT_CANDIDATES:

        font_path = FONT_DIR / font_name

        if not font_path.exists():
            continue

        print(f"\n{font_name}")

        try:
            for script, text in TEST_TEXT.items():

                missing = check_font(font_path, text)

                if not missing:
                    status = "YES"
                    results[script].append(font_name)
                else:
                    status = "NO"

                print(f"  {script:<10}: {status}")

                if missing:
                    unique_missing = "".join(
                        dict.fromkeys(missing)
                    )

                    print(
                        f"    Missing characters: "
                        f"{unique_missing}"
                    )

        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 70)
    print("COMPATIBLE FONTS")
    print("=" * 70)

    for script, fonts in results.items():

        print(f"\n{script.upper()}")

        if fonts:
            for font in fonts:
                print(f"  - {font}")
        else:
            print("  No fully compatible fonts found.")


if __name__ == "__main__":
    main()