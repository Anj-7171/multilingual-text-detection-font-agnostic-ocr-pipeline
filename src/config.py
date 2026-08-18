"""
Global configuration for the OCR pipeline.
"""

from pathlib import Path

# Project folders
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
TEST_IMAGES_DIR = DATA_DIR / "test_images"
RESULTS_DIR = DATA_DIR / "results"

# Detection model
DETECTION_MODEL = "PP-OCRv4_mobile_det"

# Recognition languages
EASYOCR_LANGUAGES = ["en"]

# Confidence threshold
DETECTION_THRESHOLD = 0.4