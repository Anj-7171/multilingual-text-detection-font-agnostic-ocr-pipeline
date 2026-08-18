import json
import sys
from pathlib import Path

from PIL import Image
from paddleocr import TextDetection, TextRecognition

from script_identifier import identify_script


DETECTION_MODEL = "PP-OCRv4_mobile_det"
RECOGNITION_MODEL = "PP-OCRv4_mobile_rec"


def crop_from_polygon(image, polygon, padding=5):
    """Create an axis-aligned crop from a detected text polygon."""

    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]

    left = max(0, int(min(xs)) - padding)
    top = max(0, int(min(ys)) - padding)
    right = min(image.width, int(max(xs)) + padding)
    bottom = min(image.height, int(max(ys)) + padding)

    return image.crop((left, top, right, bottom))


def run_pipeline(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    results_dir = Path("data/results")
    crops_dir = results_dir / "crops"

    results_dir.mkdir(parents=True, exist_ok=True)
    crops_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Load models
    # ---------------------------------------------------------
    print(f"Loading detector: {DETECTION_MODEL}")
    detector = TextDetection(model_name=DETECTION_MODEL)

    print(f"Loading recognizer: {RECOGNITION_MODEL}")
    recognizer = TextRecognition(model_name=RECOGNITION_MODEL)

    # ---------------------------------------------------------
    # 2. Detect text regions
    # ---------------------------------------------------------
    print(f"\nRunning detection on {image_path.name}...")

    detection_result = detector.predict(str(image_path))
    page = detection_result[0]

    polygons = page["dt_polys"]
    detection_scores = page.get("dt_scores", [])

    print(f"Detected {len(polygons)} text regions.")

    # ---------------------------------------------------------
    # 3. Load original image
    # ---------------------------------------------------------
    image = Image.open(image_path).convert("RGB")

    pipeline_results = []

    # ---------------------------------------------------------
    # 4. Crop + recognize each detected region
    # ---------------------------------------------------------
    for i, polygon in enumerate(polygons):

        # Convert NumPy polygon to normal Python list
        polygon_list = polygon.tolist()

        # Crop the detected region
        crop = crop_from_polygon(image, polygon_list)

        crop_path = crops_dir / f"{image_path.stem}_region_{i}.jpg"
        crop.save(crop_path)

        # -----------------------------------------------------
        # Recognition
        # -----------------------------------------------------
        recognition_result = recognizer.predict(str(crop_path))
        recognition_page = recognition_result[0]

        # PaddleOCR 3.x TextRecognition output
        text = recognition_page["rec_text"]
        recognition_confidence = float(
            recognition_page["rec_score"]
        )

        # -----------------------------------------------------
        # Script identification
        # -----------------------------------------------------
        script = identify_script(text)

        # -----------------------------------------------------
        # Detection confidence
        # -----------------------------------------------------
        detection_confidence = (
            float(detection_scores[i])
            if i < len(detection_scores)
            else 0.0
        )

        # -----------------------------------------------------
        # Store result
        # -----------------------------------------------------
        result = {
            "region_id": i,
            "text": text,
            "script": script,
            "detection_confidence": detection_confidence,
            "recognition_confidence": recognition_confidence,
            "polygon": polygon_list,
            "crop_path": str(crop_path),
        }

        pipeline_results.append(result)

        # -----------------------------------------------------
        # Display result
        # -----------------------------------------------------
        print(f"\nRegion {i}")
        print(f"  Text                  : {text}")
        print(f"  Script                : {script}")
        print(
            f"  Detection confidence  : "
            f"{detection_confidence:.3f}"
        )
        print(
            f"  Recognition confidence: "
            f"{recognition_confidence:.3f}"
        )

    # ---------------------------------------------------------
    # 5. Save structured pipeline output
    # ---------------------------------------------------------
    output_path = results_dir / f"{image_path.stem}_ocr.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            pipeline_results,
            f,
            ensure_ascii=False,
            indent=4,
        )

    print(f"\nSaved pipeline results to: {output_path}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(
            "Usage: python src/ocr_pipeline.py <image>"
        )
        sys.exit(1)

    run_pipeline(sys.argv[1])