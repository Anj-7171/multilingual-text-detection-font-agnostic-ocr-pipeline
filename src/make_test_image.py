"""
Generates a simple synthetic test image with text, for smoke-testing the
detector before we have real-world sample images collected.

This is deliberately minimal — the real multi-font benchmark dataset
(Phase 3) will extend this same idea with 8-10 actual font files,
rotation/skew, and multilingual (Hindi/Tamil) text.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def make_sample_image(out_path: str = "data/test_images/sample1.jpg"):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (600, 300), color="white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=28)

    draw.text((30, 40), "Hello World OCR Test", fill="black", font=font)
    draw.text((30, 100), "Detection Sample Line Two", fill="black", font=font)
    draw.text((30, 160), "Rotated-ish Style Text", fill="black", font=font)

    # Slight rotation to mimic a not-perfectly-flat real photo
    img = img.rotate(-2, expand=True, fillcolor="white")
    img.save(out_path)
    print(f"Saved test image to {out_path} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    make_sample_image()