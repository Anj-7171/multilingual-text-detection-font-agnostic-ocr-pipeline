from pathlib import Path
import csv
from collections import defaultdict


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "results"
    / "ocr_evaluation.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "results"
    / "analysis"
)


# ---------------------------------------------------------
# Load CSV
# ---------------------------------------------------------

def load_results():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Results file not found:\n{INPUT_PATH}"
        )

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        results = []

        for row in reader:

            results.append(
                {
                    "id": int(row["id"]),
                    "script": row["script"],
                    "font": row["font"],
                    "image": row["image"],
                    "ground_truth": row["ground_truth"],
                    "prediction": row["prediction"],
                    "recognition_confidence": float(
                        row["recognition_confidence"]
                    ),
                    "cer": float(row["cer"]),
                    "wer": float(row["wer"]),
                }
            )

    return results


# ---------------------------------------------------------
# Calculate averages
# ---------------------------------------------------------

def calculate_summary(rows):

    if not rows:
        return {
            "samples": 0,
            "cer": 0.0,
            "wer": 0.0,
            "confidence": 0.0,
        }

    return {
        "samples": len(rows),

        "cer": sum(
            row["cer"]
            for row in rows
        ) / len(rows),

        "wer": sum(
            row["wer"]
            for row in rows
        ) / len(rows),

        "confidence": sum(
            row["recognition_confidence"]
            for row in rows
        ) / len(rows),
    }


# ---------------------------------------------------------
# Group results
# ---------------------------------------------------------

def group_by_script(results):

    groups = defaultdict(list)

    for row in results:
        groups[row["script"]].append(row)

    return groups


def group_by_font(results):

    groups = defaultdict(list)

    for row in results:

        key = (
            row["script"],
            row["font"]
        )

        groups[key].append(row)

    return groups


# ---------------------------------------------------------
# Print overall summary
# ---------------------------------------------------------

def print_overall_summary(results):

    summary = calculate_summary(results)

    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)

    print(
        f"\nSamples evaluated : {summary['samples']}"
    )

    print(
        f"Average CER       : {summary['cer']:.3f}"
    )

    print(
        f"Average WER       : {summary['wer']:.3f}"
    )

    print(
        f"Average confidence: "
        f"{summary['confidence']:.3f}"
    )


# ---------------------------------------------------------
# Print per-script summary
# ---------------------------------------------------------

def print_script_summary(results):

    groups = group_by_script(results)

    print("\n" + "-" * 70)
    print("PER-SCRIPT SUMMARY")
    print("-" * 70)

    print(
        f"\n{'Script':<12}"
        f"{'Samples':<10}"
        f"{'CER':<12}"
        f"{'WER':<12}"
        f"{'Confidence':<12}"
    )

    print("-" * 58)

    summaries = []

    for script in sorted(groups):

        summary = calculate_summary(
            groups[script]
        )

        summaries.append(
            {
                "script": script,
                **summary,
            }
        )

        print(
            f"{script:<12}"
            f"{summary['samples']:<10}"
            f"{summary['cer']:<12.3f}"
            f"{summary['wer']:<12.3f}"
            f"{summary['confidence']:<12.3f}"
        )

    return summaries


# ---------------------------------------------------------
# Print per-font summary
# ---------------------------------------------------------

def print_font_summary(results):

    groups = group_by_font(results)

    print("\n" + "-" * 70)
    print("PER-FONT SUMMARY")
    print("-" * 70)

    print(
        f"\n{'Script':<12}"
        f"{'Font':<15}"
        f"{'Samples':<10}"
        f"{'CER':<12}"
        f"{'WER':<12}"
        f"{'Confidence':<12}"
    )

    print("-" * 71)

    summaries = []

    for (script, font) in sorted(groups):

        summary = calculate_summary(
            groups[(script, font)]
        )

        summaries.append(
            {
                "script": script,
                "font": font,
                **summary,
            }
        )

        print(
            f"{script:<12}"
            f"{font:<15}"
            f"{summary['samples']:<10}"
            f"{summary['cer']:<12.3f}"
            f"{summary['wer']:<12.3f}"
            f"{summary['confidence']:<12.3f}"
        )

    return summaries


# ---------------------------------------------------------
# Find best and worst fonts
# ---------------------------------------------------------

def print_font_extremes(font_summaries):

    if not font_summaries:
        return

    best = min(
        font_summaries,
        key=lambda x: x["cer"]
    )

    worst = max(
        font_summaries,
        key=lambda x: x["cer"]
    )

    print("\n" + "-" * 70)
    print("FONT ROBUSTNESS EXTREMES")
    print("-" * 70)

    print("\nBest performing font:")
    print(
        f"  Script     : {best['script']}"
    )
    print(
        f"  Font       : {best['font']}"
    )
    print(
        f"  CER        : {best['cer']:.3f}"
    )
    print(
        f"  WER        : {best['wer']:.3f}"
    )
    print(
        f"  Confidence : {best['confidence']:.3f}"
    )

    print("\nWorst performing font:")
    print(
        f"  Script     : {worst['script']}"
    )
    print(
        f"  Font       : {worst['font']}"
    )
    print(
        f"  CER        : {worst['cer']:.3f}"
    )
    print(
        f"  WER        : {worst['wer']:.3f}"
    )
    print(
        f"  Confidence : {worst['confidence']:.3f}"
    )


# ---------------------------------------------------------
# Save script summary
# ---------------------------------------------------------

def save_script_summary(summaries):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR
        / "per_script_summary.csv"
    )

    fieldnames = [
        "script",
        "samples",
        "cer",
        "wer",
        "confidence",
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in summaries:

            writer.writerow(
                {
                    "script": row["script"],
                    "samples": row["samples"],
                    "cer": f"{row['cer']:.6f}",
                    "wer": f"{row['wer']:.6f}",
                    "confidence": (
                        f"{row['confidence']:.6f}"
                    ),
                }
            )

    return output_path


# ---------------------------------------------------------
# Save font summary
# ---------------------------------------------------------

def save_font_summary(summaries):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR
        / "per_font_summary.csv"
    )

    fieldnames = [
        "script",
        "font",
        "samples",
        "cer",
        "wer",
        "confidence",
    ]

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in summaries:

            writer.writerow(
                {
                    "script": row["script"],
                    "font": row["font"],
                    "samples": row["samples"],
                    "cer": f"{row['cer']:.6f}",
                    "wer": f"{row['wer']:.6f}",
                    "confidence": (
                        f"{row['confidence']:.6f}"
                    ),
                }
            )

    return output_path


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def analyze():

    print("=" * 70)
    print("OCR RESULT ANALYSIS")
    print("=" * 70)

    print(
        f"\nLoading results from:\n{INPUT_PATH}"
    )

    results = load_results()

    print(
        f"\nLoaded {len(results)} evaluation results."
    )

    # Overall
    print_overall_summary(results)

    # Per script
    script_summaries = print_script_summary(
        results
    )

    # Per font
    font_summaries = print_font_summary(
        results
    )

    # Best / worst
    print_font_extremes(
        font_summaries
    )

    # Save summaries
    script_output = save_script_summary(
        script_summaries
    )

    font_output = save_font_summary(
        font_summaries
    )

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print(
        f"\nScript summary saved to:\n"
        f"{script_output}"
    )

    print(
        f"\nFont summary saved to:\n"
        f"{font_output}"
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    analyze()