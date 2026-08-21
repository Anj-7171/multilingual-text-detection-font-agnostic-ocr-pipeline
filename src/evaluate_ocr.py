from pathlib import Path
import csv
import json
import re

from paddleocr import TextRecognition


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "dataset"
    / "metadata.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "results"
    / "ocr_evaluation.csv"
)


# ---------------------------------------------------------
# Script-specific OCR models
# ---------------------------------------------------------
#
# Each script is evaluated using the recognition model
# intended for that script.
#
# English  -> English OCR model
# Hindi    -> Devanagari OCR model
# Tamil    -> Tamil OCR model
# ---------------------------------------------------------

MODEL_CONFIG = {

    "english": "en_PP-OCRv5_mobile_rec",

    "hindi": "devanagari_PP-OCRv5_mobile_rec",

    "tamil": "ta_PP-OCRv5_mobile_rec",
}


# ---------------------------------------------------------
# Text normalization
# ---------------------------------------------------------

def normalize_text(text):
    """
    Normalize OCR output and ground truth
    before comparison.
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
        return (
            0.0
            if len(hypothesis) == 0
            else 1.0
        )

    previous = list(
        range(len(hypothesis) + 1)
    )

    for i, ref_char in enumerate(
        reference,
        start=1
    ):

        current = [i]

        for j, hyp_char in enumerate(
            hypothesis,
            start=1
        ):

            insertion = (
                current[j - 1] + 1
            )

            deletion = (
                previous[j] + 1
            )

            substitution = (
                previous[j - 1]
                + (ref_char != hyp_char)
            )

            current.append(
                min(
                    insertion,
                    deletion,
                    substitution
                )
            )

        previous = current

    return min(
    previous[-1] / len(reference),
    1.0
)


# ---------------------------------------------------------
# Word Error Rate
# ---------------------------------------------------------

def word_error_rate(reference, hypothesis):
    """
    Calculate Word Error Rate (WER).
    """

    reference_words = (
        normalize_text(reference).split()
    )

    hypothesis_words = (
        normalize_text(hypothesis).split()
    )

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

            insertion = (
                current[j - 1] + 1
            )

            deletion = (
                previous[j] + 1
            )

            substitution = (
                previous[j - 1]
                + (ref_word != hyp_word)
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

    data = dict(result)

    text = data.get(
        "rec_text",
        ""
    )

    score = data.get(
        "rec_score",
        0.0
    )

    return text, float(score)


# ---------------------------------------------------------
# Create OCR recognizers
# ---------------------------------------------------------

def create_recognizers():
    """
    Create one recognition model for each
    supported script.
    """

    recognizers = {}

    print("\nLoading script-specific OCR models...")

    for script, model_name in MODEL_CONFIG.items():

        print(
            f"  {script.capitalize():<10} -> "
            f"{model_name}"
        )

        recognizers[script] = TextRecognition(
            model_name=model_name
        )

    return recognizers


# ---------------------------------------------------------
# Run OCR on one image
# ---------------------------------------------------------

def recognize_image(
    recognizer,
    image_path
):
    """
    Run recognition on a single image.
    """

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
    print("SCRIPT-AWARE OCR EVALUATION")
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
    # Create OCR recognizers
    # -----------------------------------------------------

    recognizers = create_recognizers()

    # -----------------------------------------------------
    # Evaluate samples
    # -----------------------------------------------------

    results = []

    for index, item in enumerate(
        metadata,
        start=1
    ):

        image_path = (
            PROJECT_ROOT
            / item["image"]
        )

        ground_truth = item["text"]

        script = item["script"]

        print(
            f"\n[{index}/{len(metadata)}] "
            f"{item['image']}"
        )

        # -------------------------------------------------
        # Validate script
        # -------------------------------------------------

        if script not in recognizers:

            print(
                f"  ERROR: Unsupported script: "
                f"{script}"
            )

            results.append(
                {
                    "id": item["id"],
                    "script": script,
                    "font": item["font"],
                    "image": item["image"],
                    "ground_truth": ground_truth,
                    "prediction": "",
                    "recognition_confidence": 0.0,
                    "cer": 1.0,
                    "wer": 1.0,
                }
            )

            continue

        recognizer = recognizers[script]

        model_name = MODEL_CONFIG[script]

        print(
            f"  Script       : {script}"
        )

        print(
            f"  OCR model    : {model_name}"
        )

        try:

            prediction, confidence = (
                recognize_image(
                    recognizer,
                    image_path
                )
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
                f"  Confidence   : "
                f"{confidence:.3f}"
            )

            print(
                f"  CER          : "
                f"{cer:.3f}"
            )

            print(
                f"  WER          : "
                f"{wer:.3f}"
            )

            results.append(
                {
                    "id": item["id"],
                    "script": script,
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
                    "script": script,
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
    # Overall summary
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
        r
        for r in results
        if r["prediction"]
    ]

    if successful:

        average_cer = (
            sum(
                r["cer"]
                for r in successful
            )
            / len(successful)
        )

        average_wer = (
            sum(
                r["wer"]
                for r in successful
            )
            / len(successful)
        )

        average_confidence = (
            sum(
                r["recognition_confidence"]
                for r in successful
            )
            / len(successful)
        )

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

    # -----------------------------------------------------
    # Per-script summary
    # -----------------------------------------------------

    print("\n" + "-" * 70)
    print("PER-SCRIPT SUMMARY")
    print("-" * 70)

    for script in MODEL_CONFIG:

        script_results = [
            r
            for r in results
            if r["script"] == script
            and r["prediction"]
        ]

        if not script_results:

            print(
                f"\n{script.capitalize()}: "
                f"No successful predictions"
            )

            continue

        script_cer = (
            sum(
                r["cer"]
                for r in script_results
            )
            / len(script_results)
        )

        script_wer = (
            sum(
                r["wer"]
                for r in script_results
            )
            / len(script_results)
        )

        script_confidence = (
            sum(
                r["recognition_confidence"]
                for r in script_results
            )
            / len(script_results)
        )

        print(
            f"\n{script.capitalize()}:"
        )

        print(
            f"  Samples evaluated : "
            f"{len(script_results)}"
        )

        print(
            f"  Average CER       : "
            f"{script_cer:.3f}"
        )

        print(
            f"  Average WER       : "
            f"{script_wer:.3f}"
        )

        print(
            f"  Average confidence: "
            f"{script_confidence:.3f}"
        )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate()