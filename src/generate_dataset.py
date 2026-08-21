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
# 20 unique samples per language.
#
# The dataset is balanced at the LANGUAGE level:
# English = 20 images
# Hindi   = 20 images
# Tamil   = 20 images
#
# Because the number of fonts differs by language,
# samples are distributed across available fonts.
# ---------------------------------------------------------

TEXT_DATA = {

    "english": [
        "Hello World OCR Test",
        "Multilingual Text Detection",
        "Font Agnostic OCR Pipeline",
        "Detection Sample Line Two",
        "Optical Character Recognition",
        "Testing Text Recognition Accuracy",
        "Computer Vision Pipeline",
        "Language Detection Experiment",
        "Robust OCR Across Fonts",
        "Synthetic Dataset Generation",
        "Machine Learning Text Analysis",
        "Image Based Text Recognition",
        "Cross Language OCR Evaluation",
        "Character Recognition Benchmark",
        "Deep Learning Vision System",
        "Text Processing With OCR",
        "Font Robustness Evaluation",
        "Multilingual Vision Pipeline",
        "Automated Text Detection",
        "OCR Performance Analysis",
    ],

    "hindi": [
        "नमस्ते दुनिया",
        "बहुभाषी पाठ पहचान",
        "फॉन्ट एग्नोस्टिक ओसीआर पाइपलाइन",
        "यह एक परीक्षण है",
        "ऑप्टिकल कैरेक्टर रिकग्निशन",
        "पाठ पहचान सटीकता परीक्षण",
        "कंप्यूटर विज़न पाइपलाइन",
        "भाषा पहचान प्रयोग",
        "विभिन्न फॉन्ट पर ओसीआर",
        "सिंथेटिक डेटासेट निर्माण",
        "मशीन लर्निंग पाठ विश्लेषण",
        "चित्र आधारित पाठ पहचान",
        "बहुभाषी ओसीआर मूल्यांकन",
        "अक्षर पहचान परीक्षण",
        "डीप लर्निंग विज़न सिस्टम",
        "ओसीआर के साथ पाठ प्रसंस्करण",
        "फॉन्ट मजबूती मूल्यांकन",
        "बहुभाषी विज़न पाइपलाइन",
        "स्वचालित पाठ पहचान",
        "ओसीआर प्रदर्शन विश्लेषण",
    ],

    "tamil": [
        "வணக்கம் உலகம்",
        "பலமொழி உரை கண்டறிதல்",
        "எழுத்துரு சார்பற்ற OCR குழாய்",
        "இது ஒரு சோதனை",
        "ஒளியியல் எழுத்து அங்கீகாரம்",
        "உரை அங்கீகார துல்லியம் சோதனை",
        "கணினி பார்வை குழாய்",
        "மொழி கண்டறிதல் பரிசோதனை",
        "வெவ்வேறு எழுத்துருக்களில் OCR",
        "செயற்கை தரவுத்தொகுப்பு உருவாக்கம்",
        "இயந்திர கற்றல் உரை பகுப்பாய்வு",
        "பட அடிப்படையிலான உரை அங்கீகாரம்",
        "பலமொழி OCR மதிப்பீடு",
        "எழுத்து அங்கீகார சோதனை",
        "ஆழமான கற்றல் பார்வை அமைப்பு",
        "OCR மூலம் உரை செயலாக்கம்",
        "எழுத்துரு வலிமை மதிப்பீடு",
        "பலமொழி பார்வை குழாய்",
        "தானியங்கி உரை கண்டறிதல்",
        "OCR செயல்திறன் பகுப்பாய்வு",
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
# Dataset configuration
# ---------------------------------------------------------

TARGET_SAMPLES_PER_LANGUAGE = 20


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

        print(
            f"  Available fonts: {len(fonts)}"
        )

        print(
            f"  Target images: "
            f"{TARGET_SAMPLES_PER_LANGUAGE}"
        )

        script_output_dir = OUTPUT_DIR / script

        script_output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # Distribute the target number of samples across
        # the available fonts.
        #
        # Example:
        #
        # English: 20 samples / 5 fonts = 4 each
        # Hindi:   20 samples / 4 fonts = 5 each
        # Tamil:   20 samples / 1 font  = 20
        # -------------------------------------------------

        base_samples = (
            TARGET_SAMPLES_PER_LANGUAGE
            // len(fonts)
        )

        extra_samples = (
            TARGET_SAMPLES_PER_LANGUAGE
            % len(fonts)
        )

        text_index = 0

        for font_index, font_path in enumerate(fonts):

            font_name = font_path.stem

            font_output_dir = (
                script_output_dir / font_name
            )

            font_output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            # Some fonts receive one additional sample
            # if the target cannot be divided equally.
            samples_for_font = (
                base_samples
                + (
                    1
                    if font_index < extra_samples
                    else 0
                )
            )

            print(
                f"  Font: {font_path.name} "
                f"({samples_for_font} images)"
            )

            for sample_index in range(
                samples_for_font
            ):

                # Select a unique text sample.
                text = texts[text_index]

                filename = (
                    f"{script}_{font_name}_"
                    f"{sample_index:02d}.png"
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
                text_index += 1

    # ---------------------------------------------------------
    # Save metadata
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Dataset summary
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)

    print(
        f"\nTotal images generated: "
        f"{len(metadata)}"
    )

    # Count samples by language
    language_counts = {}

    for item in metadata:

        script = item["script"]

        language_counts[script] = (
            language_counts.get(script, 0) + 1
        )

    print("\nImages by language:")

    for script, count in language_counts.items():

        print(
            f"  {script.capitalize():<10}: "
            f"{count}"
        )

    print(
        f"\nMetadata saved to:"
    )

    print(
        metadata_path
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    generate_dataset()