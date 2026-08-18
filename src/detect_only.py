"""
Phase 1, Step 1: Standalone text detection (no recognition).

Verifies PaddleOCR's PP-OCRv4 mobile detector runs on CPU and produces
sane bounding boxes on a single test image. Recognition is intentionally
disabled at this stage — we only want to prove detection works in isolation
before layering script-ID routing and recognition on top of it (Phase 2).

Usage:
    python src/detect_only.py data/test_images/sample1.jpg
"""

import sys
from pathlib import Path

from paddleocr import TextDetection


def run_detection(image_path: str, output_dir: str = "data/results"):
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not image_path.exists():
        raise FileNotFoundError(f"Test image not found: {image_path}")

    print(f"Loading PP-OCRv4 mobile detector (CPU)...")
    # model_name is explicit (not left to default) so we always know exactly
    # which detector is running, regardless of what paddleocr's internal
    # default happens to be in future versions.
    detector = TextDetection(model_name="PP-OCRv4_mobile_det")

    print(f"Running detection on {image_path.name}...")
    results = detector.predict(str(image_path))

    # predict() returns a list — one result per input image. We passed one
    # image, so we expect exactly one result back.
    result = results[0]

    boxes = result["dt_polys"]
    scores = result["dt_scores"]

    print(f"\nDetected {len(boxes)} text regions:")
    for i, (box, score) in enumerate(zip(boxes, scores)):
        print(f"  [{i}] confidence={score:.3f}  box={box.tolist() if hasattr(box, 'tolist') else box}")

    # Save annotated image (boxes drawn on original) and raw JSON output.
    img_out = output_dir / f"{image_path.stem}_boxes.jpg"
    json_out = output_dir / f"{image_path.stem}_boxes.json"

    result.save_to_img(str(output_dir))
    result.save_to_json(str(output_dir))

    print(f"\nSaved annotated image to: {img_out}")
    print(f"Saved raw JSON to:        {json_out}")

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/detect_only.py <path_to_image>")
        sys.exit(1)

    run_detection(sys.argv[1])