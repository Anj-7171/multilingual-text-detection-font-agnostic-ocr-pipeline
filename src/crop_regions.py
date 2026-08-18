import json
import sys
from pathlib import Path

from PIL import Image


def crop_text_regions(image_path, json_path, output_dir):
    """
    Crop detected text regions from an image using the polygon
    coordinates produced by PaddleOCR.
    """

    image = Image.open(image_path).convert("RGB")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    polygons = data["dt_polys"]
    scores = data.get("dt_scores", [])

    for i, polygon in enumerate(polygons):

        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]

        left = max(0, int(min(xs)))
        top = max(0, int(min(ys)))
        right = min(image.width, int(max(xs)))
        bottom = min(image.height, int(max(ys)))

        padding = 5

        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(image.width, right + padding)
        bottom = min(image.height, bottom + padding)

        crop = image.crop((left, top, right, bottom))

        output_path = output_dir / f"region_{i}.jpg"
        crop.save(output_path)

        if i < len(scores):
            print(
                f"Saved region {i}: {output_path} "
                f"(confidence={scores[i]:.3f})"
            )
        else:
            print(f"Saved region {i}: {output_path}")


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print(
            "Usage: python src/crop_regions.py "
            "<image> <detection_json> <output_dir>"
        )
        sys.exit(1)

    image_path = sys.argv[1]
    json_path = sys.argv[2]
    output_dir = sys.argv[3]

    crop_text_regions(
        image_path,
        json_path,
        output_dir
    )