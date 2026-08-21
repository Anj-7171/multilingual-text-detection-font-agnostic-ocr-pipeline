from pathlib import Path
import csv

import matplotlib.pyplot as plt


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "results"
    / "analysis"
    / "per_script_summary.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "results"
    / "analysis"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "cer_by_script.png"
)


# ---------------------------------------------------------
# Load script summary
# ---------------------------------------------------------

def load_results():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Summary file not found:\n{INPUT_PATH}"
        )

    scripts = []
    cer_values = []

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            scripts.append(
                row["script"].capitalize()
            )

            cer_values.append(
                float(row["cer"])
            )

    return scripts, cer_values


# ---------------------------------------------------------
# Create chart
# ---------------------------------------------------------

def create_chart():

    print("=" * 70)
    print("GENERATING OCR RESULTS VISUALIZATION")
    print("=" * 70)

    scripts, cer_values = load_results()

    print("\nResults:")

    for script, cer in zip(
        scripts,
        cer_values
    ):
        print(
            f"  {script:<10} CER = {cer:.3f}"
        )

    # Create output directory
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Plot
    # -----------------------------------------------------

    plt.figure(figsize=(8, 5))

    bars = plt.bar(
        scripts,
        cer_values
    )

    plt.title(
        "Script-Aware OCR Performance"
    )

    plt.xlabel(
        "Script"
    )

    plt.ylabel(
        "Character Error Rate (CER)"
    )

    plt.ylim(
        0,
        1.1
    )

    plt.grid(
        axis="y",
        alpha=0.3
    )

    # Add values above bars
    for bar, value in zip(
        bars,
        cer_values
    ):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,

            value + 0.03,

            f"{value:.3f}",

            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"\nChart saved to:\n{OUTPUT_PATH}"
    )

    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETE")
    print("=" * 70)


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    create_chart()