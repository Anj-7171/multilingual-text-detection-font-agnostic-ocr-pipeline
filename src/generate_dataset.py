from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FONT_DIR = PROJECT_ROOT / "fonts"
OUTPUT_DIR = PROJECT_ROOT / "data" / "dataset"


# ---------------------------------------------------------
# Ground-truth text
# ---------------------------------------------------------

TEXT_DATA = {
    "english": [
        "Hello World OCR Test",
        "Multilingual Text Detection",
        "Font Agnostic OCR Pipeline",
        "Detection Sample Line Two",
    ],

    "hindi": [
        "नमस्ते दुनिया",
        "बहुभाषी पाठ पहचान",
        "फॉन्ट एग्नोस्टिक ओसीआर पाइपलाइन",
        "यह एक परीक्षण है",
    ],

    "tamil": [
        "வணக்கம் உலகம்",
        "பலமொழி உரை கண்டறிதல்",
        "எழுத்துரு சார்பற்ற OCR குழாய்",
        "இது ஒரு சோதனை",
    ],
}


# ---------------------------------------------------------
# Image configuration
# ---------------------------------------------------------

IMAGE_WIDTH = 1400
IMAGE_HEIGHT = 180

FONT_SIZE = 60

BACKGROUND_COLOR = "white"
TEXT_COLOR = "black"


# ---------------------------------------------------------
# Generate one image
# ---------------------------------------------------------

def generate_image(text, font_path, output_path):

    font = ImageFont.truetype(
        str(font_path),
        FONT_SIZE
    )

    image = Image.new(
        "RGB",
        (IMAGE_WIDTH, IMAGE_HEIGHT),
        BACKGROUND_COLOR
    )

    draw = ImageDraw.Draw(image)

    # Calculate text bounding box
    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text
    x = (IMAGE_WIDTH - text_width) // 2
    y = (IMAGE_HEIGHT - text_height) // 2 - bbox[1]

    draw.text(
        (x, y),
        text,
        font=font,
        fill=TEXT_COLOR
    )

    image.save(output_path)


# ---------------------------------------------------------
# Find fonts
# ---------------------------------------------------------

def get_fonts(script):

    font_dir = FONT_DIR / script

    if not font_dir.exists():
        return []

    extensions = {
        ".ttf",
        ".otf",
        ".TTF",
        ".OTF",
    }

    return sorted(
        [
            path
            for path in font_dir.iterdir()
            if path.suffix in extensions
        ]
    )


# ---------------------------------------------------------
# Generate dataset
# ---------------------------------------------------------

def generate_dataset():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata = []

    image_id = 0

    for script, texts in TEXT_DATA.items():

        fonts = get_fonts(script)

        if not fonts:
            print(
                f"\nWARNING: No fonts found for "
                f"{script}."
            )
            continue

        print(
            f"\nGenerating {script} dataset..."
        )

        script_output_dir = OUTPUT_DIR / script

        script_output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        for font_path in fonts:

            font_name = font_path.stem

            font_output_dir = (
                script_output_dir / font_name
            )

            font_output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            print(
                f"  Font: {font_path.name}"
            )

            for text_index, text in enumerate(texts):

                filename = (
                    f"{script}_{font_name}_"
                    f"{text_index:02d}.png"
                )

                output_path = (
                    font_output_dir / filename
                )

                generate_image(
                    text,
                    font_path,
                    output_path
                )

                metadata.append(
                    {
                        "id": image_id,
                        "image": str(
                            output_path.relative_to(
                                PROJECT_ROOT
                            )
                        ),
                        "script": script,
                        "font": font_name,
                        "font_file": str(
                            font_path.relative_to(
                                PROJECT_ROOT
                            )
                        ),
                        "text": text,
                    }
                )

                image_id += 1

    # -----------------------------------------------------
    # Save metadata
    # -----------------------------------------------------

    metadata_path = (
        OUTPUT_DIR / "metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)

    print(
        f"\nImages generated: {len(metadata)}"
    )

    print(
        f"Metadata saved to: {metadata_path}"
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    generate_dataset()