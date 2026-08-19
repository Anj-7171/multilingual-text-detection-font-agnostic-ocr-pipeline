from pathlib import Path
import csv
import json
import re

from paddleocr import TextRecognition


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

METADATA_PATH = PROJECT_ROOT / "data" / "dataset" / "metadata.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "results" / "ocr_evaluation.csv"


# ---------------------------------------------------------
# OCR configuration
# ---------------------------------------------------------

MODEL_NAME = "PP-OCRv5_mobile_rec"


# ---------------------------------------------------------
# Text normalization
# ---------------------------------------------------------

def normalize_text(text):
    """
    Normalize OCR output and ground truth before comparison.
    """

    if text is None:
        return ""

    text = str(text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# Character Error Rate
# ---------------------------------------------------------

def character_error_rate(reference, hypothesis):
    """
    Calculate Character Error Rate (CER).

    CER = edit_distance / number_of_reference_characters
    """

    reference = normalize_text(reference)
    hypothesis = normalize_text(hypothesis)

    if len(reference) == 0:
        return 0.0 if len(hypothesis) == 0 else 1.0

    previous = list(range(len(hypothesis) + 1))

    for i, ref_char in enumerate(reference, start=1):

        current = [i]

        for j, hyp_char in enumerate(hypothesis, start=1):

            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            substitution = previous[j - 1] + (
                ref_char != hyp_char
            )

            current.append(
                min(
                    insertion,
                    deletion,
                    substitution
                )
            )

        previous = current

    return previous[-1] / len(reference)


# ---------------------------------------------------------
# Word Error Rate
# ---------------------------------------------------------

def word_error_rate(reference, hypothesis):
    """
    Calculate Word Error Rate (WER).
    """

    reference_words = normalize_text(reference).split()
    hypothesis_words = normalize_text(hypothesis).split()

    if len(reference_words) == 0:
        return (
            0.0
            if len(hypothesis_words) == 0
            else 1.0
        )

    previous = list(
        range(len(hypothesis_words) + 1)
    )

    for i, ref_word in enumerate(
        reference_words,
        start=1
    ):

        current = [i]

        for j, hyp_word in enumerate(
            hypothesis_words,
            start=1
        ):

            insertion = current[j - 1] + 1
            deletion = previous[j] + 1

            substitution = previous[j - 1] + (
                ref_word != hyp_word
            )

            current.append(
                min(
                    insertion,
                    deletion,
                    substitution
                )
            )

        previous = current

    return previous[-1] / len(reference_words)


# ---------------------------------------------------------
# Extract recognition result
# ---------------------------------------------------------

def extract_text(result):

    """
    Extract recognized text and confidence
    from PaddleOCR TextRecognition result.
    """

    # PaddleOCR result behaves like a dictionary.
    data = dict(result)

    text = data.get("rec_text", "")
    score = data.get("rec_score", 0.0)

    return text, float(score)


# ---------------------------------------------------------
# Run OCR on one image
# ---------------------------------------------------------

def recognize_image(recognizer, image_path):

    results = recognizer.predict(
        str(image_path)
    )

    if not results:
        return "", 0.0

    result = results[0]

    return extract_text(result)


# ---------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------

def evaluate():

    print("=" * 70)
    print("OCR FONT ROBUSTNESS EVALUATION")
    print("=" * 70)

    # -----------------------------------------------------
    # Load metadata
    # -----------------------------------------------------

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        metadata = json.load(f)

    print(
        f"\nLoaded {len(metadata)} dataset samples."
    )

    # -----------------------------------------------------
    # Create OCR recognizer
    # -----------------------------------------------------

    print(
        f"\nLoading OCR recognition model: "
        f"{MODEL_NAME}"
    )

    recognizer = TextRecognition(
        model_name=MODEL_NAME
    )

    # -----------------------------------------------------
    # Evaluate samples
    # -----------------------------------------------------

    results = []

    for index, item in enumerate(
        metadata,
        start=1
    ):

        image_path = (
            PROJECT_ROOT / item["image"]
        )

        ground_truth = item["text"]

        print(
            f"\n[{index}/{len(metadata)}] "
            f"{item['image']}"
        )

        try:

            prediction, confidence = recognize_image(
                recognizer,
                image_path
            )

            cer = character_error_rate(
                ground_truth,
                prediction
            )

            wer = word_error_rate(
                ground_truth,
                prediction
            )

            print(
                f"  Ground truth : {ground_truth}"
            )

            print(
                f"  OCR output   : {prediction}"
            )

            print(
                f"  Confidence   : {confidence:.3f}"
            )

            print(
                f"  CER          : {cer:.3f}"
            )

            print(
                f"  WER          : {wer:.3f}"
            )

            results.append(
                {
                    "id": item["id"],
                    "script": item["script"],
                    "font": item["font"],
                    "image": item["image"],
                    "ground_truth": ground_truth,
                    "prediction": prediction,
                    "recognition_confidence": confidence,
                    "cer": cer,
                    "wer": wer,
                }
            )

        except Exception as e:

            print(
                f"  ERROR: {e}"
            )

            results.append(
                {
                    "id": item["id"],
                    "script": item["script"],
                    "font": item["font"],
                    "image": item["image"],
                    "ground_truth": ground_truth,
                    "prediction": "",
                    "recognition_confidence": 0.0,
                    "cer": 1.0,
                    "wer": 1.0,
                }
            )

    # -----------------------------------------------------
    # Save CSV
    # -----------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "id",
        "script",
        "font",
        "image",
        "ground_truth",
        "prediction",
        "recognition_confidence",
        "cer",
        "wer",
    ]

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"\nResults saved to:"
    )

    print(
        OUTPUT_PATH
    )

    successful = [
        r for r in results
        if r["prediction"]
    ]

    if successful:

        average_cer = sum(
            r["cer"]
            for r in successful
        ) / len(successful)

        average_wer = sum(
            r["wer"]
            for r in successful
        ) / len(successful)

        average_confidence = sum(
            r["recognition_confidence"]
            for r in successful
        ) / len(successful)

        print(
            f"\nAverage CER        : "
            f"{average_cer:.3f}"
        )

        print(
            f"Average WER        : "
            f"{average_wer:.3f}"
        )

        print(
            f"Average confidence: "
            f"{average_confidence:.3f}"
        )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate()